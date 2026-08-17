"""Validate the static research publication before release."""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "website"
PUBLIC_PAGES = {
    "index.html",
    "evidence.html",
    "methods.html",
    "reproducibility.html",
    "sources.html",
    "cite.html",
}
VERIFIED_DOI = "10.5281/zenodo.21955380"
DOI_URL = f"https://doi.org/{VERIFIED_DOI}"
STYLESHEET_HREF = "styles.css?v=7"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.ids: set[str] = set()
        self.canonicals: list[str] = []
        self.h1_count = 0
        self.stylesheets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if data.get("id"):
            self.ids.add(data["id"] or "")
        if tag == "a" and data.get("href"):
            self.hrefs.append(data["href"] or "")
        if tag == "h1":
            self.h1_count += 1
        if tag == "link" and data.get("rel") == "canonical" and data.get("href"):
            self.canonicals.append(data["href"] or "")
        if tag == "link" and data.get("rel") == "stylesheet" and data.get("href"):
            self.stylesheets.append(data["href"] or "")


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def main() -> int:
    errors: list[str] = []
    parsed = {name: parse_page(WEBSITE / name) for name in PUBLIC_PAGES}

    for name, page in parsed.items():
        if page.h1_count != 1:
            errors.append(f"{name}: expected one h1, found {page.h1_count}")
        if len(page.canonicals) != 1:
            errors.append(f"{name}: expected one canonical URL")
        if page.stylesheets != [STYLESHEET_HREF]:
            errors.append(
                f"{name}: expected stylesheet {STYLESHEET_HREF}, "
                f"found {page.stylesheets or 'none'}"
            )

        for href in page.hrefs:
            parts = urlsplit(href)
            if parts.scheme or href.startswith(("mailto:", "tel:")):
                continue
            target_name = parts.path or name
            target = (WEBSITE / target_name).resolve()
            if WEBSITE.resolve() not in target.parents and target != WEBSITE.resolve():
                errors.append(f"{name}: local link escapes website directory: {href}")
                continue
            if not target.exists():
                errors.append(f"{name}: missing local target: {href}")
                continue
            if parts.fragment and target.suffix.lower() == ".html":
                target_page = parsed.get(target.name) or parse_page(target)
                if parts.fragment not in target_page.ids:
                    errors.append(f"{name}: missing fragment #{parts.fragment} in {target.name}")

    sitemap = ET.parse(WEBSITE / "sitemap.xml")
    sitemap_urls = {node.text or "" for node in sitemap.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")}
    for name in PUBLIC_PAGES:
        suffix = "" if name == "index.html" else name
        expected = "https://sunrunjie.github.io/AI-Driven-Transformation-of-Music-Information-Ecosystems/" + suffix
        if expected not in sitemap_urls:
            errors.append(f"sitemap.xml: missing {name}")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if version != "1.0.0":
        errors.append(f"VERSION: expected 1.0.0, found {version}")
    config_text = (ROOT / "src" / "config.py").read_text(encoding="utf-8")
    if f'"version": "{version}"' not in config_text:
        errors.append("src/config.py: report version does not match VERSION")

    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    for field in ("cff-version: 1.2.0", "version: 1.0.0", "date-released: 2026-08-16", "family-names: Sun", "given-names: RunJie"):
        if field not in citation:
            errors.append(f"CITATION.cff: missing {field}")

    zenodo = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    for field in ("title", "description", "creators", "license", "version", "publication_date"):
        if field not in zenodo:
            errors.append(f".zenodo.json: missing {field}")
    if zenodo.get("version") != version:
        errors.append(".zenodo.json: version does not match VERSION")
    if f"doi: {VERIFIED_DOI}" not in citation or DOI_URL not in citation:
        errors.append("CITATION.cff: verified Zenodo DOI is missing")
    if "doi" in zenodo:
        errors.append(".zenodo.json: do not declare the deposit's own minted DOI as a pre-existing DOI")

    for relative_path in ("README.md", "website/index.html", "website/cite.html"):
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        if DOI_URL not in text:
            errors.append(f"{relative_path}: verified Zenodo DOI URL is missing")

    pdf = WEBSITE / "assets" / "research-brief-v1.0.0.pdf"
    if not pdf.exists() or pdf.stat().st_size < 100_000:
        errors.append("versioned research brief PDF is missing or unexpectedly small")

    lock_text = (ROOT / "requirements-lock.txt").read_text(encoding="utf-8")
    if "--generate-hashes" not in lock_text.splitlines()[1] or "--hash=sha256:" not in lock_text:
        errors.append("requirements-lock.txt is not hash-locked")

    if errors:
        print("Publication check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Publication check passed: {len(PUBLIC_PAGES)} pages, version {version}, PDF and hash-locked environment present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
