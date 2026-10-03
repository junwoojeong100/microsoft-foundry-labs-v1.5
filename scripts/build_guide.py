"""Build the offline reader and a portable Markdown book from the same sources."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
import hashlib
from html import escape
import json
from pathlib import Path
import posixpath
import re
from urllib.parse import unquote, urlparse, urlunparse

import markdown
from markdown.extensions.toc import slugify_unicode

ROOT = Path(__file__).resolve().parents[1]
RELEASE = json.loads((ROOT / "content/release.json").read_text(encoding="utf-8"))


def read_json(name: str):
    return json.loads((ROOT / "content" / name).read_text(encoding="utf-8"))


def load_portal_captures(language):
    edition = RELEASE["languages"][language]
    name = edition["portal_manifest"]
    if Path(name).name != name or not name.endswith(".json"):
        raise ValueError("Portal manifest must be a JSON filename relative to content/.")
    manifest_path = ROOT / "content" / name
    if not manifest_path.is_file() or manifest_path.is_symlink() or manifest_path.parent.is_symlink():
        raise ValueError(f"Missing or nonregular portal manifest: content/{name}")
    manifest = read_json(name)
    if manifest.get("capture_method") != "playwright-mcp-headless" or manifest.get("synthetic_ui") is not False:
        raise ValueError("Portal screenshots must be genuine headless MCP captures.")
    scope = manifest.get("scope", {})
    project = "contoso-workshop-en" if language == "en" else "contoso-workshop"
    if (
        scope.get("repository_id") != 1396573688 or scope.get("project") != project
        or not scope.get("resource_group") or not scope.get("ownership_receipt")
    ):
        raise ValueError(f"{language}: portal captures must identify the owned {project} project.")
    captures = manifest["captures"]
    paths = [item["path"] for item in captures]
    if len(paths) != edition["portal_screenshots"] or len(paths) != len(set(paths)):
        raise ValueError(f"{language}: expected {edition['portal_screenshots']} distinct portal captures.")
    directory = Path("assets/portal/en" if language == "en" else "assets/portal")
    for item in captures:
        relative = Path(item["path"])
        path = ROOT / relative
        if relative.parent != directory or relative.suffix != ".png":
            raise ValueError(f"{language}: unexpected portal screenshot path: {item['path']}")
        if not path.is_file() or any(
            part.is_symlink() for part in (path, *path.parents) if part.is_relative_to(ROOT)
        ):
            raise ValueError(f"Missing or nonregular portal screenshot: {item['path']}")
        data = path.read_bytes()
        if data[:8] != b"\x89PNG\r\n\x1a\n" or hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise ValueError(f"Portal screenshot signature/hash mismatch: {item['path']}")
        if datetime.fromisoformat(item["captured_at"].replace("Z", "+00:00")).tzinfo is None:
            raise ValueError("Portal capture time must include timezone.")
        if not item["route"] or not item["masked"] or not item["purpose"]:
            raise ValueError(f"Portal screenshot lacks provenance/caption: {item['path']}")
    return captures


def load_content(language):
    if language not in RELEASE["languages"]:
        raise ValueError(f"Unsupported guide language: {language}")
    chapters = read_json("chapters.json")
    learning = read_json("learning-paths.json")
    source_data = read_json("sources.json")
    capabilities = read_json("capabilities.json")
    if language == "en":
        translated_chapters = read_json("chapters.en.json")
        if [c["id"] for c in translated_chapters] != [c["id"] for c in chapters]:
            raise ValueError("English chapter translations must match every canonical chapter in order.")
        for chapter, translation in zip(chapters, translated_chapters, strict=True):
            if set(translation) != {"id", "title", "summary", "status"}:
                raise ValueError(f"Unexpected translated chapter fields: {translation['id']}")
            chapter.update(translation)
            if "file" in chapter:
                chapter["file"] = "docs/en/" + Path(chapter["file"]).name
        translated_learning = read_json("learning-paths.en.json")
        if set(translated_learning) != set(learning):
            raise ValueError("Every learning-path requirement needs an English translation.")
        for chapter_id, translation in translated_learning.items():
            if set(translation) != {"label", "requires"}:
                raise ValueError(f"Unexpected translated learning-path fields: {chapter_id}")
            learning[chapter_id].update(translation)
        translated_sources = read_json("sources.en.json")
        if set(translated_sources["notes"]) != {s["id"] for s in source_data["sources"]}:
            raise ValueError("Every official source needs an English scope note.")
        source_data["policy"] = translated_sources["policy"]
        for source in source_data["sources"]:
            source["basis"] = translated_sources["basis"][source["basis"]]
            source["note"] = translated_sources["notes"][source["id"]]
        translated_capabilities = read_json("capabilities.en.json")
        for original, translation in zip(capabilities, translated_capabilities, strict=True):
            if set(translation) != {"lab", "source", "area", "name", "status"}:
                raise ValueError("Unexpected translated capability fields.")
            if any(original[key] != translation[key] for key in ("lab", "source")):
                raise ValueError("Translated capabilities must retain their canonical lab and source.")
            original.update(translation)
    chapters = [{**chapter, "learning": learning.get(chapter["id"])} for chapter in chapters]
    return chapters, source_data, capabilities


def coverage_markdown(capabilities, chapters, sources, language="ko"):
    title_map = {c["id"]: c for c in chapters}
    counts = Counter(c["mode"] for c in capabilities)
    if language == "en":
        modes = {
            "직접 실습": ("Direct lab", "An executable main path or local exercise is provided. This does not mean every subfeature in the row was run in the cloud."),
            "조건부 실습": ("Conditional lab", "Follow the steps only when the required resources, permissions, licenses, and Preview access are available."),
            "설계": ("Design", "Design the decision criteria, configuration, and failure, permission, and operational checks. No real change is performed."),
            "참고": ("Reference", "Understand product boundaries and the current official implementation path. Not counted as a full implementation lab."),
        }
        lines = [
            "> **Coverage is explicit.** The official capability map and reference connect each capability group to labs, design exercises, or reference material.",
            "",
            f"There are **{len(capabilities)} coverage entries** across 25 modules. This is not a count of individual product APIs or models.",
            "", "## How to read the coverage levels", "",
            "| Depth | Meaning | Entries |", "| --- | --- | ---: |",
        ]
        lines += [f"| {label} | {description} | {counts[mode]} |" for mode, (label, description) in modes.items()]
        lines += [
            "", "**A status label is not an unconditional guarantee for an entire row.** Check the source for API, SDK, portal, model, and regional details. If permissions or quota prevent a run, record it as not executed.",
            "", "## Capabilities mapped to labs", "",
            "| Area | Capability group | Module | Depth | Availability / verification scope | Evidence |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for item in capabilities:
            chapter = title_map[item["lab"]]
            lines.append(
                f"| {item['area']} | {item['name']} | [L{chapter['number']}](#{chapter['id']}) | "
                f"{modes[item['mode']][0]} | {item['status']} | [Official documentation]({sources[item['source']]['url']}) |"
            )
        return "\n".join(lines)
    lines = [
        "> **포함 범위를 공개합니다.** 공식 capability map/reference를 기준으로 기능군을 실습·설계·참고 항목에 연결했습니다.",
        "",
        f"총 **{len(capabilities)}개 커버리지 항목**입니다. 25개 모듈에서 다룹니다. 항목 수는 제품의 개별 API나 모델 개수가 아닙니다.",
        "",
        "## 범위 읽는 법",
        "",
        "| 깊이 | 의미 | 항목 수 |", "| --- | --- | ---: |",
    ]
    descriptions = {
        "직접 실습": "실행 가능한 주요 경로 또는 로컬 실습 제공. 해당 행의 모든 세부 기능을 cloud 실행했다는 의미는 아님.",
        "조건부 실습": "추가 자원·권한·라이선스·Preview가 준비된 경우 단계에 따라 수행.",
        "설계": "판단 기준·구성·실패/권한/운영 검증을 설계. 실제 변경 미실행.",
        "참고": "제품 경계와 현재 공식 구현 경로 안내. 전체 구현 실습으로 합산하지 않음.",
    }
    for mode, description in descriptions.items():
        lines.append(f"| {mode} | {description} | {counts[mode]} |")
    lines += [
        "",
        "**상태는 행 전체의 무조건적 보증이 아닙니다.** API·SDK·포털·모델·지역의 세부 상태는 원문을 확인하세요. "
        "권한이나 quota가 없어서 실행하지 못한 항목은 미실행으로 남깁니다.",
        "",
        "## 기능과 실습 연결",
        "",
        "| 영역 | 기능군 | 모듈 | 깊이 | 확인 상태 | 근거 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in capabilities:
        chapter = title_map[item["lab"]]
        source = sources[item["source"]]
        lines.append(
            f"| {item['area']} | {item['name']} | [L{chapter['number']}](#{chapter['id']}) | "
            f"{item['mode']} | {item['status']} | [공식 문서]({source['url']}) |"
        )
    return "\n".join(lines)


def sources_markdown(source_data, language="ko"):
    table = [
        "| ID | Document | Basis for verification | Used for |" if language == "en"
        else "| ID | 문서 | 확인 근거 | 사용하는 내용 |",
        "| --- | --- | --- | --- |",
    ]
    table += [
        f"| `{source['id']}` | [{source['title']}]({source['url']}) | {source['basis']} | {source['note']} |"
        for source in source_data["sources"]
    ]
    path = ROOT / ("docs/en/sources.md" if language == "en" else "docs/sources.md")
    return path.read_text(encoding="utf-8").format(
        documentation_validation=RELEASE["documentation_validation"],
        historical_validation=RELEASE["historical_validation"],
        validation=RELEASE["languages"][language]["validation"],
        source_table="\n".join(table),
    )


def instruction_reading_example(language):
    """Present one preserved answer pair without rerunning or rewriting evidence."""
    folder = ROOT / "validation/current" / language
    responses = json.loads((folder / "responses.json").read_text(encoding="utf-8"))
    native = json.loads((folder / "native.json").read_text(encoding="utf-8"))
    case_id = "compound-request-no-tools"
    answers = [row for row in responses["rows"] if row["id"] == case_id]
    judgments = [row for row in native["comparison"]["rows"] if row["case_id"] == case_id]
    for record, rows in ((responses, answers), (native, judgments)):
        if (
            record["language"] != language or len(rows) != 2
            or {row["instructions"] for row in rows} != {"v1", "v2"}
        ):
            raise ValueError(f"{language}: the reading example requires one actual v1/v2 pair.")
    answers = {row["instructions"]: row for row in answers}
    judgments = {row["instructions"]: row for row in judgments}
    if not answers["v1"]["query"] or answers["v1"]["query"] != answers["v2"]["query"]:
        raise ValueError("The reading example must compare the same actual question.")
    english = language == "en"
    labels = (
        ("Preserved question", "Actual answer", "Metric / 5", "Original relevance reasons (English)")
        if english else ("보존된 질문 원문", "실제 답변", "평가 항목 / 5", "관련성 채점 이유 원문 (영어)")
    )
    metrics = {
        "completeness": "Completeness" if english else "완결성",
        "relevance": "Relevance" if english else "관련성",
        "groundedness": "Groundedness" if english else "근거성",
    }
    lines = [
        '<div class="worked-example" markdown="1">',
        "", f"**{labels[0]} · `{case_id}`**", "",
        *("> " + escape(line) for line in answers["v1"]["query"].splitlines()),
    ]
    for version in ("v1", "v2"):
        answer = json.loads(answers[version]["raw_answer"])
        if (
            not isinstance(answer["answer"], str) or not answer["answer"].strip()
            or answers[version]["response_id"] != judgments[version]["response_id"]
        ):
            raise ValueError("The reading example must retain correlated, nonempty actual answers.")
        lines += [
            "", '<div class="recorded-answer" markdown="1">',
            "", f"**{version} — {labels[1]}**", "", escape(answer["answer"]), "", "</div>",
        ]
    lines += ["", f"| {labels[2]} | v1 | v2 |", "| --- | ---: | ---: |"]
    for key, title in metrics.items():
        scores = [judgments[version]["metrics"][key]["score"] for version in ("v1", "v2")]
        if any(type(score) not in (int, float) or not 1 <= score <= 5 for score in scores):
            raise ValueError("The reading example requires actual native scores on the 1–5 scale.")
        lines.append(f"| {title} | {scores[0]:g} | {scores[1]:g} |")
    lines += ["", '<details class="judge-reasons" markdown="1">', f"<summary>{labels[3]}</summary>"]
    for version in ("v1", "v2"):
        reason = judgments[version]["metrics"]["relevance"]["reason"]
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("The reading example requires the original judge reasons.")
        lines += ["", f"**{version}**", "", escape(reason)]
    lines += ["", "</details>", "", "</div>"]
    return "\n".join(lines)


def source_body(chapter, chapters, capabilities, source_data, language="ko"):
    sources = {s["id"]: s for s in source_data["sources"]}
    if chapter.get("generated") == "coverage":
        return coverage_markdown(capabilities, chapters, sources, language)
    if chapter.get("generated") == "sources":
        return sources_markdown(source_data, language)
    body = (ROOT / chapter["file"]).read_text(encoding="utf-8")
    def normalize_link(match):
        address = urlparse(match[1])
        resolved = ((ROOT / chapter["file"]).parent / unquote(address.path)).resolve()
        relative = resolved.relative_to(ROOT).as_posix()
        return "](" + urlunparse(address._replace(path=relative)) + ")"

    body = re.sub(r"\]\((\.\./[^)]+)\)", normalize_link, body)
    if chapter["id"] == "l08":
        marker = "<!-- instruction-reading-example -->"
        if body.count(marker) != 1:
            raise ValueError("L08 must contain exactly one preserved-result reading example.")
        body = body.replace(marker, instruction_reading_example(language))
    if chapter.get("learning"):
        learning = chapter["learning"]
        label = read_json("reader-labels.json")[language]["learning_order"]
        body = f"> **{label}: {learning['label']}** — {learning['requires']}\n\n" + body
    return body


def render_chapter(chapter, body, source_map, previous, following, captures, ui):
    chapter_id = chapter["id"]
    engine = markdown.Markdown(
        extensions=["tables", "fenced_code", "toc", "md_in_html", "sane_lists"],
        extension_configs={"toc": {
            "slugify": lambda value, separator: chapter_id + "-" + slugify_unicode(value, separator),
        }},
    )
    rendered = engine.convert(body)
    rendered = re.sub(
        r"<table>", f'<div class="table-wrap" tabindex="0" role="region" aria-label="{ui["table_aria"]}"><table>', rendered,
    ).replace("</table>", "</table></div>")
    def figure(match):
        image, source = match.groups()
        description = re.search(r'\balt="([^"]+)"', image).group(1)
        capture = captures.get(source)
        if source.startswith("assets/portal/") and capture is None:
            raise ValueError(f"Portal image has no capture in this language's manifest: {source}")
        note = (
            f'<span class="capture-note">{escape(ui["capture"].format(date=capture["captured_at"][:10]))}</span>'
            if capture else ""
        )
        kind = ' class="portal-capture"' if capture else ""
        return (
            f'<figure{kind}>{image}<figcaption><span>{description}</span>{note}'
            f'<a href="{source}" target="_blank" rel="noopener noreferrer">{ui["original"]}</a></figcaption></figure>'
        )

    rendered = re.sub(r'<p>(<img[^>]+src="([^"]+)"[^>]*>)</p>', figure, rendered)
    rendered = re.sub(r"<a href=\"(https?://[^\"]+)\"", r'<a href="\1" target="_blank" rel="noopener noreferrer"', rendered)
    headings = [
        f'<a href="#{escape(token["id"])}">{escape(token["name"])}</a>'
        for token in engine.toc_tokens if token["level"] == 2
    ]
    citations = "".join(
        f'<li><a href="{escape(source_map[key]["url"])}" target="_blank" rel="noopener noreferrer">'
        f'{escape(source_map[key]["title"])}</a></li>' for key in chapter["sources"]
    )
    label = f'L{chapter["number"]}' if chapter["track"] != "reference" else chapter["number"]
    time_label = f'<span>{ui["minutes"].format(minutes=chapter["minutes"])}</span>' if chapter["minutes"] else ""
    badge = "preview" if "preview" in chapter["status"].lower() else "neutral"
    learning = chapter.get("learning")
    learning_badge = (
        f'<span class="learning-badge" data-learning-mode="{escape(learning["mode"])}">{escape(learning["label"])}</span>'
        if learning else f'<span class="learning-badge" data-learning-mode="core">{ui["core_badge"]}</span>'
        if chapter["track"] == "core" else ""
    )
    checkbox = (
        f'<button class="complete-button" type="button" data-complete="{chapter_id}" aria-pressed="false">'
        f'<span class="check-icon" aria-hidden="true">✓</span><span class="complete-label">{ui["complete"]}</span></button>'
        if chapter["track"] != "reference" else ""
    )
    prev_link = f'<a href="#{previous["id"]}"><span>{ui["previous"]}</span>{escape(previous["title"])}</a>' if previous else '<span></span>'
    next_link = f'<a class="next" href="#{following["id"]}"><span>{ui["next"]}</span>{escape(following["title"])} <b aria-hidden="true">→</b></a>' if following else f'<a href="#l00">{ui["back"]}</a>'
    return f"""
