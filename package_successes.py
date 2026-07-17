#!/usr/bin/env python3
"""Build a clean, success-only benchmark deliverable."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PRIMARY_RUN = ROOT / "runs/20260715T223949Z"
OUTPUT = ROOT / "results"
PROMPT_SHA256 = "a8bd16d59f62e340517bf960c614d4b7a23b25e8bc6410ef695d9136b19f515f"

RECOVERIES = [
    {
        "run_dir": ROOT / "runs/recovery/openai-luna-max-65536",
        "effort": "max",
        "profile": "recovered: 65,536 output-token ceiling",
    },
    {
        "run_dir": ROOT / "runs/recovery/openai-terra-max-65536",
        "effort": "max",
        "profile": "recovered: 65,536 output-token ceiling",
    },
    {
        "run_dir": ROOT / "runs/recovery/openai-sol-max-65536",
        "effort": "max",
        "profile": "recovered: 65,536 output-token ceiling",
    },
    {
        "run_dir": ROOT / "runs/recovery/claude-sonnet-budget-12000",
        "effort": "max",
        "profile": "recovered: 12,000 reasoning-token budget",
    },
]


def read_rows(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-")


def load_content(run_dir: Path, row: dict[str, Any]) -> str:
    raw = json.loads((run_dir / row["raw_path"]).read_text(encoding="utf-8"))
    if raw.get("request_prompt_sha256") != PROMPT_SHA256:
        raise ValueError(f"Prompt hash mismatch for {row['model']} {row['reasoning_effort_label']}")
    content = ((raw.get("assembled") or {}).get("content") or "").strip()
    if not content:
        raise ValueError(f"No visible content for {row['model']} {row['reasoning_effort_label']}")
    return content


def add_result(
    records: list[dict[str, Any]],
    seen: set[tuple[str, str]],
    run_dir: Path,
    row: dict[str, Any],
    effort: str,
    profile: str,
) -> None:
    if row["status"] != "success" or row.get("finish_reason") == "length":
        raise ValueError(f"Non-success supplied for packaging: {row['model']} {effort}")
    key = (row["model"], effort)
    if key in seen:
        raise ValueError(f"Duplicate model/effort result: {key}")
    seen.add(key)

    content = load_content(run_dir, row)
    response_relative = Path("responses", *row["model"].split("/"), f"{safe_slug(effort)}.md")
    record = dict(row)
    record["reasoning_effort_label"] = effort
    record["profile"] = profile
    record["response_relative"] = response_relative
    record["content"] = content
    records.append(record)


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    durations = [Decimal(str(row.get("total_ms") or 0)) for row in rows]
    costs = [Decimal(str(row.get("cost_usd") or 0)) for row in rows]
    return {
        "runs": len(rows),
        "cost": sum(costs, Decimal("0")),
        "prompt_tokens": sum(int(row.get("prompt_tokens") or 0) for row in rows),
        "completion_tokens": sum(int(row.get("completion_tokens") or 0) for row in rows),
        "reasoning_tokens": sum(int(row.get("reasoning_tokens") or 0) for row in rows),
        "sum_seconds": sum(durations, Decimal("0")) / Decimal("1000"),
        "average_seconds": (
            sum(durations, Decimal("0")) / Decimal("1000") / Decimal(len(rows))
            if rows
            else Decimal("0")
        ),
    }


def money(value: Decimal, digits: int = 6) -> str:
    return f"${value:.{digits}f}"


def seconds(value: Decimal) -> str:
    return f"{value:.3f}s"


def render_stats(records: list[dict[str, Any]]) -> str:
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        by_family[row["family"]].append(row)
        by_model[row["model"]].append(row)

    total = aggregate(records)
    lines = [
        "# Successful benchmark results",
        "",
        f"- Successful model/effort results: {total['runs']}",
        f"- Core model cost: {money(total['cost'], 9)}",
        f"- Tokens: {total['prompt_tokens']:,} input / {total['completion_tokens']:,} output / {total['reasoning_tokens']:,} reasoning",
        f"- Sum of successful request time: {seconds(total['sum_seconds'])}",
        "",
        "Core model cost is the direct sum of `cost_usd` for the included successful responses. It excludes failed and partial attempts, retries, preflight calls, interrupted calls, account reconciliation differences, and OpenRouter-level fees.",
        "",
        "All 71 files use the same prompt. Four entries are complete recovery replacements: Luna, Terra, and Sol at `max` use a 65,536-token output ceiling; Claude Sonnet 5 uses a 12,000-token reasoning budget. Sol Pro `max` is omitted because it never completed.",
        "",
        "## By family",
        "",
        "| Family | Results | Core cost | Input | Output | Reasoning | Avg time |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for family, rows in sorted(by_family.items()):
        stats = aggregate(rows)
        lines.append(
            f"| {family} | {stats['runs']} | {money(stats['cost'])} | {stats['prompt_tokens']:,} | {stats['completion_tokens']:,} | {stats['reasoning_tokens']:,} | {seconds(stats['average_seconds'])} |"
        )

    lines.extend(
        [
            "",
            "## By model",
            "",
            "| Model | Results | Core cost | Input | Output | Reasoning | Avg time |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for model, rows in sorted(by_model.items()):
        stats = aggregate(rows)
        lines.append(
            f"| `{model}` | {stats['runs']} | {money(stats['cost'])} | {stats['prompt_tokens']:,} | {stats['completion_tokens']:,} | {stats['reasoning_tokens']:,} | {seconds(stats['average_seconds'])} |"
        )

    lines.extend(
        [
            "",
            "## Every successful result",
            "",
            "| Model | Effort | Request profile | Core cost | Input | Output | Reasoning | Total time | Response |",
            "|---|---|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in sorted(records, key=lambda item: (item["family"], item["model"], item["reasoning_effort_label"])):
        total_seconds = Decimal(str(row.get("total_ms") or 0)) / Decimal("1000")
        link = row["response_relative"].as_posix()
        lines.append(
            f"| `{row['model']}` | {row['reasoning_effort_label']} | {row['profile']} | {money(Decimal(str(row.get('cost_usd') or 0)))} | {int(row.get('prompt_tokens') or 0):,} | {int(row.get('completion_tokens') or 0):,} | {int(row.get('reasoning_tokens') or 0):,} | {seconds(total_seconds)} | [view]({link}) |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing deliverable: {OUTPUT}")

    records: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for row in read_rows(PRIMARY_RUN / "results.jsonl"):
        if row["status"] == "success":
            add_result(
                records,
                seen,
                PRIMARY_RUN,
                row,
                row["reasoning_effort_label"],
                "primary",
            )

    for recovery in RECOVERIES:
        rows = read_rows(recovery["run_dir"] / "results.jsonl")
        if len(rows) != 1:
            raise ValueError(f"Expected one recovery row in {recovery['run_dir']}")
        add_result(
            records,
            seen,
            recovery["run_dir"],
            rows[0],
            recovery["effort"],
            recovery["profile"],
        )

    if len(records) != 71:
        raise ValueError(f"Expected 71 unique successful results, found {len(records)}")

    for row in records:
        destination = OUTPUT / row["response_relative"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            f"# {row['model']} - {row['reasoning_effort_label']}\n\n{row['content']}\n",
            encoding="utf-8",
        )
    (OUTPUT / "stats.md").write_text(render_stats(records), encoding="utf-8")
    print(f"Created {OUTPUT} with {len(records)} successful responses")


if __name__ == "__main__":
    main()
