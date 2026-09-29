"""Offline structural checks for the generated guide and source metadata."""

from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class GuideParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []
        self.images = []
        self.remote_assets = []
        self.articles = []
        self.inputs_without_labels = []
        self.script_sources = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"])
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])
        if tag == "img":
            self.images.append(values)
        if tag == "article":
            self.articles.append(values.get("id"))
        if tag in {"script", "img", "iframe", "link"}:
            address = values.get("src") or values.get("href") or ""
            if address.startswith(("http:", "https:", "//")):
                self.remote_assets.append(address)
        if tag == "script" and "src" in values:
            self.script_sources.append(values["src"])


def check() -> dict:
    chapters = json.loads((ROOT / "content/chapters.json").read_text(encoding="utf-8"))
    sources = json.loads((ROOT / "content/sources.json").read_text(encoding="utf-8"))["sources"]
    capabilities = json.loads((ROOT / "content/capabilities.json").read_text(encoding="utf-8"))
    ids = {chapter["id"] for chapter in chapters}
    source_ids = {source["id"] for source in sources}
    if len(ids) != len(chapters) or len(source_ids) != len(sources):
        raise ValueError("Duplicate chapter or source IDs.")
    labs = [chapter for chapter in chapters if chapter["track"] != "reference"]
    core_minutes = sum(c["minutes"] for c in labs if c["track"] == "core")
    duration = f"{core_minutes // 60}시간 {core_minutes % 60}분"
    for path in ("README.md", "docs/00-start.md", "docs/instructor.md"):
        if duration not in (ROOT / path).read_text(encoding="utf-8"):
            raise ValueError(f"{path}: course duration differs from chapter metadata")
    if [chapter["id"] for chapter in labs] != [f"l{i:02}" for i in range(25)]:
        raise ValueError("Expected contiguous L00-L24 labs.")
    for chapter in chapters:
        if not set(chapter["sources"]) <= source_ids:
            raise ValueError(f"{chapter['id']}: unresolved official source")
        if chapter["track"] != "reference":
            text = (ROOT / chapter["file"]).read_text(encoding="utf-8")
            for heading in ("목표", "준비", "실행", "성공 기준", "막혔을 때", "정리"):
                if not re.search(rf"^## {heading}$", text, re.M):
                    raise ValueError(f"{chapter['id']}: missing {heading} section")
            if len(text) < 1000:
                raise ValueError(f"{chapter['id']}: unexpectedly thin lab")
    for item in capabilities:
        if item["lab"] not in ids or item["source"] not in source_ids:
            raise ValueError(f"Unresolved capability: {item['name']}")
        if item["mode"] not in {"직접 실습", "조건부 실습", "설계", "참고"}:
            raise ValueError("Coverage depth must be explicit.")
    for source in sources:
        address = urlparse(source["url"])
        if address.scheme != "https" or address.hostname != "learn.microsoft.com":
            raise ValueError(f"Unexpected official source URL: {source['id']}")
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    parser = GuideParser()
    parser.feed(html)
    duplicates = [item for item, count in Counter(parser.ids).items() if count > 1]
    if duplicates:
        raise ValueError(f"Duplicate HTML IDs: {duplicates}")
    if set(parser.articles) != ids:
        raise ValueError("Generated article set differs from chapter manifest.")
    if parser.remote_assets:
        raise ValueError(f"Guide must not require remote assets: {parser.remote_assets}")
    for address in parser.links:
        parsed = urlparse(address)
        if parsed.scheme or parsed.netloc:
            continue
        if not parsed.path:
            if parsed.fragment and unquote(parsed.fragment) not in parser.ids:
                raise ValueError(f"Broken internal anchor: {address}")
        elif not (ROOT / unquote(parsed.path)).is_file():
            raise ValueError(f"Missing linked file: {address}")
    for image in parser.images:
        if not image.get("alt"):
            raise ValueError("Image missing alt text.")
        if not (ROOT / image["src"]).is_file():
            raise ValueError(f"Missing image: {image['src']}")
    for path in (ROOT / "assets").glob("*.svg"):
        ET.parse(path)
    for needle in ("2026-12-01", "부분 GA", "클라우드", "2.7.0", "1.13.1"):
        if needle not in html:
            raise ValueError(f"Missing key caveat: {needle}")
    book = (ROOT / "GUIDE.ko.md").read_text(encoding="utf-8")
    for chapter_id in ids:
        if f'<a id="{chapter_id}"></a>' not in book:
            raise ValueError("Markdown book missing an anchor.")
    result = {
        "pages": len(chapters), "labs": len(labs),
        "coverage_rows": len(capabilities), "official_sources": len(sources),
        "core_minutes": core_minutes,
        "duplicate_ids": 0, "broken_local_links": 0, "remote_asset_dependencies": 0,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    check()