<article class="chapter" id="{chapter_id}" data-track="{chapter['track']}" aria-labelledby="{chapter_id}-title">
  <header class="chapter-header">
    <div class="chapter-meta"><span class="eyebrow">{label} / {ui['tracks'][chapter['track']]}</span>{time_label}{learning_badge}<span class="status-badge {badge}">{escape(chapter['status'])}</span></div>
    <h1 id="{chapter_id}-title" tabindex="-1">{escape(chapter['title'])}</h1>
    <p class="chapter-summary">{escape(chapter['summary'])}</p>
    <nav class="section-nav" aria-label="{ui['sections']}">{''.join(headings)}</nav>
  </header>
  <div class="prose">{rendered}</div>
  <details class="source-notes"><summary>{ui['citations'].format(count=len(chapter['sources']))}</summary><ul>{citations}</ul></details>
  <div class="completion">{checkbox}<span>{ui['progress_boundary']}</span></div>
  <nav class="chapter-pagination" aria-label="{ui['pagination']}">{prev_link}{next_link}</nav>
</article>
"""


def portable_book_links(text, output_path):
    def replace(match):
        address = urlparse(match[1])
        if address.scheme or address.netloc or not address.path:
            return match[0]
        if address.path.endswith(".html"):
            target = RELEASE["site_url"] + match[1]
        else:
            target = urlunparse(address._replace(
                path=posixpath.relpath(address.path, Path(output_path).parent.as_posix()),
            ))
        return f"]({target})"

    return re.sub(r"\]\(([^)\s]+)\)", replace, text)


def build_language(language):
    chapters, source_data, capabilities = load_content(language)
    ui = read_json("reader-labels.json")[language]
    edition = RELEASE["languages"][language]
    sources = {s["id"]: s for s in source_data["sources"]}
    captures = {item["path"]: item for item in load_portal_captures(language)}
    bodies = {c["id"]: source_body(c, chapters, capabilities, source_data, language) for c in chapters}
    pages = []
    search_data = []
    for index, chapter in enumerate(chapters):
        pages.append(render_chapter(
            chapter, bodies[chapter["id"]], sources,
            chapters[index - 1] if index else None,
            chapters[index + 1] if index + 1 < len(chapters) else None, captures, ui,
        ))
        plain = re.sub(r"<[^>]+>", " ", markdown.markdown(bodies[chapter["id"]], extensions=["tables", "fenced_code"]))
        search_data.append({
            "id": chapter["id"], "number": chapter["number"], "title": chapter["title"],
            "summary": chapter["summary"], "track": chapter["track"], "text": re.sub(r"\s+", " ", plain),
        })
    nav = []
    for track, title in ui["tracks"].items():
        links = []
        for c in chapters:
            if c["track"] == track:
                mode_label = f'<small class="nav-learning">{escape(c["learning"]["label"])}</small>' if c.get("learning") else ""
                links.append(
                    f'<a class="chapter-link" href="#{c["id"]}" data-chapter="{c["id"]}" data-track="{track}">'
                    f'<span class="nav-number">{c["number"]}</span><span class="nav-title">{escape(c["title"])}{mode_label}</span>'
                    '<span class="nav-done" aria-hidden="true">✓</span></a>'
                )
        nav.append(f'<div class="nav-group" data-group="{track}"><h2>{title}</h2>{"".join(links)}</div>')
    css = (ROOT / "assets/styles.css").read_text(encoding="utf-8")
    js = (ROOT / "assets/app.js").read_text(encoding="utf-8")
    serialized = json.dumps(search_data, ensure_ascii=False).replace("<", "\\u003c").replace("&", "\\u0026")
    serialized_ui = json.dumps(
        {**ui["js"], **{key: ui[key] for key in ("previous", "next", "back")}}, ensure_ascii=False,
    ).replace("<", "\\u003c").replace("&", "\\u0026")
    language_links = []
    for code, other in RELEASE["languages"].items():
        current = ' aria-current="true"' if code == language else ""
        language_links.append(
            f'<a href="{other["html"]}" data-language="{code}" lang="{code}" hreflang="{code}"'
            f'{current}>{other["label"]}</a>'
        )
    alternate_links = "".join(
        f'<link rel="alternate" hreflang="{code}" href="{RELEASE["site_url"]}{other["html"]}">'
        for code, other in RELEASE["languages"].items()
    )
    print_toc = "".join(
        f'<li><a href="#{c["id"]}"><span>{c["number"]}</span> {escape(c["title"])}</a></li>' for c in chapters
    )
    cover_boundary = ui["cover_boundary"].format(
        validation=f'<a href="{escape(edition["validation"])}">{escape(edition["validation"])}</a>',
    )
    html = f"""<!doctype html>
