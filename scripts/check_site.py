#!/usr/bin/env python3
"""Verify that local links required by the static site resolve."""

from html.parser import HTMLParser
from html import unescape
import json
import re
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attribute = "href" if tag in {"a", "link"} else "src" if tag == "script" else None
        if not attribute:
            return
        values = dict(attrs)
        if values.get(attribute):
            self.links.append(values[attribute] or "")


def resolve(link: str) -> Path | None:
    parsed = urlparse(link)
    if parsed.scheme or parsed.netloc or link.startswith("#"):
        return None
    path = parsed.path
    if path.startswith("results/"):
        return ROOT / path
    return SITE / path


def main() -> None:
    html = (SITE / "index.html").read_text(encoding="utf-8")
    parser = LinkParser()
    parser.feed(html)
    missing = [f"{link} -> {path}" for link in parser.links if (path := resolve(link)) and not path.exists()]
    if missing:
        raise SystemExit("Missing site targets:\n" + "\n".join(missing))
    response_count = len(list((ROOT / "results/responses").glob("*/*/*.md")))
    if response_count != 71:
        raise SystemExit(f"Expected 71 published responses, found {response_count}")
    showcase = json.loads((ROOT / "results/showcase.json").read_text(encoding="utf-8"))
    if len(showcase) != 71 or any(len(item["haiku"]) != 3 or not item["pirate"] for item in showcase):
        raise SystemExit("Showcase data must contain 71 complete haiku and pirate summaries")
    prompt_match = re.search(r'<figure class="prompt-card">.*?<blockquote>(.*?)</blockquote>', html, re.DOTALL)
    visible_prompt = unescape(prompt_match.group(1)).strip() if prompt_match else ""
    source_prompt = (ROOT / "prompts/woodchuck.txt").read_text(encoding="utf-8").strip()
    if visible_prompt != source_prompt:
        raise SystemExit("The prominent site prompt must exactly match prompts/woodchuck.txt")
    print(f"Verified {len(parser.links)} links, exact prompt, {response_count} responses, and both 71-item carousels")


if __name__ == "__main__":
    main()
