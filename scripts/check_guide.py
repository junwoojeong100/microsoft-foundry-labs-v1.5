"""Offline structural checks for the generated guide and source metadata."""

from collections import Counter
import argparse
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlparse
import xml.etree.ElementTree as ET

from build_guide import RELEASE, load_content, load_portal_captures

ROOT = Path(__file__).resolve().parents[1]
LAB_HEADINGS = {
    "ko": ("목표", "개념과 실습 지도", "준비", "실행", "성공 기준", "막혔을 때", "정리"),
    "en": ("Objectives", "Concepts and lab map", "Prerequisites", "Steps", "Success criteria", "Troubleshooting", "Cleanup"),
}
CONCEPT_LABELS = {
    "ko": ("경험할 기능", "무엇이며 왜 중요한가요?", "어떻게 사용하나요?", "어디서 실행하나요?"),
    "en": ("What you will try:", "What is it, and why does it matter?", "How do you use it?", "Where do you run it?"),
}
BRIEF_LABELS = {
    "ko": ("진행 방식:", "먼저 할 일:", "확인할 결과:"),
    "en": ("Format:", "Start here:", "What to check:"),
}
PRACTICE_LABS = {"l15", "l15-collaboration", "l21", "l22"}
PRACTICE_LABELS = {
    "ko": ("직접 해보기", "한 가지 바꾸기", "결과 설명하기"),
    "en": ("Try it", "Change one thing", "Explain the result"),
}


def command_coverage(text: str, source: str, language: str = "ko") -> dict:
    blocks = commands = 0
    for block in re.finditer(r"^```(bash|powershell)\n(.*?)^```[^\S\n]*(?:\n|$)", text, re.M | re.S):
        lines = [line.strip() for line in block[2].splitlines() if line.strip() and not line.lstrip().startswith("#")]
        if lines and lines[-1].endswith("\\"):
            raise ValueError(f"{source}: unfinished command continuation")
        count = sum(not line.endswith("\\") for line in lines)
        note = re.match(
            r'\s*<div class="command-explanation" markdown="1">(.*?)\n</div>',
            text[block.end():], re.S,
        )
        label = {"ko": "명령 해설", "en": "Command walkthrough"}[language]
        if not count or not note or label not in note[1]:
            raise ValueError(f"{source}: every shell block needs an adjacent command explanation")
        rows = re.findall(r"^\|\s*(\d+)\.\s*([^|]+)\|([^|]+)\|([^|]+)\|\s*$", note[1], re.M)
        if [int(row[0]) for row in rows] != list(range(1, count + 1)):
            raise ValueError(f"{source}: each logical command needs its own ordered explanation row")
        if any(not cell.strip() for row in rows for cell in row[1:]):
            raise ValueError(f"{source}: empty command explanation")
        blocks += 1
        commands += count
    return {"blocks": blocks, "commands": commands}


def check_portal_captures(parser, language) -> int:
    captures = load_portal_captures(language)
    paths = {item["path"] for item in captures}
    used = {image["src"] for image in parser.images if image["src"].startswith("assets/portal/")}
    if paths != used:
        raise ValueError(f"{language}: portal capture manifest and guide images differ.")
    return len(paths)


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
        self.language = None

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "html":
            self.language = values.get("lang")
        if values.get("id"):
            self.ids.append(values["id"])
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])
        if tag == "img":
            self.images.append(values)
        if tag == "article":
            self.articles.append(values.get("id"))
        if tag in {"script", "img", "iframe", "link"} and not (
            tag == "link" and values.get("rel") in {"alternate", "canonical"}
        ):
            address = values.get("src") or values.get("href") or ""
            if address.startswith(("http:", "https:", "//")):
                self.remote_assets.append(address)
        if tag == "script" and "src" in values:
            self.script_sources.append(values["src"])