<html lang="{language}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{escape(ui['description'])} {RELEASE['edition']}.">
<meta name="color-scheme" content="light dark">
<link rel="icon" type="image/svg+xml" href="assets/microsoft-foundry.svg">
<link rel="canonical" href="{RELEASE['site_url']}{edition['html']}">
<link rel="alternate" hreflang="x-default" href="{RELEASE['site_url']}">
{alternate_links}
<title>{ui['title']} | {ui['tagline']}</title>
<style>{css}</style>
</head>
<body>
<a class="skip-link" href="#main">{ui['skip']}</a>
<header class="topbar">
  <a class="brand" href="#l00" aria-label="{ui['home']}">
    <img class="brand-mark" src="assets/microsoft-foundry.svg" alt="Microsoft Foundry" width="42" height="42">
    <span><strong>Foundry <span class="brand-light">Lab Guide</span></strong><small>{ui['tagline']}</small></span>
  </a>
  <div class="top-actions">
    <span class="edition"><span aria-hidden="true"></span>Contoso · {RELEASE['edition']}</span>
    <nav class="language-switch" aria-label="{ui['language']}">{''.join(language_links)}</nav>
    <button id="theme-toggle" class="icon-button" type="button" aria-label="{ui['js']['dark_aria']}">{ui['theme']}</button>
    <button id="print-one" class="quiet-button" type="button">{ui['print_one']}</button>
    <button id="print-all" class="quiet-button" type="button">{ui['print_all']}</button>
    <button id="menu-toggle" class="quiet-button mobile-only" type="button" aria-expanded="false" aria-controls="sidebar">{ui['menu']}</button>
  </div>
