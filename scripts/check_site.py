#!/usr/bin/env python3
"""Verify that local links required by the static site resolve."""

from html.parser import HTMLParser
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
    parser = LinkParser()
    parser.feed((SITE / "index.html").read_text(encoding="utf-8"))
    missing = [f"{link} -> {path}" for link in parser.links if (path := resolve(link)) and not path.exists()]
    if missing:
        raise SystemExit("Missing site targets:\n" + "\n".join(missing))
    response_count = len(list((ROOT / "results/responses").glob("*/*/*.md")))
    if response_count != 71:
        raise SystemExit(f"Expected 71 published responses, found {response_count}")
    print(f"Verified {len(parser.links)} links and {response_count} published responses")


if __name__ == "__main__":
    main()
