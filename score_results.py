#!/usr/bin/env python3
"""Deterministically score the clean woodchuck responses for prompt compliance."""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Any


ROOT = Path(__file__).resolve().parent
CLEAN = ROOT / "results"
STATS = CLEAN / "stats.md"
OUTPUT_CSV = CLEAN / "scores.csv"
OUTPUT_REPORT = CLEAN / "evaluation.md"

MAX_POINTS = {
    "json_valid": 12,
    "json_final": 6,
    "json_estimate": 2,
    "json_assumptions": 2,
    "json_uncertainty": 2,
    "json_units": 2,
    "json_haiku": 2,
    "json_pirate": 2,
    "numeric_answer": 3,
    "si_units": 4,
    "imperial_units": 4,
    "consistent_conversion": 6,
    "numeric_uncertainty": 4,
    "transparent_math": 4,
    "explicit_assumptions": 5,
    "multiple_assumptions": 3,
    "citations": 4,
    "source_locator": 3,
    "haiku_present": 5,
    "haiku_three_lines": 4,
    "haiku_575": 6,
    "pirate_present": 3,
    "pirate_style": 2,
    "linguistics": 2,
    "history": 2,
    "physics_math": 2,
    "humor_signal": 2,
    "organized": 2,
}

SECTIONS = {
    "JSON and output structure": [
        "json_valid", "json_final", "json_estimate", "json_assumptions",
        "json_uncertainty", "json_units", "json_haiku", "json_pirate",
    ],
    "Quantitative and scientific compliance": [
        "numeric_answer", "si_units", "imperial_units", "consistent_conversion",
        "numeric_uncertainty", "transparent_math",
    ],
    "Assumptions and evidence": [
        "explicit_assumptions", "multiple_assumptions", "citations", "source_locator",
    ],
    "Creative requirements": [
        "haiku_present", "haiku_three_lines", "haiku_575", "pirate_present", "pirate_style",
    ],
    "Breadth and structure": [
        "linguistics", "history", "physics_math", "humor_signal", "organized",
    ],
}

SYLLABLE_OVERRIDES = {
    "arr": 1, "burrow": 2, "burrows": 2, "chuck": 1, "chucked": 1,
    "chucking": 2, "dreamed": 1, "every": 2, "fire": 1, "fired": 1,
    "forest": 2, "groundhog": 2, "hour": 1, "hours": 1, "marmot": 2,
    "meadow": 2, "poem": 2, "quiet": 2, "science": 2, "seven": 2,
    "timber": 2, "tongue": 1, "uncertainty": 5, "whistle": 2,
    "wood": 1, "woodchuck": 2, "woodchucks": 2,
}


@dataclass
class JsonCandidate:
    value: Any
    start: int
    end: int
    final: bool