def check_language(language) -> dict:
    chapters, source_data, capabilities = load_content(language)
    sources = source_data["sources"]
    edition = RELEASE["languages"][language]
    ids = {chapter["id"] for chapter in chapters}
    source_ids = {source["id"] for source in sources}
    if len(ids) != len(chapters) or len(source_ids) != len(sources):
        raise ValueError("Duplicate chapter or source IDs.")
    labs = [chapter for chapter in chapters if chapter["track"] != "reference"]
    shell_blocks = shell_commands = 0
    core_minutes = sum(c["minutes"] for c in labs if c["track"] == "core")
    duration = (
        f"{core_minutes // 60}시간 {core_minutes % 60}분" if language == "ko"
        else f"{core_minutes // 60} hours {core_minutes % 60} minutes"
    )
    docs = "docs" if language == "ko" else "docs/en"
    for path in (edition["readme"], f"{docs}/00-start.md", f"{docs}/instructor.md"):
        if duration not in (ROOT / path).read_text(encoding="utf-8"):
            raise ValueError(f"{path}: course duration differs from chapter metadata")
    expected_numbers = [f"{number:02}" for number in range(20)]
    if (
        [chapter["number"] for chapter in labs] != expected_numbers
        or [chapter["track"] for chapter in labs] != ["core"] * 11 + ["advanced"] * 8 + ["wrapup"]
        or labs[-1]["id"] != "l12"
    ):
        raise ValueError("Expected continuous L00-L19: 11 core, 8 advanced, then the shared wrap-up.")
    for chapter in chapters:
        if not set(chapter["sources"]) <= source_ids:
            raise ValueError(f"{chapter['id']}: unresolved official source")
        if chapter["track"] != "reference":
            text = (ROOT / chapter["file"]).read_text(encoding="utf-8")
            for heading in LAB_HEADINGS[language]:
                if not re.search(rf"^## {re.escape(heading)}$", text, re.M):
                    raise ValueError(f"{chapter['id']}: missing {heading} section")
            if len(text) < 1000:
                raise ValueError(f"{chapter['id']}: unexpectedly thin lab")
            for label in CONCEPT_LABELS[language]:
                if f"**{label}" not in text:
                    raise ValueError(f"{chapter['id']}: missing learner explanation: {label}")
            brief = re.search(r'<div class="lab-brief" markdown="1">(.*?)</div>', text, re.S)
            if (
                text.count('class="lab-brief"') != 1 or not brief
                or any(f"**{label}" not in brief[1] for label in BRIEF_LABELS[language])
                or brief.start() > text.index("## " + LAB_HEADINGS[language][1])
            ):
                raise ValueError(f"{chapter['id']}: needs a beginner start card before the concept map")
            if chapter["id"] in PRACTICE_LABS and (
                text.count('class="practice-block"') != 1
                or any("**" + label not in text for label in PRACTICE_LABELS[language])
            ):
                raise ValueError(f"{chapter['id']}: needs a try/change/explain exercise")
            coverage = command_coverage(text, chapter["file"], language)
            shell_blocks += coverage["blocks"]
            shell_commands += coverage["commands"]
    if shell_blocks != edition["shell_blocks"] or shell_commands != edition["commands"]:
        raise ValueError(
            f"{language}: expected {edition['shell_blocks']} shell blocks / {edition['commands']} commands; "
            f"found {shell_blocks} / {shell_commands}."
        )
    for item in capabilities:
        if item["lab"] not in ids or item["source"] not in source_ids:
            raise ValueError(f"Unresolved capability: {item['name']}")
        if item["mode"] not in {"직접 실습", "조건부 실습", "설계", "참고"}:
            raise ValueError("Coverage depth must be explicit.")
    for source in sources:
        address = urlparse(source["url"])
        if address.scheme != "https" or address.hostname != "learn.microsoft.com":
            raise ValueError(f"Unexpected official source URL: {source['id']}")
    html = (ROOT / edition["html"]).read_text(encoding="utf-8")
    parser = GuideParser()
    parser.feed(html)
    if parser.language != language:
        raise ValueError(f"{edition['html']}: incorrect HTML language metadata")
    duplicates = [item for item, count in Counter(parser.ids).items() if count > 1]
    if duplicates:
        raise ValueError(f"Duplicate HTML IDs: {duplicates}")
    if parser.articles != [chapter["id"] for chapter in chapters]:
        raise ValueError("Generated article order differs from chapter manifest.")
    if parser.remote_assets:
        raise ValueError(f"Guide must not require remote assets: {parser.remote_assets}")
    for path in (edition["receipt_html"],):
        if path not in parser.links:
            raise ValueError(f"{language}: missing localized evidence/receipt link: {path}")
    for address in parser.links:
        if address.startswith(("validation/", "results/")):
            raise ValueError("Execution records must remain outside the reader.")
        parsed = urlparse(address)
        if parsed.scheme or parsed.netloc:
            continue
        if not parsed.path:
            if parsed.fragment and unquote(parsed.fragment) not in parser.ids:
                raise ValueError(f"Broken internal anchor: {address}")
        elif not (ROOT / unquote(parsed.path)).is_file():
            raise ValueError(f"Missing linked file: {address}")
        elif parsed.fragment and parsed.path.endswith(".html"):
            linked = GuideParser()
            linked.feed((ROOT / unquote(parsed.path)).read_text(encoding="utf-8"))
            if unquote(parsed.fragment) not in linked.ids:
                raise ValueError(f"Broken cross-language anchor: {address}")
    for image in parser.images:
        if not image.get("alt"):
            raise ValueError("Image missing alt text.")
        if not (ROOT / image["src"]).is_file():
            raise ValueError(f"Missing image: {image['src']}")
    portal_captures = check_portal_captures(parser, language)
    for path in (ROOT / "assets").glob("*.svg"):
        ET.parse(path)
    caveats = ("부분 GA", "클라우드") if language == "ko" else ("Partially GA", "cloud")
    for needle in ("2026-12-01", "2.7.0", "1.13.1", *caveats):
        if needle not in html:
            raise ValueError(f"Missing key caveat: {needle}")
    book = (ROOT / edition["markdown"]).read_text(encoding="utf-8")
    for address in (RELEASE["site_url"] + edition["receipt_html"],):
        if f"]({address})" not in book:
            raise ValueError(f"{language}: Markdown book missing localized evidence/receipt link: {address}")
    book_paths = set()
    for address in re.findall(r"\]\(([^)\s]+)\)", book):
        parsed = urlparse(address)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        target = (ROOT / Path(edition["markdown"]).parent / unquote(parsed.path)).resolve()
        if not target.is_relative_to(ROOT) or not target.is_file():
            raise ValueError(f"{language}: broken portable Markdown link: {address}")
        book_paths.add(target.relative_to(ROOT).as_posix())
    for chapter_id in ids:
        if f'<a id="{chapter_id}"></a>' not in book:
            raise ValueError("Markdown book missing an anchor.")
    result = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Offline guide structure, command coverage and screenshot provenance; no Azure execution.",
        "guide_sha256": hashlib.sha256(html.encode("utf-8")).hexdigest(),
        "language": language, "html": edition["html"], "markdown": edition["markdown"],
        "pages": len(chapters), "labs": len(labs),
        "coverage_rows": len(capabilities), "official_sources": len(sources),
        "core_minutes": core_minutes,
        "advanced_minutes": sum(c["minutes"] for c in labs if c["track"] == "advanced"),
        "wrapup_minutes": sum(c["minutes"] for c in labs if c["track"] == "wrapup"),
        "duplicate_ids": 0, "broken_local_links": 0, "remote_asset_dependencies": 0,
        "markdown_local_paths_checked": len(book_paths),
        "modules_with_concept_maps": len(labs),
        "modules_with_beginner_start_cards": len(labs),
        "modules_with_guided_experiments": len(PRACTICE_LABS),
        "explained_shell_blocks": shell_blocks, "explained_commands": shell_commands,
        "portal_screenshots": portal_captures,
        "portal_manifest": edition["portal_manifest"],
        "portal_capture_paths": sorted({
            image["src"] for image in parser.images if image["src"].startswith("assets/portal/")
        }),
    }
    return result


def check() -> dict:
    languages = {language: check_language(language) for language in RELEASE["languages"]}
    for key, expected in {
        "pages": 25, "labs": 20, "coverage_rows": 68, "official_sources": 80,
        "core_minutes": 285, "advanced_minutes": 335, "wrapup_minutes": 10,
    }.items():
        if {result[key] for result in languages.values()} != {expected}:
            raise ValueError(f"Language editions must each have {expected} {key}.")
    capture_names = {
        language: {Path(path).name for path in result["portal_capture_paths"]}
        for language, result in languages.items()
    }
    if capture_names["en"] != capture_names["ko"] | {"18-resource-group.png"}:
        raise ValueError("English captures must cover the active Korean screens plus the English resource group.")
    result = {
        "scope": "Offline bilingual documentation checks only; no Azure execution.",
        "default_language": RELEASE["default_language"],
        "languages": languages,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-dir", type=Path, default=Path(RELEASE["documentation_validation"]))
    args = parser.parse_args()
    report_dir = (ROOT / args.report_dir).resolve()
    if not report_dir.is_relative_to(ROOT / "results") or report_dir == ROOT / "results":
        raise ValueError("Reports must be inside private results/.")
    report = check()
    target = report_dir / "structure.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
