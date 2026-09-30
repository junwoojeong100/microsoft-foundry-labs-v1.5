"""Build the offline reader and a portable Markdown book from the same sources."""

from __future__ import annotations

from collections import Counter
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlparse, urlunparse

import markdown
from markdown.extensions.toc import slugify_unicode

ROOT = Path(__file__).resolve().parents[1]
RELEASE = json.loads((ROOT / "content/release.json").read_text(encoding="utf-8"))


def read_json(name: str):
    return json.loads((ROOT / "content" / name).read_text(encoding="utf-8"))


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
    if language == "en":
        table = [
            "| ID | Document | Basis for verification | Used for |",
            "| --- | --- | --- | --- |",
        ]
        table += [
            f"| `{source['id']}` | [{source['title']}]({source['url']}) | {source['basis']} | {source['note']} |"
            for source in source_data["sources"]
        ]
        return (ROOT / "docs/en/sources.md").read_text(encoding="utf-8").format(
            documentation_validation=RELEASE["documentation_validation"],
            historical_validation=RELEASE["historical_validation"],
            source_table="\n".join(table),
        )
    lines = [
        "> **기초 출처 확인: 2026-09-29 / 실행 API 재확인·Contoso 보완: 2026-09-30, Asia/Seoul.** "
        "날짜가 적혀 있다고 영구적으로 최신인 자료는 아닙니다.",
        "",
        "## 최신성을 판단한 방식",
        "",
        "Microsoft Learn의 플랫폼 개요, capability reference, GA 표, 기능별 문서와 공식 SDK 예제를 확인했습니다. "
        "상태가 충돌하거나 범위가 다르면 기능별 API·포털·지역을 분리하고 더 좁은 의미로 설명했습니다.",
        "",
        "확인 당시 월간 What's new 모음은 **2026년 8월**을 안내했습니다. 이를 9월의 모든 출시를 포괄하는 목록으로 바꾸지 않았습니다. "
        "Content Understanding 등의 기능별 문서에는 9월 업데이트가 있어 별도로 반영했습니다.",
        "",
        "## 반드시 기억할 변경",
        "",
        "| 항목 | 이 가이드의 처리 |",
        "| --- | --- |",
        "| 새 포털 GA | 개별 기능의 GA와 분리 |",
        "| 포털 Workflows 종료 예정 | 2026-12-01을 명시하고 새 구현은 MAF |",
        "| Foundry IQ | 일부 API GA, 포털 Preview |",
        "| Foundry RBAC 이름 | 새 이름과 이전 Azure AI 이름을 설명 |",
        "| Memory / Voice / Agent guardrails / 운영 일부 | Preview 표기 |",
        "| Agent Optimizer | GA 표 기준 Limited preview |",
        "| Content Understanding | 2025-11-01 GA와 2026-06-01-preview 구분 |",
        "| SDK 조합 | 실제 설치 가능한 기본/advanced 환경 분리 |",
        "",
        "## 검증의 경계",
        "",
        "### 현재 자동 검증 결과",
        "",
        "**automated-v3의 실제 릴리스 게이트는 통과했습니다.** dev 29/30, 독립 holdout 9/10, "
        "critical 실패 0건, calibration 8/8입니다. 비중대 미통과 사례도 원본으로 남겼으며 "
        "사람 검토는 선택 안내로 구분합니다.",
        "",
        "Routine은 실제 예약 응답과 trace 및 disabled 상태를 확인했습니다. Optimizer는 "
        "지시문만 바뀌는 후보의 누락 모델을 명시적으로 상속하도록 보완한 뒤 정상 실행됐습니다. "
        "별도 Optimizer dev 20건의 baseline/best 점수는 1.0/1.0으로 추가 개선이 없어 승격하지 않았습니다. "
        "검증 세부 자료는 `validation/current/`와 `validation/automated-v3/`에 있습니다.",
        "",
        f"최신 문서·브라우저·PDF·패키지 검사는 `{RELEASE['documentation_validation']}/`에 따로 둡니다. "
        "이는 문서 검사이며 Azure를 새로 실행한 증거가 아닙니다.",
        "",
        "### 이전 v1 결과와 현재 자동 검증 경로",
        "",
        f"이전 검증 파일은 [정리 전 Git 커밋의 원본]({RELEASE['historical_validation']})에서 확인합니다. "
        "현재 파일 목록에서는 중복·이전 실행을 정리했으며 과거 기록의 내용이나 판정을 바꾸지 않았습니다.",
        "",
        "**아래 수치는 보존한 v1 결과입니다.** 새 RG에서 Hosted·Search/IQ·"
        "Toolbox/MCP/OpenAPI/Skills·Memory·A2A·native 평가·Tracing과 실제 OIDC 배포를 수행했습니다.",
        "",
        "| 구분 | 이번 결과 |", "| --- | --- |",
        "| 구현 완료 | A만으로 설치·문서 생성·테스트·패키징 가능 |",
        "| 실행 완료 | 새 Azure 환경, dev 10건·독립 holdout 10건, trace 10/10, CI 배포·업무 smoke |",
        "| 품질 통과 | **미통과**: holdout 9/10이나 safety 사례 hold-08의 필수 보안 정책 인용 누락 |",
        "| v1 운영 제한 | Routine history/output 미확인; native optimizer 신규 후보 0 |",
        "| 미실행 | Voice·CU 서비스·실제 fine-tuning·Foundry Local 장치·문서별 ACL·Teams 게시 |",
        "",
        "hold-08은 승인 우회를 거절했지만 요구된 `security-policy.md` 4절 근거가 없었습니다. "
        "판정 기준이나 safety 0건 규칙을 낮추지 않았고, holdout을 본 뒤 지시를 다시 조정하지 않았습니다. "
        "judge 대조군은 6/6 일치했지만 실제 사용자에 의한 검토와 동일하지 않습니다.",
        "",
        "**현재 automated-v3는 사람 검토를 선택 안내로 분리했습니다.** 기존 v1/v2 시험지는 dev 회귀로 보존하고 "
        "새 봉인 holdout과 검색·인용·도구 자동 검사를 사용합니다. 전체 90%·safety/access 실패 0건은 유지합니다. "
        "v3의 실제 통과 여부는 최신 `validation/current/report.json` 및 `validation/automated-v3/` 결과를 확인하세요.",
        "",
        "Routine은 생성·dispatch 요청까지 수행했으며 disabled 상태로 보존했습니다. "
        "Optimizer의 서비스 job 완료는 새 후보 생성/품질 개선을 뜻하지 않습니다. "
        f"이 v1 실행의 원본 결과·CI 요약·운영 상태는 [과거 검증 원본]({RELEASE['historical_validation']})에 있습니다.",
        "",
        "**로컬 계약 검증은 cloud 실행 검증이 아닙니다.** 구현 완료 / 실행 완료 / 품질 통과 / 차단 / 미실행을 "
        "구분합니다. 이번 실행은 새 전용 RG만 대상으로 하며 과거 A/B 결과를 Contoso 증거로 재사용하지 않습니다.",
        "",
        "로컬 검사 대상으로는 문서 구조·내부 링크·합성 데이터·도구 검증·평가 게이트·SDK 계약·웹 UI가 있습니다. "
        "구체적인 실행 결과와 미검증 범위는 [`validation/current/report.json`](validation/current/report.json)을 확인합니다. "
        "과거 검증 원본은 위의 고정된 Git 커밋에 보존하며 새로운 결과로 바꾸지 않습니다.",
        "",
        "전달물은 Microsoft 공식 교육과정이나 보증서가 아닙니다. 시나리오·설명·그림은 이 실습을 위해 작성했습니다. "
        "제품 사실의 근거는 아래 원문이며 전체 문서를 복제하지 않았습니다.",
        "",
        "## 공개 공식 출처",
        "",
        "| ID | 문서 | 확인 근거 | 사용하는 내용 |",
        "| --- | --- | --- | --- |",
    ]
    for source in source_data["sources"]:
        lines.append(
            f"| `{source['id']}` | [{source['title']}]({source['url']}) | {source['basis']} | {source['note']} |"
        )
    lines += [
        "",
        "## 다음 교육 전에 업데이트하기",
        "",
        "GA 표 → capability reference → 필요한 기능 문서 → 지역/모델 카드 → SDK 호환 조합 순으로 다시 확인합니다. "
        "변경한 사실은 `content/sources.json`과 해당 모듈에 함께 반영합니다. 출처 링크만 갱신하고 "
        "실습 코드·패키지·완료 기준을 그대로 두지 않습니다.",
    ]
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


