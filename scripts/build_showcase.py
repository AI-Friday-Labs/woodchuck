#!/usr/bin/env python3
"""Build the public haiku and pirate carousel data from published responses."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import score_results  # noqa: E402


RESULTS = ROOT / "results"
OUTPUT = RESULTS / "showcase.json"


def clean_pirate(value: str, limit: int = 480) -> str:
    """Flatten light Markdown while preserving the model's visible wording."""
    text = re.sub(r"```(?:json)?|```", " ", value, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s{0,3}#{1,6}\s+", "", text)
    text = re.sub(r"[*_`]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    shortened = text[: limit + 1].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return shortened + "…"


def load_scores() -> dict[tuple[str, str], int]:
    with (RESULTS / "scores.csv").open(encoding="utf-8", newline="") as handle:
        return {
            (row["model"], row["effort"]): int(row["score"])
            for row in csv.DictReader(handle)
        }


def build() -> list[dict[str, object]]:
    scores = load_scores()
    items: list[dict[str, object]] = []
    for relative, metadata in sorted(score_results.read_metadata().items()):
        packaged = (RESULTS / relative).read_text(encoding="utf-8")
        text = score_results.strip_package_heading(packaged)
        candidate = score_results.json_candidate(text)
        haiku = score_results.extract_haiku(text, candidate)
        pirate = clean_pirate(score_results.extract_pirate(text, candidate))
        if len(haiku) != 3 or not pirate:
            raise ValueError(f"Missing showcase content for {metadata['model']} {metadata['effort']}")
        items.append(
            {
                "model": metadata["model"],
                "effort": metadata["effort"],
                "score": scores[(metadata["model"], metadata["effort"])],
                "path": relative,
                "haiku": haiku,
                "pirate": pirate,
            }
        )
    if len(items) != 71:
        raise ValueError(f"Expected 71 showcase items, found {len(items)}")
    return items


def main() -> None:
    items = build()
    OUTPUT.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT} with {len(items)} haiku and pirate summaries")


if __name__ == "__main__":
    main()