def strip_package_heading(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
        if lines and not lines[0].strip():
            lines = lines[1:]
    return "\n".join(lines).strip()


def only_trivia(text: str) -> bool:
    stripped = re.sub(r"[\s`*_#>-]+", "", text)
    return not stripped


def json_candidate(text: str) -> JsonCandidate | None:
    candidates: list[JsonCandidate] = []
    for match in re.finditer(r"```(?:json|JSON)?\s*\n?(.*?)\n?```", text, flags=re.DOTALL):
        try:
            value = json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            continue
        candidates.append(JsonCandidate(value, match.start(), match.end(), only_trivia(text[match.end():])))

    stripped = text.strip()
    try:
        value = json.loads(stripped)
        start = text.find(stripped)
        candidates.append(JsonCandidate(value, start, start + len(stripped), True))
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    for match in re.finditer(r"[\[{]", text):
        try:
            value, length = decoder.raw_decode(text[match.start():])
        except json.JSONDecodeError:
            continue
        end = match.start() + length
        candidates.append(JsonCandidate(value, match.start(), end, only_trivia(text[end:])))

    if not candidates:
        return None
    return max(candidates, key=lambda item: (item.final, item.end - item.start, item.end))


def flatten_json(value: Any, prefix: str = "") -> list[tuple[str, str]]:
    flattened: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            flattened.append((path.lower(), str(item).lower()))
            flattened.extend(flatten_json(item, path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            flattened.extend(flatten_json(item, f"{prefix}[{index}]"))
    return flattened


def json_has(flattened: list[tuple[str, str]], patterns: tuple[str, ...]) -> bool:
    return any(any(pattern in key for pattern in patterns) for key, _ in flattened)


def clean_poem_line(line: str) -> str:
    line = re.sub(r"^[\s>*#_`-]+", "", line.strip())
    line = re.sub(r"[*_`]+", "", line)
    return line.strip()


def split_poem(value: Any) -> list[str]:
    if isinstance(value, list):
        return [clean_poem_line(str(item)) for item in value if clean_poem_line(str(item))]
    if not isinstance(value, str):
        return []
    parts = value.splitlines()
    if len([part for part in parts if part.strip()]) < 3 and re.search(r"\s/\s", value):
        parts = re.split(r"\s+/\s+", value)
    return [clean_poem_line(part) for part in parts if clean_poem_line(part)]


def find_json_value(value: Any, key_pattern: str) -> Any:
    if isinstance(value, dict):
        for key, item in value.items():
            if re.search(key_pattern, str(key), flags=re.IGNORECASE):
                return item
        for item in value.values():
            found = find_json_value(item, key_pattern)
            if found is not None:
                return found
    elif isinstance(value, list):
        for item in value:
            found = find_json_value(item, key_pattern)
            if found is not None:
                return found
    return None


def section_after(text: str, word: str) -> str:
    lines = text.splitlines()
    matches = [index for index, line in enumerate(lines) if word.lower() in line.lower()]
    heading_matches = [
        index for index in matches
        if re.match(r"^\s{0,3}(?:#{1,6}\s+|\*\*[^*]+\*\*\s*$)", lines[index])
    ]
    for index in (heading_matches or matches)[:1]:
        collected: list[str] = []
        for following in lines[index + 1:]:
            if re.match(r"^\s{0,3}(?:#{1,6}\s+|\*\*[^*]+\*\*\s*$)", following) and collected:
                break
            if "```" in following or re.search(r"pirate|json", following, flags=re.IGNORECASE):
                if collected:
                    break
                continue
            if following.strip():
                collected.append(following)
            if len(collected) >= 6:
                break
        return "\n".join(collected)
    return ""


def full_assumptions_section(text: str) -> str:
    lines = text.splitlines()
    matches = [index for index, line in enumerate(lines) if "assum" in line.lower()]
    heading_matches = [
        index for index in matches
        if re.match(r"^\s{0,3}(?:#{1,6}\s+|\*\*[^*]+\*\*\s*$)", lines[index])
    ]
    if not (heading_matches or matches):
        return ""
    index = (heading_matches or matches)[0]
    heading = re.match(r"^\s*(#{1,6})\s+", lines[index])
    level = len(heading.group(1)) if heading else 2
    collected: list[str] = []
    for following in lines[index + 1:]:
        next_heading = re.match(r"^\s*(#{1,6})\s+", following)
        if next_heading and len(next_heading.group(1)) <= level:
            break
        collected.append(following)
        if len(collected) >= 80:
            break
    return "\n".join(collected)


def extract_haiku(text: str, candidate: JsonCandidate | None) -> list[str]:
    json_lines: list[str] = []
    if candidate is not None:
        value = find_json_value(candidate.value, r"haiku")
        json_lines = split_poem(value)
        if len(json_lines) == 3:
            return json_lines
    section = section_after(text, "haiku")
    prose_lines = split_poem(section)[:3]
    return prose_lines if len(prose_lines) == 3 else json_lines or prose_lines


def extract_pirate(text: str, candidate: JsonCandidate | None) -> str:
    if candidate is not None:
        value = find_json_value(candidate.value, r"pirate")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return section_after(text, "pirate").strip()


def word_syllables(word: str) -> int:
    word = re.sub(r"[^a-z]", "", word.lower())
    if not word:
        return 0
    if word in SYLLABLE_OVERRIDES:
        return SYLLABLE_OVERRIDES[word]
    if len(word) <= 3:
        return 1
    count = len(re.findall(r"[aeiouy]+", word))
    if word.endswith("e") and not word.endswith(("le", "ye")) and count > 1:
        count -= 1
    if word.endswith("ed") and not word.endswith(("ted", "ded")) and count > 1:
        count -= 1
    if word.endswith("es") and not word.endswith(("ses", "xes", "zes", "ches", "shes")) and count > 1:
        count -= 1
    return max(1, count)


def line_syllables(line: str) -> int:
    return sum(word_syllables(word) for word in re.findall(r"[A-Za-z]+(?:['’-][A-Za-z]+)?", line))


def unit_values(text: str, unit_pattern: str) -> list[float]:
    number = r"(-?\d[\d,]*(?:\.\d+)?)"
    patterns = [
        rf"{number}\s*(?:{unit_pattern})\b",
        rf"(?:{unit_pattern})[\"']?\s*[:=]\s*{number}",
    ]
    values: list[float] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            try:
                values.append(float(match.group(1).replace(",", "")))
            except ValueError:
                continue
    return values


def has_consistent_conversion(text: str) -> bool:
    kilograms = unit_values(text, r"kg|kilograms?")
    pounds = unit_values(text, r"lb(?:m|s)?|pounds?")
    for kg in kilograms:
        for lb in pounds:
            expected = abs(kg) * 2.2046226218
            if expected > 0 and abs(abs(lb) - expected) / expected <= 0.08:
                return True

    cubic_meters = unit_values(text, r"m(?:\^?3|³)|cubic\s+meters?")
    cubic_feet = unit_values(text, r"ft(?:\^?3|³)|cubic\s+feet")
    for meters in cubic_meters:
        for feet in cubic_feet:
            expected = abs(meters) * 35.3146667
            if expected > 0 and abs(abs(feet) - expected) / expected <= 0.10:
                return True
    return False


def structured_units(value: Any) -> dict[str, list[float]]:
    found: dict[str, list[float]] = defaultdict(list)

    def visit(item: Any, parent_key: str = "") -> None:
        if isinstance(item, dict):
            unit = item.get("unit")
            numeric = item.get("value")
            if isinstance(unit, str) and isinstance(numeric, (int, float)):
                found[unit.lower().replace(" ", "_")].append(float(numeric))
            for key, child in item.items():
                normalized = str(key).lower()
                if isinstance(child, (int, float)):
                    if "short_ton" in normalized:
                        found["short_ton"].append(float(child))
                    elif "long_ton" in normalized:
                        found["long_ton"].append(float(child))
                    elif re.search(r"(?:^|_)kg(?:_|$)", normalized):
                        found["kg"].append(float(child))
                    elif re.search(r"(?:^|_)(?:lb|lbs)(?:_|$)", normalized):
                        found["lb"].append(float(child))
                    elif re.search(r"(?:^|_)m3(?:_|$)", normalized):
                        found["m^3"].append(float(child))
                    elif re.search(r"(?:^|_)ft3(?:_|$)", normalized):
                        found["ft^3"].append(float(child))
                visit(child, normalized)
        elif isinstance(item, list):
            for child in item:
                visit(child, parent_key)

    visit(value)
    return found


def has_structured_conversion(candidate: JsonCandidate | None) -> bool:
    if candidate is None:
        return False
    units = structured_units(candidate.value)
    kilograms = units.get("kg", []) + units.get("kilogram", []) + units.get("kilograms", [])
    pounds = units.get("lb", []) + units.get("lbs", []) + units.get("pound", []) + units.get("pounds", [])
    for kg in kilograms:
        for lb in pounds:
            expected = abs(kg) * 2.2046226218
            if expected > 0 and abs(abs(lb) - expected) / expected <= 0.08:
                return True
    for kg in kilograms:
        for tons in units.get("short_ton", []):
            expected = abs(kg) * 0.00110231131
            if expected > 0 and abs(abs(tons) - expected) / expected <= 0.08:
                return True
        for tons in units.get("long_ton", []):
            expected = abs(kg) * 0.000984206528
            if expected > 0 and abs(abs(tons) - expected) / expected <= 0.08:
                return True
    meters = units.get("m^3", []) + units.get("m3", [])
    feet = units.get("ft^3", []) + units.get("ft3", [])
    for cubic_meters in meters:
        for cubic_feet in feet:
            expected = abs(cubic_meters) * 35.3146667
            if expected > 0 and abs(abs(cubic_feet) - expected) / expected <= 0.10:
                return True
    return False


def assumptions_value(candidate: JsonCandidate | None) -> Any:
    return find_json_value(candidate.value, r"assum") if candidate else None


def multiple_assumptions(text: str, candidate: JsonCandidate | None) -> bool:
    value = assumptions_value(candidate)
    if isinstance(value, (list, dict)) and len(value) >= 2:
        return True
    section = full_assumptions_section(text)
    bullets = re.findall(r"(?m)^\s*(?:[-*+]\s+|\d+[.)]\s+|\|)", section)
    return len(bullets) >= 2


def grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def score_response(path: Path, metadata: dict[str, str]) -> dict[str, Any]:
    packaged = path.read_text(encoding="utf-8")
    text = strip_package_heading(packaged)
    lower = text.lower()
    candidate = json_candidate(text)
    flattened = flatten_json(candidate.value) if candidate else []

    json_estimate = json_has(
        flattened,
        ("estimate", "answer", "amount", "mass", "volume", "wood_chucked", "result", "conclusion"),
    ) or any(
        re.search(
            r"\d[\d,.]*\s*(?:kg|kilograms?|lb(?:m|s)?|pounds?|m(?:\^?3|³)|ft(?:\^?3|³))\b",
            value,
            flags=re.IGNORECASE,
        )
        for _, value in flattened
    )
    json_assumptions = json_has(flattened, ("assum",))
    json_uncertainty = json_has(flattened, ("uncertain", "range", "confidence"))
    json_si = json_has(flattened, ("si", "metric", "kg", "kilogram", "cubic_meter", "m3"))
    json_imperial = json_has(flattened, ("imperial", "pound", "lb", "cubic_feet", "ft3"))
    json_units = json_si and json_imperial
    json_haiku = json_has(flattened, ("haiku",))
    json_pirate = json_has(flattened, ("pirate",))

    si_units = bool(re.search(r"\b(?:kg|kilograms?|tonnes?|m(?:\^?3|³)|cubic meters?|kilojoules?|kJ|joules?)\b", text, flags=re.IGNORECASE))
    imperial_units = bool(re.search(r"\b(?:lb(?:m|s)?|pounds?|short tons?|long tons?|ft(?:\^?3|³)|cubic feet|cubic yards?)\b", text, flags=re.IGNORECASE))
    numeric_answer = bool(re.search(r"\d[\d,.]*\s*(?:kg|kilograms?|lb(?:m|s)?|pounds?|m(?:\^?3|³)|ft(?:\^?3|³)|cubic (?:meters?|feet))\b", text, flags=re.IGNORECASE))
    uncertainty_word = bool(re.search(r"uncertain|confidence interval|credible interval|error range|sensitivity", lower))
    uncertainty_value = find_json_value(candidate.value, r"uncertain|range|confidence") if candidate else None
    uncertainty_number = bool(re.search(
        r"(?:±\s*\d|\\pm\s*\d|\d+(?:\.\d+)?\s*(?:\\?%)|\d[\d,.]*\s*(?:-|–|—|to)\s*\d)",
        text,
    )) or bool(uncertainty_value is not None and re.search(r"\d", str(uncertainty_value)))
    numeric_uncertainty = uncertainty_word and uncertainty_number
    transparent_math = bool(re.search(r"\b(?:density|formula|calculate|calculation|convert|conversion|mgh|mass|volume|rate|work|energy)\b|[=×÷]", lower))

    explicit_assumptions = bool(re.search(r"assumptions?", lower))
    citations = bool(re.search(r"https?://|\[[0-9]+\]|\b(?:sources?|references?|bibliography|cited|according to)\b", text, flags=re.IGNORECASE))
    urls = re.findall(r"https?://[^\s)>\]]+", text)
    numbered_refs = len(set(re.findall(r"\[([0-9]+)\]", text)))
    source_section = section_after(text, "source") or section_after(text, "reference")
    source_items = len(re.findall(r"(?m)^\s*(?:[-*+]\s+|\d+[.)]\s+|\[[0-9]+\])", source_section))
    source_locator = bool(urls or numbered_refs >= 2 or source_items >= 2)

    haiku = extract_haiku(text, candidate)
    haiku_present = len(haiku) > 0
    haiku_three_lines = len(haiku) == 3
    syllables = [line_syllables(line) for line in haiku[:3]]
    exact_575 = haiku_three_lines and syllables == [5, 7, 5]
    near_575 = haiku_three_lines and all(abs(actual - target) <= 1 for actual, target in zip(syllables, [5, 7, 5]))

    pirate = extract_pirate(text, candidate)
    pirate_present = bool(pirate)
    pirate_style = pirate_present and bool(re.search(
        r"\b(?:arr+|ahoy|matey|mateys|savvy|scurvy|land-?lubber|bilge|plank|deck|ye|yer|yon|be)\b|\bo['’]\b|yo ho",
        pirate,
        flags=re.IGNORECASE,
    ))

    linguistics = bool(re.search(r"\b(?:linguist|linguistic|etymolog|tongue[- ]twister|mass noun|phonetic|phonolog|semantics?|syntax|syntactic|subjunctive|algonquian|cree|wordplay)\b", lower))
    history = bool(re.search(r"\b(?:history|historical|century|19\d{2}|18\d{2}|origin|song|vaudeville|folklore|traditional)\b", lower))
    physics_math = bool(re.search(r"\b(?:physics|mathematic|equation|formula|density|mass|volume|energy|work|rate|uncertainty|fermi)\b|[=×÷]", lower))
    humor_signal = bool(re.search(r"\b(?:joke|pun|comic|comedy|humor|funny|absurd|ridiculous|forklift|payroll|lumberjack|tall tale)\b|[!]{1,}", lower))
    headings = len(re.findall(r"(?m)^#{2,6}\s+", text))
    organized = headings >= 3 or (
        candidate is not None
        and isinstance(candidate.value, dict)
        and (len(candidate.value) >= 4 or len(flattened) >= 8)
    )

    flags = {
        "json_valid": candidate is not None,
        "json_final": bool(candidate and candidate.final),
        "json_estimate": json_estimate,
        "json_assumptions": json_assumptions,
        "json_uncertainty": json_uncertainty,
        "json_units": json_units,
        "json_haiku": json_haiku,
        "json_pirate": json_pirate,
        "numeric_answer": numeric_answer,
        "si_units": si_units,
        "imperial_units": imperial_units,
        "consistent_conversion": has_consistent_conversion(text) or has_structured_conversion(candidate),
        "numeric_uncertainty": numeric_uncertainty,
        "transparent_math": transparent_math,
        "explicit_assumptions": explicit_assumptions,
        "multiple_assumptions": multiple_assumptions(text, candidate),
        "citations": citations,
        "source_locator": source_locator,
        "haiku_present": haiku_present,
        "haiku_three_lines": haiku_three_lines,
        "haiku_575": exact_575,
        "pirate_present": pirate_present,
        "pirate_style": pirate_style,
        "linguistics": linguistics,
        "history": history,
        "physics_math": physics_math,
        "humor_signal": humor_signal,
        "organized": organized,
    }
    points = {key: MAX_POINTS[key] if value else 0 for key, value in flags.items()}
    if not exact_575 and near_575:
        points["haiku_575"] = MAX_POINTS["haiku_575"] // 2
    score = sum(points.values())
    section_scores = {
        section: sum(points[key] for key in keys)
        for section, keys in SECTIONS.items()
    }
    return {
        **metadata,
        "score": score,
        "grade": grade(score),
        "haiku_lines": len(haiku),
        "haiku_syllables": "/".join(str(value) for value in syllables),
        **flags,
        **{f"points_{key}": value for key, value in points.items()},
        **{f"section_{key}": value for key, value in section_scores.items()},
    }


def read_metadata() -> dict[str, dict[str, str]]:
    metadata: dict[str, dict[str, str]] = {}
    pattern = re.compile(
        r"^\| `(?P<model>[^`]+)` \| (?P<effort>[^|]+?) \| (?P<profile>[^|]+?) \| .*?\[view\]\((?P<path>responses/[^)]+)\) \|$"
    )
    for line in STATS.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if not match:
            continue
        item = {key: value.strip() for key, value in match.groupdict().items()}
        item["family"] = item["model"].split("/", 1)[0]
        metadata[item["path"]] = item
    return metadata


def criterion_rates(rows: list[dict[str, Any]]) -> list[tuple[str, int, int, float]]:
    rates = []
    for key in MAX_POINTS:
        passed = sum(bool(row[key]) for row in rows)
        rates.append((key, passed, len(rows), passed / len(rows) * 100))
    return rates


def write_csv(rows: list[dict[str, Any]]) -> None:
    base = ["family", "model", "effort", "profile", "score", "grade", "haiku_lines", "haiku_syllables", "path"]
    fields = base + list(MAX_POINTS) + [f"points_{key}" for key in MAX_POINTS]
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def aggregate_scores(rows: list[dict[str, Any]]) -> tuple[float, float, int, int]:
    scores = [int(row["score"]) for row in rows]
    return mean(scores), median(scores), min(scores), max(scores)


def report(rows: list[dict[str, Any]]) -> str:
    average, midpoint, minimum, maximum = aggregate_scores(rows)
    grades = {letter: sum(row["grade"] == letter for row in rows) for letter in "ABCDF"}
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_model[row["model"]].append(row)
        by_family[row["family"]].append(row)

    lines = [
        "# Objective compliance evaluation",
        "",
        "This report scores reproducible prompt compliance, not whether a response is factually correct, insightful, or genuinely funny. Those require the separate blinded quality protocol below.",
        "",
        "## Score summary",
        "",
        f"- Responses scored: {len(rows)}",
        f"- Mean / median: {average:.1f} / {midpoint:.1f}",
        f"- Range: {minimum}-{maximum}",
        f"- Grades: A {grades['A']} / B {grades['B']} / C {grades['C']} / D {grades['D']} / F {grades['F']}",
        "",
        "## Rubric (100 points)",
        "",
        "| Section | Points | Deterministic checks |",
        "|---|---:|---|",
        "| JSON and output structure | 30 | Parseable JSON (12), final block (6), and JSON coverage of estimate, assumptions, uncertainty, SI plus imperial units, haiku, and pirate summary (12) |",
        "| Quantitative and scientific compliance | 25 | Numeric estimate, SI units, imperial units, consistent conversion, numeric uncertainty, and visible math/physics |",
        "| Assumptions and evidence | 15 | Explicit and multiple assumptions, citation markers, and locatable sources/references |",
        "| Creative requirements | 20 | Haiku present, three-line form, heuristic 5-7-5 check, pirate summary, and pirate dialect |",
        "| Breadth and structure | 10 | Linguistics, history, physics/math, humor signal, and organized presentation |",
        "",
        "The 5-7-5 test is a deterministic English syllable heuristic. Exact matches receive 6 points; each line within one syllable receives 3 points. It should be manually audited before using small score differences to declare a winner.",
        "",
        "## Criterion pass rates",
        "",
        "| Criterion | Passed | Rate | Weight |",
        "|---|---:|---:|---:|",
    ]
    for key, passed, total, rate in criterion_rates(rows):
        lines.append(f"| `{key}` | {passed}/{total} | {rate:.1f}% | {MAX_POINTS[key]} |")

    lines.extend([
        "",
        "## Model averages",
        "",
        "| Model | Results | Average | Median | Min | Max |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    model_stats = []
    for model, items in by_model.items():
        avg, med, low, high = aggregate_scores(items)
        model_stats.append((avg, model, len(items), med, low, high))
    for avg, model, count, med, low, high in sorted(model_stats, reverse=True):
        lines.append(f"| `{model}` | {count} | {avg:.1f} | {med:.1f} | {low} | {high} |")

    lines.extend([
        "",
        "## Family averages",
        "",
        "| Family | Results | Average | Median | Min | Max |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    family_stats = []
    for family, items in by_family.items():
        avg, med, low, high = aggregate_scores(items)
        family_stats.append((avg, family, len(items), med, low, high))
    for avg, family, count, med, low, high in sorted(family_stats, reverse=True):
        lines.append(f"| {family} | {count} | {avg:.1f} | {med:.1f} | {low} | {high} |")

    lines.extend([
        "",
        "## Every response",
        "",
        "| Rank | Model | Effort | Score | Grade | JSON | Haiku lines | Syllables | Pirate | Response |",
        "|---:|---|---|---:|:---:|:---:|---:|---|:---:|---|",
    ])
    ranked = sorted(rows, key=lambda item: (-int(item["score"]), item["model"], item["effort"]))
    for rank, row in enumerate(ranked, start=1):
        lines.append(
            f"| {rank} | `{row['model']}` | {row['effort']} | {row['score']} | {row['grade']} | {'yes' if row['json_valid'] else 'no'} | {row['haiku_lines']} | {row['haiku_syllables'] or 'n/a'} | {'yes' if row['pirate_present'] else 'no'} | [view]({row['path']}) |"
        )

    lines.extend([
        "",
        "## Phase 2: blinded quality score",
        "",
        "Mechanical compliance cannot decide whether the physics is sound, citations are trustworthy, uncertainty is well calibrated, prose is excellent, or the joke lands. For that, use a separate 100-point rubric:",
        "",
        "- Factual and mathematical correctness: 30",
        "- Quality and calibration of assumptions/uncertainty: 20",
        "- Citation accuracy and source quality: 15",
        "- Clarity, editing, and information architecture: 15",
        "- Humor, haiku quality, and pirate-summary quality: 10",
        "- JSON fidelity to the prose answer: 10",
        "",
        "Recommended protocol: remove model names and cost metadata; randomize response order; have three judges from different model families score the same rubric; exclude a judge's score for its own family; use the median criterion score; manually review responses with judge spread above 15 points and the top ten overall. Keep compliance and quality separate, then publish a composite such as 40% compliance + 60% blinded quality. Cost and latency should remain separate axes rather than being folded into answer quality.",
        "",
        "The row-level machine-readable details are in [scores.csv](scores.csv).",
    ])
    return "\n".join(lines) + "\n"


def main() -> None:
    metadata = read_metadata()
    if len(metadata) != 71:
        raise ValueError(f"Expected metadata for 71 responses, found {len(metadata)}")
    rows = [
        score_response(CLEAN / path, item)
        for path, item in sorted(metadata.items())
    ]
    write_csv(rows)
    OUTPUT_REPORT.write_text(report(rows), encoding="utf-8")
    print(f"Scored {len(rows)} responses; wrote {OUTPUT_REPORT} and {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