</header>
<div class="layout">
<aside id="sidebar" class="sidebar" aria-label="{ui['navigation']}">
  <div class="search-box"><label for="guide-search">{ui['search']}</label><div class="search-field"><input id="guide-search" type="search" placeholder="{ui['placeholder']}" autocomplete="off" aria-controls="search-results"><kbd aria-hidden="true">/</kbd></div></div>
  <label for="learning-path" class="path-label">{ui['path']}</label>
  <select id="learning-path">
    <option value="all">{ui['all']}</option><option value="core">{ui['core']}</option>
    <option value="quick">{ui['quick']}</option><option value="offline">{ui['offline']}</option>
    <option value="advanced">{ui['advanced']}</option><option value="reference">{ui['reference']}</option>
  </select>
  <div class="progress-card"><div><strong>{ui['progress']}</strong><span id="progress-label">0 / 25</span></div><progress id="progress" value="0" max="25" aria-label="{ui['progress_aria']}"></progress><small>{ui['progress_hint']}</small></div>
  <nav id="chapter-nav" aria-label="{ui['toc']}">{''.join(nav)}</nav>
  <button id="reset-progress" class="text-button" type="button">{ui['reset']}</button>
  <div class="sidebar-note">{ui['offline_note']}</div>
</aside>
<main id="main" tabindex="-1">
  <section class="hero" id="hero" aria-labelledby="hero-title">
    <div class="hero-kicker">{ui['hero_kicker']}</div>
    <h2 id="hero-title">{ui['hero_title']}</h2>
    <p>{ui['hero_description']}</p>
    <div class="hero-actions"><a href="#l00-first-steps" class="primary-link">{ui['start']} <span aria-hidden="true">→</span></a><a href="#l01" class="secondary-link">{ui['ready']}</a><a href="{RELEASE['archive']}" class="secondary-link">{ui['download_kit']}</a></div>
    <div class="hero-stats"><div><strong>13</strong><span>{ui['stat_core']}</span></div><div><strong>12</strong><span>{ui['stat_electives']}</span></div><div><strong>1</strong><span>{ui['stat_scenario']}</span></div></div>
    <div class="hero-orbit" aria-hidden="true"><span></span><i></i><b>f</b></div>
  </section>
  <div class="reader-note" id="reader-note"><span class="note-mark" aria-hidden="true">i</span><p>{ui['reader_note']}</p><a href="#sources">{ui['view_basis']}</a></div>
  <section class="print-cover" aria-label="{ui['cover_aria']}">
    <p class="eyebrow">MICROSOFT FOUNDRY / HANDS-ON GUIDE</p>
    <h1>{ui['cover_title']}</h1>
    <p>{ui['cover_description']}</p>
    <p><strong>{RELEASE['edition']} {ui['cover_edition']}</strong><br>{ui['duration']}</p>
    <p class="print-boundary">{cover_boundary}</p>
    <h2>{ui['reading_order']}</h2><ol class="print-toc">{print_toc}</ol>
    <p>{ui['kit_note']} {ui['web_guide']}: {edition['html']} / {ui['text_edition']}: {edition['markdown']} / <a href="{edition['receipt_html']}">{ui['receipt']}</a></p>
  </section>
  <section id="search-results" class="search-results" aria-labelledby="search-title" hidden><h1 id="search-title">{ui['search_results']}</h1><p id="search-count" role="status" aria-live="polite"></p><div id="search-list"></div></section>
  <p id="storage-warning" class="storage-warning" role="status" hidden>{ui['storage_warning']}</p>
{''.join(pages)}
  <footer class="site-footer"><strong>{ui['footer_title']}</strong><p>{ui['footer_note']}</p><a href="{edition['readme']}">{ui['getting_started']}</a><a href="{edition['markdown']}">{ui['markdown']}</a><a href="{edition['pdf']}">{ui['pdf']}</a><a href="{RELEASE['archive']}">{ui['zip']}</a><a href="{edition['receipt_html']}">{ui['receipt']}</a><a href="{edition['validation']}">{ui['validation']}</a><a href="#sources">{ui['sources']}</a></footer>