def build_language(language):
    chapters, source_data, capabilities = load_content(language)
    ui = read_json("reader-labels.json")[language]
    edition = RELEASE["languages"][language]
    sources = {s["id"]: s for s in source_data["sources"]}
    captures = {item["path"]: item for item in read_json("portal-screenshots.json")["captures"]}
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
    serialized_ui = json.dumps(ui["js"], ensure_ascii=False).replace("<", "\\u003c").replace("&", "\\u0026")
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
    <div class="hero-kicker">BUILD → GROUND → ACT → EVALUATE → OPERATE</div>
    <h2 id="hero-title">{ui['hero_title']}</h2>
    <p>{ui['hero_description']}</p>
    <div class="hero-actions"><a href="#l01" class="primary-link">{ui['start']} <span aria-hidden="true">→</span></a><a href="#instructor" class="secondary-link">{ui['tour']}</a></div>
    <div class="hero-stats"><div><strong>25</strong><span>{ui['stat_modules']}</span></div><div><strong>{len(capabilities)}</strong><span>{ui['stat_features']}</span></div><div><strong>{len(sources)}</strong><span>{ui['stat_sources']}</span></div><div><strong>1</strong><span>{ui['stat_scenario']}</span></div></div>
    <div class="hero-orbit" aria-hidden="true"><span></span><i></i><b>f</b></div>
  </section>
  <div class="reader-note" id="reader-note"><span class="note-mark" aria-hidden="true">i</span><p>{ui['reader_note']}</p><a href="#sources">{ui['view_basis']}</a></div>
  <section class="print-cover" aria-label="{ui['cover_aria']}">
    <p class="eyebrow">MICROSOFT FOUNDRY / HANDS-ON GUIDE</p>
    <h1>{ui['cover_title']}</h1>
    <p>{ui['cover_description']}</p>
    <p><strong>{RELEASE['edition']} {ui['cover_edition']}</strong><br>{ui['duration']}</p>
    <p class="print-boundary">{ui['cover_boundary']}</p>
    <h2>{ui['reading_order']}</h2><ol class="print-toc">{print_toc}</ol>
    <p>{ui['kit_note']} {ui['web_guide']}: {edition['html']} / {ui['text_edition']}: {edition['markdown']}</p>
  </section>
  <section id="search-results" class="search-results" aria-labelledby="search-title" hidden><h1 id="search-title">{ui['search_results']}</h1><p id="search-count" role="status" aria-live="polite"></p><div id="search-list"></div></section>
  <p id="storage-warning" class="storage-warning" role="status" hidden>{ui['storage_warning']}</p>
{''.join(pages)}
  <footer class="site-footer"><strong>{ui['footer_title']}</strong><p>{ui['footer_note']}</p><a href="{edition['readme']}">{ui['getting_started']}</a><a href="{edition['markdown']}">{ui['markdown']}</a><a href="{edition['pdf']}">{ui['pdf']}</a><a href="{RELEASE['site_url']}{RELEASE['artifact']}.zip">{ui['zip']}</a><a href="data/receipt.html">{ui['receipt']}</a><a href="validation/current/report.json">{ui['validation']}</a><a href="#sources">{ui['sources']}</a></footer>
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
        " | ".join(f"[{other['label']}]({other['markdown']})" for other in RELEASE["languages"].values()),
        "",
        ui["book_boundary"],
        "",
        f"## {ui['toc']}",
        "",
    ]
    book += [f'- [{c["number"]}. {c["title"]}](#{c["id"]})' for c in chapters]
    for chapter in chapters:
        book_body = re.sub(
            r"\]\(([^():#?\s]+\.html(?:#[^)]*)?)\)",
            lambda match: f"]({RELEASE['site_url']}{match[1]})",
            bodies[chapter["id"]],
        )
        book += [
            "", "---", "", f'<a id="{chapter["id"]}"></a>', "",
            f'# {chapter["number"]}. {chapter["title"]}', "",
            f'**{ui["tracks"][chapter["track"]]} · {chapter["status"]}**' + (" · " + ui["book_time"].format(minutes=chapter["minutes"]) if chapter["minutes"] else ""),
            "", book_body, "", f"### {ui['official']}", "",
        ]
        book += [f'- [{sources[key]["title"]}]({sources[key]["url"]})' for key in chapter["sources"]]
    (ROOT / edition["markdown"]).write_text("\n".join(book) + "\n", encoding="utf-8")
    print(f"Built {language}: {len(chapters)} sections (25 labs), {len(capabilities)} coverage rows, {len(sources)} official sources.")


def build():
    for language in RELEASE["languages"]:
        build_language(language)


if __name__ == "__main__":
    build()
