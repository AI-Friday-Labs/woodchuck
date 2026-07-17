#!/usr/bin/env python3
"""Run and report a reproducible multi-model OpenRouter benchmark.

Uses only the Python standard library. The API key is read from .env and is
never written to result artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import signal
import shutil
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
OPENROUTER_API = "https://openrouter.ai/api/v1"


class RequestDeadlineError(TimeoutError):
    """Raised when a request exceeds the configured wall-clock deadline."""


class wall_clock_deadline:
    def __init__(self, seconds: int):
        self.seconds = seconds
        self.previous_handler: Any = None

    def __enter__(self) -> None:
        self.previous_handler = signal.getsignal(signal.SIGALRM)

        def raise_deadline(_signum: int, _frame: Any) -> None:
            raise RequestDeadlineError(
                f"Request exceeded the {self.seconds}s wall-clock deadline"
            )

        signal.signal(signal.SIGALRM, raise_deadline)
        signal.setitimer(signal.ITIMER_REAL, self.seconds)

    def __exit__(self, _exc_type: Any, _exc: Any, _traceback: Any) -> None:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, self.previous_handler)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def json_dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp.replace(path)


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key, value)


def safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "__", value).strip("_")


def as_float(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def as_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def first_present(mapping: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if mapping.get(key) is not None:
            return mapping[key]
    return None


def extract_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if not isinstance(value, list):
        return ""
    parts: list[str] = []
    for item in value:
        if isinstance(item, str):
            parts.append(item)
        elif isinstance(item, dict):
            text = first_present(item, "text", "content", "summary")
            if isinstance(text, str):
                parts.append(text)
    return "".join(parts)


def api_headers(api_key: str, accept: str = "application/json") -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": accept,
        "X-Title": "Chuck Model Benchmark",
    }


def get_json(url: str, api_key: str, timeout: int = 60) -> dict[str, Any]:
    request = urllib.request.Request(url, headers=api_headers(api_key), method="GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_catalog(api_key: str) -> list[dict[str, Any]]:
    return get_json(f"{OPENROUTER_API}/models", api_key)["data"]


def fetch_generation(
    api_key: str,
    generation_id: str,
    retry_delays: tuple[float, ...] = (0.0, 1.0, 2.0, 4.0, 8.0),
) -> dict[str, Any] | None:
    url = f"{OPENROUTER_API}/generation?{urllib.parse.urlencode({'id': generation_id})}"
    for delay in retry_delays:
        if delay:
            time.sleep(delay)
        try:
            payload = get_json(url, api_key, timeout=30)
            data = payload.get("data")
            if isinstance(data, dict):
                return data
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
            continue
    return None


def build_jobs(config: dict[str, Any]) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    for model in config["models"]:
        configured_runs = model.get("runs")
        if configured_runs is None:
            configured_runs = [
                {"reasoning_effort": effort}
                for effort in model["reasoning_efforts"]
            ]
        for configured_run in configured_runs:
            effort = configured_run.get("reasoning_effort")
            reasoning = configured_run.get("reasoning")
            label = configured_run.get("label") or effort or "default"
            job = {
                "model": model["id"],
                "family": model["family"],
                "reasoning_effort": effort,
                "reasoning_effort_label": label,
            }
            if reasoning is not None:
                job["reasoning"] = reasoning
            if configured_run.get("max_tokens") is not None:
                job["max_tokens"] = int(configured_run["max_tokens"])
            jobs.append(job)
    random.Random(config["shuffle_seed"]).shuffle(jobs)
    for sequence, job in enumerate(jobs, start=1):
        effort_label = job["reasoning_effort_label"]
        job["sequence"] = sequence
        job["run_id"] = f"{sequence:03d}__{safe_slug(job['model'])}__{safe_slug(effort_label)}"
    return jobs


def validate_matrix(config: dict[str, Any], catalog: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    by_id = {model["id"]: model for model in catalog}
    errors: list[str] = []
    warnings: list[str] = []
    for configured in config["models"]:
        model_id = configured["id"]
        live = by_id.get(model_id)
        if not live:
            errors.append(f"Model is not present in the live catalog: {model_id}")
            continue
        declared = ((live.get("reasoning") or {}).get("supported_efforts"))
        if configured.get("runs") is not None:
            requested = [
                run.get("reasoning_effort") or (run.get("reasoning") or {}).get("effort")
                for run in configured["runs"]
            ]
            requested = [item for item in requested if item is not None]
        else:
            requested = [item for item in configured["reasoning_efforts"] if item is not None]
        if requested and not declared:
            warnings.append(f"{model_id} does not publish supported_efforts; requested {requested}")
        elif declared:
            unsupported = [item for item in requested if item not in declared]
            if unsupported:
                errors.append(f"{model_id} does not declare reasoning efforts: {unsupported}")
    return errors, warnings


def estimate_ceiling_usd(
    config: dict[str, Any], jobs: list[dict[str, Any]], catalog: list[dict[str, Any]], prompt: str
) -> float:
    """Conservative output ceiling, not an expected bill.

    Prompt tokens are approximated as characters / 3 to avoid claiming a
    tokenizer-specific exact count before the requests are made.
    """
    by_id = {model["id"]: model for model in catalog}
    approximate_prompt_tokens = max(1, len(prompt) // 3)
    total = 0.0
    for job in jobs:
        pricing = by_id[job["model"]].get("pricing") or {}
        total += approximate_prompt_tokens * float(pricing.get("prompt") or 0)
        total += int(job.get("max_tokens") or config["max_tokens"]) * float(pricing.get("completion") or 0)
        total += float(pricing.get("request") or 0)
    return total


def build_request_payload(
    job: dict[str, Any], config: dict[str, Any], prompt: str
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": job["model"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": int(job.get("max_tokens") or config["max_tokens"]),
        "stream": True,
        "provider": {"require_parameters": True},
    }
    if job.get("reasoning") is not None:
        payload["reasoning"] = dict(job["reasoning"])
    elif job.get("reasoning_effort") is not None:
        payload["reasoning"] = {
            "effort": job["reasoning_effort"],
            "exclude": False,
        }
    return payload


def classify_status(content: str, error: str | None, finish_reason: str | None) -> str:
    if error or not content:
        return "failed"
    if finish_reason == "length":
        return "partial"
    return "success"


def parse_stream(
    response: Any,
    started_monotonic: float,
) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    raw_lines: list[str] = []
    content_parts: list[str] = []
    reasoning_parts: list[str] = []
    first_event: float | None = None
    first_token: float | None = None
    first_content: float | None = None
    first_reasoning: float | None = None
    usage: dict[str, Any] = {}
    generation_id: str | None = None
    resolved_model: str | None = None
    finish_reason: str | None = None
    native_finish_reason: str | None = None
    stream_error: str | None = None

    try:
        for raw_line in response:
            now = time.monotonic()
            decoded = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")
            raw_lines.append(decoded)
            if not decoded.startswith("data:"):
                continue
            data = decoded[5:].strip()
            if not data or data == "[DONE]":
                continue
            if first_event is None:
                first_event = now
            try:
                event = json.loads(data)
            except json.JSONDecodeError:
                events.append({"unparsed_data": data})
                continue
            events.append(event)

            generation_id = event.get("id") or generation_id
            resolved_model = event.get("model") or resolved_model
            if isinstance(event.get("error"), dict):
                stream_error = json.dumps(event["error"], ensure_ascii=False)
            if isinstance(event.get("usage"), dict):
                usage = event["usage"]

            for choice in event.get("choices") or []:
                if choice.get("finish_reason") is not None:
                    finish_reason = choice["finish_reason"]
                if choice.get("native_finish_reason") is not None:
                    native_finish_reason = choice["native_finish_reason"]
                delta = choice.get("delta") or {}
                content = extract_text(delta.get("content"))
                reasoning = extract_text(first_present(delta, "reasoning", "reasoning_content"))
                if not reasoning and isinstance(delta.get("reasoning_details"), list):
                    reasoning = extract_text(delta["reasoning_details"])
                if content:
                    content_parts.append(content)
                    first_content = first_content or now
                    first_token = first_token or now
                if reasoning:
                    reasoning_parts.append(reasoning)
                    first_reasoning = first_reasoning or now
                    first_token = first_token or now
    except RequestDeadlineError as exc:
        stream_error = str(exc)

    completed_monotonic = time.monotonic()
    elapsed_after_first = (
        completed_monotonic - first_token if first_token is not None else None
    )
    completion_tokens = as_int(usage.get("completion_tokens"))
    tokens_per_second = (
        completion_tokens / elapsed_after_first
        if completion_tokens is not None and elapsed_after_first and elapsed_after_first > 0
        else None
    )
    return {
        "events": events,
        "raw_sse": "\n".join(raw_lines) + "\n",
        "content": "".join(content_parts),
        "reasoning": "".join(reasoning_parts),
        "usage": usage,
        "generation_id": generation_id,
        "resolved_model": resolved_model,
        "finish_reason": finish_reason,
        "native_finish_reason": native_finish_reason,
        "total_ms": round((completed_monotonic - started_monotonic) * 1000, 3),
        "time_to_first_event_ms": round((first_event - started_monotonic) * 1000, 3) if first_event else None,
        "time_to_first_token_ms": round((first_token - started_monotonic) * 1000, 3) if first_token else None,
        "time_to_first_content_ms": round((first_content - started_monotonic) * 1000, 3) if first_content else None,
        "time_to_first_reasoning_ms": round((first_reasoning - started_monotonic) * 1000, 3) if first_reasoning else None,
        "tokens_per_second": round(tokens_per_second, 3) if tokens_per_second is not None else None,
        "stream_error": stream_error,
    }


def post_stream_request(api_key: str, payload: dict[str, Any], timeout: int) -> tuple[dict[str, Any], dict[str, str]]:
    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        f"{OPENROUTER_API}/chat/completions",
        data=body,
        headers=api_headers(api_key, "text/event-stream"),
        method="POST",
    )
    started_monotonic = time.monotonic()
    with wall_clock_deadline(timeout):
        with urllib.request.urlopen(request, timeout=timeout) as response:
            safe_headers = {
                key.lower(): value
                for key, value in response.headers.items()
                if key.lower() in {"content-type", "x-request-id", "x-ratelimit-limit", "x-ratelimit-remaining"}
            }
            return parse_stream(response, started_monotonic), safe_headers


def generation_provider(generation: dict[str, Any] | None) -> str | None:
    if not generation:
        return None
    return first_present(generation, "provider_name", "provider", "provider_id")


def create_response_markdown(row: dict[str, Any], content: str, reasoning: str) -> str:
    lines = [
        f"# {row['model']} — {row['reasoning_effort_label']}",
        "",
        f"- Status: {row['status']}",
        f"- Provider route: {row.get('provider') or 'not reported'}",
        f"- Total time: {format_ms(row.get('total_ms'))}",
        f"- Time to first token: {format_ms(row.get('time_to_first_token_ms'))}",
        f"- Time to first visible content: {format_ms(row.get('time_to_first_content_ms'))}",
        f"- Input / output / reasoning tokens: {row.get('prompt_tokens') or 0} / {row.get('completion_tokens') or 0} / {row.get('reasoning_tokens') or 0}",
        f"- Cost: {format_cost(row.get('cost_usd'))}",
        f"- Finish reason: {row.get('finish_reason') or 'not reported'}",
        "",
        "## Response",
        "",
        content or "_No visible response content was returned._",
    ]
    if reasoning:
        lines.extend(["", "## Returned reasoning", "", reasoning])
    if row.get("error"):
        lines.extend(["", "## Error", "", f"```text\n{row['error']}\n```"])
    return "\n".join(lines).rstrip() + "\n"


def run_job(
    job: dict[str, Any],
    config: dict[str, Any],
    prompt: str,
    api_key: str,
    run_dir: Path,
    model_name: str | None,
    benchmark_attempt: int = 1,
) -> dict[str, Any]:
    effort = job["reasoning_effort"]
    effort_label = job["reasoning_effort_label"]
    payload = build_request_payload(job, config, prompt)

    started_at = utc_now()
    parsed: dict[str, Any] | None = None
    generation: dict[str, Any] | None = None
    safe_headers: dict[str, str] = {}
    error: str | None = None
    attempt_count = 0

    for attempt in range(1, 4):
        attempt_count = attempt
        try:
            parsed, safe_headers = post_stream_request(
                api_key, payload, int(config["request_timeout_seconds"])
            )
            error = parsed.get("stream_error")
            break
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            error = f"HTTP {exc.code}: {body[:4000]}"
            if exc.code not in {408, 409, 429, 500, 502, 503, 504} or attempt == 3:
                break
            time.sleep(2 ** attempt)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            error = f"{type(exc).__name__}: {exc}"
            if attempt == 3:
                break
            time.sleep(2 ** attempt)

    completed_at = utc_now()
    parsed = parsed or {
        "events": [],
        "raw_sse": "",
        "content": "",
        "reasoning": "",
        "usage": {},
        "generation_id": None,
        "resolved_model": None,
        "finish_reason": None,
        "native_finish_reason": None,
        "total_ms": None,
        "time_to_first_event_ms": None,
        "time_to_first_token_ms": None,
        "time_to_first_content_ms": None,
        "time_to_first_reasoning_ms": None,
        "tokens_per_second": None,
        "stream_error": error,
    }
    usage = parsed["usage"] or {}
    completion_details = usage.get("completion_tokens_details") or {}
    prompt_details = usage.get("prompt_tokens_details") or {}
    raw_relative = f"raw/{job['run_id']}.json"
    sse_relative = f"raw/{job['run_id']}.sse"
    response_relative = f"responses/{safe_slug(job['model'])}/{effort_label}.md"

    generation_cost = first_present(generation or {}, "total_cost", "cost")
    row = {
        "run_id": job["run_id"],
        "sequence": job["sequence"],
        "family": job["family"],
        "model": job["model"],
        "model_name": model_name,
        "reasoning_effort": effort,
        "reasoning_effort_label": effort_label,
        "reasoning_config": payload.get("reasoning"),
        "max_tokens": payload["max_tokens"],
        "status": classify_status(parsed["content"], error, parsed.get("finish_reason")),
        "started_at": started_at,
        "completed_at": completed_at,
        "attempt_count": attempt_count,
        "benchmark_attempt": benchmark_attempt,
        "generation_id": parsed.get("generation_id"),
        "resolved_model": parsed.get("resolved_model"),
        "provider": generation_provider(generation),
        "provider_model": None,
        "openrouter_latency_ms": None,
        "openrouter_generation_time_ms": None,
        "upstream_provider_latency_ms": None,
        "service_tier": None,
        "data_region": None,
        "is_byok": None,
        "cache_discount_usd": None,
        "finish_reason": parsed.get("finish_reason"),
        "native_finish_reason": parsed.get("native_finish_reason"),
        "total_ms": parsed.get("total_ms"),
        "time_to_first_event_ms": parsed.get("time_to_first_event_ms"),
        "time_to_first_token_ms": parsed.get("time_to_first_token_ms"),
        "time_to_first_content_ms": parsed.get("time_to_first_content_ms"),
        "time_to_first_reasoning_ms": parsed.get("time_to_first_reasoning_ms"),
        "tokens_per_second": parsed.get("tokens_per_second"),
        "prompt_tokens": as_int(usage.get("prompt_tokens")) or as_int((generation or {}).get("tokens_prompt")),
        "completion_tokens": as_int(usage.get("completion_tokens")) or as_int((generation or {}).get("tokens_completion")),
        "reasoning_tokens": as_int(completion_details.get("reasoning_tokens")),
        "total_tokens": as_int(usage.get("total_tokens")),
        "cached_tokens": as_int(prompt_details.get("cached_tokens")),
        "cost_usd": as_float(usage.get("cost")) if usage.get("cost") is not None else as_float(generation_cost),
        "content_characters": len(parsed["content"]),
        "reasoning_characters": len(parsed["reasoning"]),
        "response_path": response_relative,
        "raw_path": raw_relative,
        "raw_sse_path": sse_relative,
        "error": error,
    }

    raw_artifact = {
        "request": payload,
        "request_prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "response_headers": safe_headers,
        "events": parsed["events"],
        "assembled": {
            "content": parsed["content"],
            "reasoning": parsed["reasoning"],
        },
        "generation": generation,
        "result": row,
    }
    json_dump(run_dir / raw_relative, raw_artifact)
    (run_dir / sse_relative).write_text(parsed["raw_sse"], encoding="utf-8")
    response_path = run_dir / response_relative
    response_path.parent.mkdir(parents=True, exist_ok=True)
    response_path.write_text(
        create_response_markdown(row, parsed["content"], parsed["reasoning"]), encoding="utf-8"
    )
    return row


def apply_generation_metadata(row: dict[str, Any], generation: dict[str, Any]) -> None:
    provider_responses = generation.get("provider_responses") or []
    upstream_latencies = [
        as_float(item.get("latency"))
        for item in provider_responses
        if isinstance(item, dict) and item.get("latency") is not None
    ]
    row["provider"] = generation_provider(generation) or row.get("provider")
    row["provider_model"] = generation.get("model") or row.get("provider_model")
    row["resolved_model"] = generation.get("model") or row.get("resolved_model")
    row["openrouter_latency_ms"] = as_float(generation.get("latency"))
    row["openrouter_generation_time_ms"] = as_float(generation.get("generation_time"))
    row["upstream_provider_latency_ms"] = (
        min(value for value in upstream_latencies if value is not None)
        if any(value is not None for value in upstream_latencies)
        else None
    )
    row["service_tier"] = generation.get("service_tier")
    row["data_region"] = generation.get("data_region")
    row["is_byok"] = generation.get("is_byok")
    row["cache_discount_usd"] = as_float(generation.get("cache_discount"))
    row["finish_reason"] = generation.get("finish_reason") or row.get("finish_reason")
    row["native_finish_reason"] = generation.get("native_finish_reason") or row.get("native_finish_reason")
    native_prompt = as_int(generation.get("native_tokens_prompt"))
    native_completion = as_int(generation.get("native_tokens_completion"))
    native_reasoning = as_int(generation.get("native_tokens_reasoning"))
    native_cached = as_int(generation.get("native_tokens_cached"))
    generation_cost = as_float(first_present(generation, "total_cost", "usage"))
    if native_prompt is not None:
        row["prompt_tokens"] = native_prompt
    if native_completion is not None:
        row["completion_tokens"] = native_completion
    if native_reasoning is not None:
        row["reasoning_tokens"] = native_reasoning
    if native_cached is not None:
        row["cached_tokens"] = native_cached
    if generation_cost is not None:
        row["cost_usd"] = generation_cost
    if row.get("prompt_tokens") is not None and row.get("completion_tokens") is not None:
        row["total_tokens"] = int(row["prompt_tokens"]) + int(row["completion_tokens"])


def backfill_generation_metadata(
    rows: list[dict[str, Any]], api_key: str, run_dir: Path
) -> None:
    candidates = [row for row in rows if row.get("generation_id")]
    if not candidates:
        return
    print(f"Backfilling OpenRouter generation metadata for {len(candidates)} runs...", flush=True)
    for index, row in enumerate(candidates, start=1):
        raw_path = run_dir / row["raw_path"]
        raw = json.loads(raw_path.read_text(encoding="utf-8"))
        generation = raw.get("generation")
        if not isinstance(generation, dict):
            generation = fetch_generation(api_key, row["generation_id"])
        if isinstance(generation, dict):
            apply_generation_metadata(row, generation)
            raw["generation"] = generation
            raw["result"] = row
            json_dump(raw_path, raw)
            assembled = raw.get("assembled") or {}
            if assembled:
                (run_dir / row["response_path"]).write_text(
                    create_response_markdown(
                        row,
                        assembled.get("content") or "",
                        assembled.get("reasoning") or "",
                    ),
                    encoding="utf-8",
                )
        if index % 10 == 0 or index == len(candidates):
            print(f"  metadata {index}/{len(candidates)}", flush=True)


def percentile(values: Iterable[float], pct: float) -> float | None:
    ordered = sorted(values)
    if not ordered:
        return None
    if len(ordered) == 1:
        return ordered[0]
    index = (len(ordered) - 1) * pct
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    weight = index - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    successful = [row for row in rows if row["status"] == "success"]
    partial = [row for row in rows if row["status"] == "partial"]
    failed = [row for row in rows if row["status"] == "failed"]

    def nums(field: str) -> list[float]:
        return [float(row[field]) for row in rows if row.get(field) is not None]

    durations = nums("total_ms")
    first_tokens = nums("time_to_first_token_ms")
    first_content = nums("time_to_first_content_ms")
    throughput = nums("tokens_per_second")
    costs = nums("cost_usd")
    successful_costs = [
        float(row["cost_usd"])
        for row in successful
        if row.get("cost_usd") is not None
    ]
    partial_costs = [
        float(row["cost_usd"])
        for row in partial
        if row.get("cost_usd") is not None
    ]
    failed_costs = [
        float(row["cost_usd"])
        for row in failed
        if row.get("cost_usd") is not None
    ]
    started = [row["started_at"] for row in rows if row.get("started_at")]
    completed = [row["completed_at"] for row in rows if row.get("completed_at")]
    return {
        "runs": len(rows),
        "successful_runs": len(successful),
        "partial_runs": len(partial),
        "failed_runs": len(failed),
        "non_successful_runs": len(partial) + len(failed),
        "total_cost_usd": round(sum(costs), 9),
        "successful_cost_usd": round(sum(successful_costs), 9),
        "partial_cost_usd": round(sum(partial_costs), 9),
        "failed_cost_usd": round(sum(failed_costs), 9),
        "incomplete_cost_usd": round(sum(partial_costs) + sum(failed_costs), 9),
        "average_cost_usd": round(statistics.mean(costs), 9) if costs else None,
        "prompt_tokens": sum(int(row.get("prompt_tokens") or 0) for row in rows),
        "completion_tokens": sum(int(row.get("completion_tokens") or 0) for row in rows),
        "reasoning_tokens": sum(int(row.get("reasoning_tokens") or 0) for row in rows),
        "total_tokens": sum(int(row.get("total_tokens") or 0) for row in rows),
        "cached_tokens": sum(int(row.get("cached_tokens") or 0) for row in rows),
        "sum_request_seconds": round(sum(durations) / 1000, 3),
        "average_total_ms": round(statistics.mean(durations), 3) if durations else None,
        "median_total_ms": round(statistics.median(durations), 3) if durations else None,
        "p95_total_ms": round(percentile(durations, 0.95), 3) if durations else None,
        "min_total_ms": round(min(durations), 3) if durations else None,
        "max_total_ms": round(max(durations), 3) if durations else None,
        "average_time_to_first_token_ms": round(statistics.mean(first_tokens), 3) if first_tokens else None,
        "average_time_to_first_content_ms": round(statistics.mean(first_content), 3) if first_content else None,
        "average_tokens_per_second": round(statistics.mean(throughput), 3) if throughput else None,
        "first_started_at": min(started) if started else None,
        "last_completed_at": max(completed) if completed else None,
    }


def build_summary(rows: list[dict[str, Any]], prompt_sha256: str) -> dict[str, Any]:
    by_model_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_family_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_effort_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_model_rows[row["model"]].append(row)
        by_family_rows[row["family"]].append(row)
        by_effort_rows[row["reasoning_effort_label"]].append(row)
    return {
        "generated_at": utc_now(),
        "prompt_sha256": prompt_sha256,
        "experiment": aggregate(rows),
        "by_family": {key: aggregate(value) for key, value in sorted(by_family_rows.items())},
        "by_model": {key: aggregate(value) for key, value in sorted(by_model_rows.items())},
        "by_reasoning_effort": {key: aggregate(value) for key, value in sorted(by_effort_rows.items())},
    }


def format_cost(value: Any) -> str:
    number = as_float(value)
    return f"${number:.6f}" if number is not None else "n/a"


def format_ms(value: Any) -> str:
    number = as_float(value)
    return f"{number / 1000:.3f}s" if number is not None else "n/a"


def format_number(value: Any, digits: int = 1) -> str:
    number = as_float(value)
    return f"{number:,.{digits}f}" if number is not None else "n/a"


def summary_markdown(
    summary: dict[str, Any], rows: list[dict[str, Any]], manifest: dict[str, Any]
) -> str:
    total = summary["experiment"]
    lines = [
        f"# {manifest['experiment_name']}",
        "",
        f"Generated: {summary['generated_at']}",
        "",
        "All runs used the exact same single user message. The only intentional per-run changes were the model and, where supported, the reasoning effort. Timing is end-to-end from this machine. Runs were sequential and shuffled with a fixed seed.",
        "",
        "## Experiment totals",
        "",
        f"- Runs: {total['successful_runs']} successful / {total['partial_runs']} partial / {total['failed_runs']} failed / {total['runs']} total",
        f"- Primary-matrix billed cost: {format_cost(total['total_cost_usd'])} ({format_cost(total['successful_cost_usd'])} successful + {format_cost(total['partial_cost_usd'])} partial + {format_cost(total['failed_cost_usd'])} failed)",
        f"- Tokens: {total['prompt_tokens']:,} input / {total['completion_tokens']:,} output / {total['reasoning_tokens']:,} reasoning",
        f"- Sum of request time: {total['sum_request_seconds']:,.3f}s",
        f"- Median request time: {format_ms(total['median_total_ms'])}",
        f"- Average time to first token: {format_ms(total['average_time_to_first_token_ms'])}",
    ]
    accounting = summary.get("accounting")
    if accounting:
        lines.extend(
            [
                "",
                "## Whole-experiment accounting",
                "",
                f"- OpenRouter account-usage delta: {format_cost(accounting.get('account_usage_delta_usd'))}",
                f"- Primary 72-pair matrix: {format_cost(accounting.get('primary_matrix_cost_usd'))}",
                f"- Archived failed first attempts: {format_cost(accounting.get('archived_attempt_cost_usd'))}",
                f"- Separate preflight: {format_cost(accounting.get('preflight_cost_usd'))}",
                f"- Failed-run recovery investigation: {format_cost(accounting.get('recovery_investigation_cost_usd'))}",
                f"- Interrupted/unattributed provider call: {format_cost(accounting.get('unattributed_cost_usd'))}",
                f"- Full 72-pair workflow wall time, including retries: {format_ms((accounting.get('primary_matrix_wall_clock_seconds') or 0) * 1000)}",
                f"- Recovery investigation wall time: {format_ms((accounting.get('recovery_investigation_wall_clock_seconds') or 0) * 1000)}",
                f"- Whole workflow wall time, including investigation: {format_ms((accounting.get('whole_workflow_wall_clock_seconds') or 0) * 1000)}",
                f"- Known artifact tokens, including retries/preflight/recovery: {int(accounting.get('known_artifact_prompt_tokens') or 0):,} input / {int(accounting.get('known_artifact_completion_tokens') or 0):,} output / {int(accounting.get('known_artifact_reasoning_tokens') or 0):,} reasoning",
                "",
                accounting.get("note", ""),
            ]
        )
    lines.extend(
        [
            "",
            "## Family stats",
            "",
            "| Family | Success / partial / failed | Cost | Input tokens | Output tokens | Reasoning tokens | Avg total | Avg first token | Avg tok/s |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for family, stats in summary["by_family"].items():
        lines.append(
            f"| {family} | {stats['successful_runs']} / {stats['partial_runs']} / {stats['failed_runs']} | {format_cost(stats['total_cost_usd'])} | {stats['prompt_tokens']:,} | {stats['completion_tokens']:,} | {stats['reasoning_tokens']:,} | {format_ms(stats['average_total_ms'])} | {format_ms(stats['average_time_to_first_token_ms'])} | {format_number(stats['average_tokens_per_second'])} |"
        )
    lines.extend(
        [
            "",
            "## Model stats",
            "",
            "| Model | Success / partial / failed | Cost | Input tokens | Output tokens | Reasoning tokens | Avg total | Median total | Avg first token | Avg tok/s |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for model, stats in summary["by_model"].items():
        lines.append(
            f"| `{model}` | {stats['successful_runs']} / {stats['partial_runs']} / {stats['failed_runs']} | {format_cost(stats['total_cost_usd'])} | {stats['prompt_tokens']:,} | {stats['completion_tokens']:,} | {stats['reasoning_tokens']:,} | {format_ms(stats['average_total_ms'])} | {format_ms(stats['median_total_ms'])} | {format_ms(stats['average_time_to_first_token_ms'])} | {format_number(stats['average_tokens_per_second'])} |"
        )
    lines.extend(
        [
            "",
            "## Every run",
            "",
            "| # | Model | Effort | Status | Cost | Input | Output | Reasoning | First token | First content | Total | Tok/s | Response |",
            "|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in sorted(rows, key=lambda item: item["sequence"]):
        link = f"[view]({row['response_path']})"
        lines.append(
            f"| {row['sequence']} | `{row['model']}` | {row['reasoning_effort_label']} | {row['status']} | {format_cost(row.get('cost_usd'))} | {row.get('prompt_tokens') or 0:,} | {row.get('completion_tokens') or 0:,} | {row.get('reasoning_tokens') or 0:,} | {format_ms(row.get('time_to_first_token_ms'))} | {format_ms(row.get('time_to_first_content_ms'))} | {format_ms(row.get('total_ms'))} | {format_number(row.get('tokens_per_second'))} | {link} |"
        )
    lines.extend(
        [
            "",
            "## Method notes",
            "",
            "- One run was made per model/effort pair. Latency differences are directional, not statistically stable repeated-trial estimates.",
            "- Output token counts include reasoning tokens where the provider reports them; the reasoning-token column is the reported subset.",
            "- OpenRouter chooses the upstream provider route unless a model has only one route. The returned route is saved when the generation endpoint reports it.",
            "- `max` and `xhigh` are both included when advertised even though OpenRouter documents them as equivalent budget allocations for some models.",
            "- The conservative preflight ceiling assumes every request consumes the entire output cap. It is not an expected-cost forecast.",
            "",
        ]
    )
    return "\n".join(lines)


def rewrite_reports(run_dir: Path, rows: list[dict[str, Any]], manifest: dict[str, Any]) -> None:
    rows = sorted(rows, key=lambda item: item["sequence"])
    for row in rows:
        raw_path = run_dir / row["raw_path"]
        raw = json.loads(raw_path.read_text(encoding="utf-8")) if raw_path.exists() else {}
        request = raw.get("request") or {}
        assembled = raw.get("assembled") or {}
        row["reasoning_config"] = row.get("reasoning_config") or request.get("reasoning")
        row["max_tokens"] = row.get("max_tokens") or request.get("max_tokens") or manifest.get("max_tokens")
        has_content = bool(row.get("content_characters") or assembled.get("content"))
        row["status"] = classify_status(
            "content" if has_content else "",
            row.get("error"),
            row.get("finish_reason"),
        )
        if raw:
            raw["result"] = row
            json_dump(raw_path, raw)
            (run_dir / row["response_path"]).write_text(
                create_response_markdown(
                    row,
                    assembled.get("content") or "",
                    assembled.get("reasoning") or "",
                ),
                encoding="utf-8",
            )
    results_path = run_dir / "results.jsonl"
    results_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    summary = build_summary(rows, manifest["prompt_sha256"])
    accounting_path = run_dir / "accounting.json"
    if accounting_path.exists():
        summary["accounting"] = json.loads(accounting_path.read_text(encoding="utf-8"))
    json_dump(run_dir / "summary.json", summary)
    (run_dir / "summary.md").write_text(
        summary_markdown(summary, rows, manifest), encoding="utf-8"
    )


def read_existing_results(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def archive_attempt(run_dir: Path, row: dict[str, Any], attempt_number: int) -> None:
    attempt_dir = run_dir / "attempts" / row["run_id"] / f"attempt-{attempt_number}"
    attempt_dir.mkdir(parents=True, exist_ok=True)
    json_dump(attempt_dir / "result.json", row)
    for field in ("raw_path", "raw_sse_path", "response_path"):
        relative = row.get(field)
        if not relative:
            continue
        source = run_dir / relative
        if source.exists():
            shutil.copy2(source, attempt_dir / source.name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config/benchmark.json")
    parser.add_argument("--prompt", type=Path, default=ROOT / "prompts/woodchuck.txt")
    parser.add_argument("--output-root", type=Path, default=ROOT / "runs")
    parser.add_argument("--run-dir", type=Path, help="Resume or write into this exact run directory")
    parser.add_argument("--only", help="Regex matched against model id or family")
    parser.add_argument("--limit", type=int, help="Run at most this many selected jobs")
    parser.add_argument("--dry-run", action="store_true", help="Validate and show the matrix without paid calls")
    parser.add_argument(
        "--retry-failed",
        action="store_true",
        help="Archive and rerun failed rows with the exact same request payload",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_dotenv(ROOT / ".env")
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("OPENROUTER_API_KEY is missing from the environment or .env", file=sys.stderr)
        return 2

    config = json.loads(args.config.read_text(encoding="utf-8"))
    prompt = args.prompt.read_text(encoding="utf-8").rstrip("\r\n")
    prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    jobs = build_jobs(config)
    if args.only:
        pattern = re.compile(args.only, re.IGNORECASE)
        jobs = [job for job in jobs if pattern.search(job["model"]) or pattern.search(job["family"])]
    if args.limit is not None:
        jobs = jobs[: args.limit]
    if not jobs:
        print("No jobs matched the requested filters", file=sys.stderr)
        return 2

    print("Fetching live OpenRouter model metadata...", flush=True)
    catalog = fetch_catalog(api_key)
    errors, warnings = validate_matrix(config, catalog)
    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2

    ceiling = estimate_ceiling_usd(config, jobs, catalog, prompt)
    print(f"Selected jobs: {len(jobs)}")
    print(f"Prompt SHA-256: {prompt_sha256}")
    print(f"Conservative max-token cost ceiling: ${ceiling:.4f}")
    for job in jobs:
        print(f"  {job['sequence']:03d}  {job['model']}  {job['reasoning_effort_label']}")
    if args.dry_run:
        return 0

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = (args.run_dir or (args.output_root / timestamp)).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    by_id = {model["id"]: model for model in catalog}
    selected_ids = sorted({job["model"] for job in jobs})
    manifest = {
        "experiment_name": config["experiment_name"],
        "description": config.get("description"),
        "created_at": utc_now(),
        "prompt": prompt,
        "prompt_sha256": prompt_sha256,
        "message_context": [{"role": "user", "content": prompt}],
        "max_tokens": config["max_tokens"],
        "shuffle_seed": config["shuffle_seed"],
        "streaming": True,
        "execution": "sequential",
        "conservative_cost_ceiling_usd": round(ceiling, 9),
        "jobs": jobs,
        "model_catalog_snapshot": {model_id: by_id[model_id] for model_id in selected_ids},
    }
    manifest_path = run_dir / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("prompt_sha256") != prompt_sha256:
            print("Refusing to resume: prompt hash differs from the existing manifest", file=sys.stderr)
            return 2
    else:
        json_dump(manifest_path, manifest)

    rows = read_existing_results(run_dir / "results.jsonl")
    benchmark_attempts: dict[str, int] = {}
    if args.retry_failed:
        failed_by_id = {row["run_id"]: row for row in rows if row["status"] != "success"}
        for run_id, prior in failed_by_id.items():
            prior_attempt = int(prior.get("benchmark_attempt") or 1)
            archive_attempt(run_dir, prior, prior_attempt)
            benchmark_attempts[run_id] = prior_attempt + 1
        rows = [row for row in rows if row["run_id"] not in failed_by_id]
        remaining = [job for job in jobs if job["run_id"] in failed_by_id]
    else:
        completed_ids = {row["run_id"] for row in rows}
        remaining = [job for job in jobs if job["run_id"] not in completed_ids]
    print(f"Run directory: {run_dir}")
    print(f"Remaining jobs: {len(remaining)}", flush=True)

    for index, job in enumerate(remaining, start=1):
        effort = job["reasoning_effort_label"]
        print(
            f"[{index}/{len(remaining)}] {job['model']} ({effort})...",
            end=" ",
            flush=True,
        )
        row = run_job(
            job,
            config,
            prompt,
            api_key,
            run_dir,
            (by_id.get(job["model"]) or {}).get("name"),
            benchmark_attempts.get(job["run_id"], 1),
        )
        rows.append(row)
        rewrite_reports(run_dir, rows, manifest)
        print(
            f"{row['status']} in {format_ms(row.get('total_ms'))}, {format_cost(row.get('cost_usd'))}",
            flush=True,
        )

    backfill_generation_metadata(rows, api_key, run_dir)
    rewrite_reports(run_dir, rows, manifest)
    incomplete = sum(1 for row in rows if row["status"] != "success")
    print(f"Complete: {len(rows) - incomplete} succeeded, {incomplete} incomplete")
    print(f"Summary: {run_dir / 'summary.md'}")
    return 1 if incomplete else 0


if __name__ == "__main__":
    raise SystemExit(main())