</main>
</div>
<div id="toast" class="toast" role="status" aria-live="polite"></div>
<noscript><div class="noscript-note">{ui['nojs']}</div></noscript>
<script id="guide-data" type="application/json">{serialized}</script>
<script id="guide-ui" type="application/json">{serialized_ui}</script>
<script>{js}</script>
</body>
</html>
"""
    (ROOT / edition["html"]).write_text(html, encoding="utf-8")
    book = [
        f"# {ui['title']} — {ui['tagline']}",
        "",
        f"> {RELEASE['edition']} {ui['book_intro']} "
        f"[{ui['web_guide']}]({RELEASE['site_url']}{edition['html']}) — {ui['book_web']}",
        "",
        " | ".join(
            f"[{other['label']}]({other['markdown']})"
            for other in RELEASE["languages"].values()
        ),
        "",
        ui["book_boundary"].format(validation=edition["validation"]),
        "",
        f"[{ui['receipt']}]({RELEASE['site_url']}{edition['receipt_html']})",
        "",
        f"## {ui['toc']}",
        "",
    ]
    book += [f'- [{c["number"]}. {c["title"]}](#{c["id"]})' for c in chapters]
    for chapter in chapters:
        book += [
            "", "---", "", f'<a id="{chapter["id"]}"></a>', "",
            f'# {chapter["number"]}. {chapter["title"]}', "",
            f'**{ui["tracks"][chapter["track"]]} · {chapter["status"]}**' + (" · " + ui["book_time"].format(minutes=chapter["minutes"]) if chapter["minutes"] else ""),
            "", bodies[chapter["id"]], "", f"### {ui['official']}", "",
        ]
        book += [f'- [{sources[key]["title"]}]({sources[key]["url"]})' for key in chapter["sources"]]
    markdown_path = ROOT / edition["markdown"]
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(
        portable_book_links("\n".join(book) + "\n", edition["markdown"]), encoding="utf-8",
    )
    print(f"Built {language}: {len(chapters)} sections (25 labs), {len(capabilities)} coverage rows, {len(sources)} official sources.")


def build():
    for language in RELEASE["languages"]:
        build_language(language)


if __name__ == "__main__":
    build()
