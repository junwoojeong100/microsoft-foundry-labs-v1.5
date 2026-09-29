"""Build the offline reader and a portable Markdown book from the same sources."""

from __future__ import annotations

from collections import Counter
from html import escape
import json
from pathlib import Path
import re

import markdown
from markdown.extensions.toc import slugify_unicode

ROOT = Path(__file__).resolve().parents[1]
TRACKS = {"core": "기본 코스", "advanced": "심화 코스", "reference": "참고 자료"}
RELEASE = json.loads((ROOT / "content/release.json").read_text(encoding="utf-8"))


def read_json(name: str):
    return json.loads((ROOT / "content" / name).read_text(encoding="utf-8"))


def coverage_markdown(capabilities, chapters, sources):
    title_map = {c["id"]: c for c in chapters}
    counts = Counter(c["mode"] for c in capabilities)
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


def sources_markdown(source_data):
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
        "**로컬 계약 검증은 cloud 실행 검증이 아닙니다.** 구현 완료 / 실행 완료 / 품질 통과 / 차단 / 미실행을 "
        "구분합니다. 이번 실행은 새 전용 RG만 대상으로 하며 과거 A/B 결과를 Contoso 증거로 재사용하지 않습니다.",
        "",
        "로컬 검사 대상으로는 문서 구조·내부 링크·합성 데이터·도구 검증·평가 게이트·SDK 계약·웹 UI가 있습니다. "
        "구체적인 실행 결과와 미검증 범위는 [`validation/current/report.json`](validation/current/report.json)을 확인합니다. "
        "기존 validation 원본은 과거 자료로 보존하며 새로운 결과로 바꾸지 않습니다.",
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


def source_body(chapter, chapters, capabilities, source_data):
    sources = {s["id"]: s for s in source_data["sources"]}
    if chapter.get("generated") == "coverage":
        return coverage_markdown(capabilities, chapters, sources)
    if chapter.get("generated") == "sources":
        return sources_markdown(source_data)
    return (ROOT / chapter["file"]).read_text(encoding="utf-8").replace("../assets/", "assets/").replace("../data/", "data/")


def render_chapter(chapter, body, source_map, previous, following):
    chapter_id = chapter["id"]
    engine = markdown.Markdown(
        extensions=["tables", "fenced_code", "toc", "md_in_html", "sane_lists"],
        extension_configs={"toc": {
            "slugify": lambda value, separator: chapter_id + "-" + slugify_unicode(value, separator),
        }},
    )
    rendered = engine.convert(body)
    rendered = re.sub(
        r"<table>", '<div class="table-wrap" tabindex="0" role="region" aria-label="가로로 스크롤할 수 있는 표"><table>', rendered,
    ).replace("</table>", "</table></div>")
    rendered = re.sub(
        r'<p>(<img[^>]+src="([^"]+)"[^>]*>)</p>',
        r'<figure>\1<figcaption><a href="\2" target="_blank" rel="noopener noreferrer">다이어그램 크게 보기 ↗</a></figcaption></figure>',
        rendered,
    )
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
    time_label = f'<span>{chapter["minutes"]}분</span>' if chapter["minutes"] else ""
    badge = "preview" if "Preview" in chapter["status"] else "neutral"
    checkbox = (
        f'<button class="complete-button" type="button" data-complete="{chapter_id}" aria-pressed="false">'
        '<span class="check-icon" aria-hidden="true">✓</span><span class="complete-label">성공 기준을 확인했어요</span></button>'
        if chapter["track"] != "reference" else ""
    )
    prev_link = f'<a href="#{previous["id"]}"><span>이전</span>{escape(previous["title"])}</a>' if previous else '<span></span>'
    next_link = f'<a class="next" href="#{following["id"]}"><span>다음</span>{escape(following["title"])} <b aria-hidden="true">→</b></a>' if following else '<a href="#l00">시작으로 돌아가기 ↑</a>'
    return f"""
<article class="chapter" id="{chapter_id}" data-track="{chapter['track']}" aria-labelledby="{chapter_id}-title">
  <header class="chapter-header">
    <div class="chapter-meta"><span class="eyebrow">{label} / {TRACKS[chapter['track']]}</span>{time_label}<span class="status-badge {badge}">{escape(chapter['status'])}</span></div>
    <h1 id="{chapter_id}-title" tabindex="-1">{escape(chapter['title'])}</h1>
    <p class="chapter-summary">{escape(chapter['summary'])}</p>
    <nav class="section-nav" aria-label="이 모듈 안에서 이동">{''.join(headings)}</nav>
  </header>
  <div class="prose">{rendered}</div>
  <details class="source-notes"><summary>공식 근거 {len(chapter['sources'])}건 · 항목별 확인 범위는 출처 참조</summary><ul>{citations}</ul></details>
  <div class="completion">{checkbox}<span>진도는 이 브라우저에만 저장됩니다. Azure 실행을 판정하지 않습니다.</span></div>
  <nav class="chapter-pagination" aria-label="모듈 이동">{prev_link}{next_link}</nav>
</article>
"""


def build():
    chapters = read_json("chapters.json")
    source_data = read_json("sources.json")
    sources = {s["id"]: s for s in source_data["sources"]}
    capabilities = read_json("capabilities.json")
    bodies = {c["id"]: source_body(c, chapters, capabilities, source_data) for c in chapters}
    pages = []
    search_data = []
    for index, chapter in enumerate(chapters):
        pages.append(render_chapter(
            chapter, bodies[chapter["id"]], sources,
            chapters[index - 1] if index else None,
            chapters[index + 1] if index + 1 < len(chapters) else None,
        ))
        plain = re.sub(r"<[^>]+>", " ", markdown.markdown(bodies[chapter["id"]], extensions=["tables", "fenced_code"]))
        search_data.append({
            "id": chapter["id"], "number": chapter["number"], "title": chapter["title"],
            "summary": chapter["summary"], "track": chapter["track"], "text": re.sub(r"\s+", " ", plain),
        })
    nav = []
    for track, title in TRACKS.items():
        links = []
        for c in chapters:
            if c["track"] == track:
                links.append(
                    f'<a class="chapter-link" href="#{c["id"]}" data-chapter="{c["id"]}" data-track="{track}">'
                    f'<span class="nav-number">{c["number"]}</span><span class="nav-title">{escape(c["title"])}</span>'
                    '<span class="nav-done" aria-hidden="true">✓</span></a>'
                )
        nav.append(f'<div class="nav-group" data-group="{track}"><h2>{title}</h2>{"".join(links)}</div>')
    css = (ROOT / "assets/styles.css").read_text(encoding="utf-8")
    js = (ROOT / "assets/app.js").read_text(encoding="utf-8")
    serialized = json.dumps(search_data, ensure_ascii=False).replace("<", "\\u003c").replace("&", "\\u0026")
    print_toc = "".join(
        f'<li><a href="#{c["id"]}"><span>{c["number"]}</span> {escape(c["title"])}</a></li>' for c in chapters
    )
    html = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Contoso 구매 도우미로 모델·지식·도구·평가·운영까지 배우는 독립형 한국어 Microsoft Foundry 실습 가이드. {RELEASE['edition']} 보완본.">
<meta name="color-scheme" content="light dark">
<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
<title>Microsoft Foundry 실습 가이드 | 직접 만들며 이해하기</title>
<style>{css}</style>
</head>
<body>
<a class="skip-link" href="#main">본문으로 건너뛰기</a>
<header class="topbar">
  <a class="brand" href="#l00" aria-label="Foundry 실습 가이드 시작">
    <span class="brand-mark" aria-hidden="true">f<span>·</span></span>
    <span><strong>Foundry <span class="brand-light">Lab Guide</span></strong><small>직접 만들며 이해하기</small></span>
  </a>
  <div class="top-actions">
    <span class="edition"><span aria-hidden="true"></span>Contoso · {RELEASE['edition']}</span>
    <button id="theme-toggle" class="icon-button" type="button" aria-label="어두운 화면으로 전환">테마</button>
    <button id="print-one" class="quiet-button" type="button">현재 인쇄</button>
    <button id="print-all" class="quiet-button" type="button">전체 PDF</button>
    <button id="menu-toggle" class="quiet-button mobile-only" type="button" aria-expanded="false" aria-controls="sidebar">목차</button>
  </div>
</header>
<div class="layout">
<aside id="sidebar" class="sidebar" aria-label="학습 탐색">
  <div class="search-box"><label for="guide-search">가이드 검색</label><div class="search-field"><input id="guide-search" type="search" placeholder="IQ, 권한, 403…" autocomplete="off" aria-controls="search-results"><kbd aria-hidden="true">/</kbd></div></div>
  <label for="learning-path" class="path-label">학습 경로</label>
  <select id="learning-path">
    <option value="all">전체 모듈</option><option value="core">기본 코스 · 처음부터 끝까지</option>
    <option value="quick">90분 체험 · 사전 환경 필요</option><option value="offline">Azure 없이 · 로컬/설계 단계</option>
    <option value="advanced">심화 코스 · 선택해서 확장</option><option value="reference">참고 자료</option>
  </select>
  <div class="progress-card"><div><strong>나의 학습 진도</strong><span id="progress-label">0 / 25</span></div><progress id="progress" value="0" max="25" aria-label="25개 모듈 학습 진도"></progress><small>성공 기준을 확인한 모듈을 체크하세요.</small></div>
  <nav id="chapter-nav" aria-label="모듈 목차">{''.join(nav)}</nav>
  <button id="reset-progress" class="text-button" type="button">이 브라우저 진도 초기화</button>
  <div class="sidebar-note">가이드는 오프라인으로 읽습니다.<br>Azure 실습은 별도 인증·비용이 필요합니다.</div>
</aside>
<main id="main" tabindex="-1">
  <section class="hero" id="hero" aria-labelledby="hero-title">
    <div class="hero-kicker">BUILD → GROUND → ACT → EVALUATE → OPERATE</div>
    <h2 id="hero-title">Microsoft Foundry,<br><span>직접 만들며 이해하기.</span></h2>
    <p>하나의 업무용 에이전트로 연결하는<br>모델·지식·도구·평가·안전·운영의 전체 흐름.</p>
    <div class="hero-actions"><a href="#l01" class="primary-link">기본 실습 시작 <span aria-hidden="true">→</span></a><a href="#instructor" class="secondary-link">90분 코스 보기</a></div>
    <div class="hero-stats"><div><strong>25</strong><span>단계별 모듈</span></div><div><strong>{len(capabilities)}</strong><span>기능군 연결</span></div><div><strong>{len(sources)}</strong><span>공식 출처</span></div><div><strong>1</strong><span>일관된 실습 시나리오</span></div></div>
    <div class="hero-orbit" aria-hidden="true"><span></span><i></i><b>f</b></div>
  </section>
  <div class="reader-note" id="reader-note"><span class="note-mark" aria-hidden="true">i</span><p><strong>새 포털 GA ≠ 모든 기능 GA.</strong> Workflows는 2026-12-01 종료 예정입니다. 기본은 안정적인 핵심 경로, 심화는 Preview·지원 조건을 구분합니다.</p><a href="#sources">기준 보기 →</a></div>
  <section class="print-cover" aria-label="인쇄본 표지와 목차">
    <p class="eyebrow">MICROSOFT FOUNDRY / HANDS-ON GUIDE</p>
    <h1>Microsoft Foundry,<br>직접 만들며 이해하기.</h1>
    <p>하나의 구매·정책 도우미로 연결하는 모델 · 지식 · 도구 · 평가 · 안전 · 운영</p>
    <p><strong>{RELEASE['edition']} Contoso 독립형 실행 가이드 · 한국어 · 25개 모듈</strong><br>기본 코스 5시간 20분 + 대기·휴식 / 심화는 필요에 따라 선택</p>
    <p class="print-boundary">GA/Preview 및 구현·실행·품질을 구분합니다. 현재 실행 범위는 validation/current/report.json을 확인하세요. 실제 주문·결제·업무 승인은 수행하지 않습니다.</p>
    <h2>읽는 순서</h2><ol class="print-toc">{print_toc}</ol>
    <p>실행 파일과 데이터는 함께 제공된 실습 키트에 있습니다. 웹 가이드: index.html / 텍스트 판: GUIDE.ko.md</p>
  </section>
  <section id="search-results" class="search-results" aria-labelledby="search-title" hidden><h1 id="search-title">검색 결과</h1><p id="search-count" role="status" aria-live="polite"></p><div id="search-list"></div></section>
  <p id="storage-warning" class="storage-warning" role="status" hidden>이 환경에서는 로컬 저장소를 사용할 수 없어 진도가 현재 페이지에만 유지됩니다.</p>
  {''.join(pages)}
  <footer class="site-footer"><strong>배우는 것과 검증한 것을 구분합니다.</strong><p>Contoso 합성 데이터 · 명시적 Azure 실행 · GA/Preview 구분</p><a href="README.md">시작 안내</a><a href="GUIDE.ko.md">전체 Markdown</a><a href="{RELEASE['artifact']}.pdf">인쇄용 PDF</a><a href="validation/current/report.json">검증 범위</a><a href="#sources">출처</a></footer>
</main>
</div>
<div id="toast" class="toast" role="status" aria-live="polite"></div>
<noscript><div class="noscript-note">JavaScript가 꺼져 있습니다. 모든 모듈을 순서대로 읽을 수 있으며 검색·진도 저장은 동작하지 않습니다.</div></noscript>
<script id="guide-data" type="application/json">{serialized}</script>
<script>{js}</script>
</body>
</html>
"""
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    book = [
        "# Microsoft Foundry, 직접 만들며 이해하기",
        "",
        f"> {RELEASE['edition']} Contoso 독립형 실행 가이드 · 한국어 · 25개 모듈. "
        "웹으로는 [index.html](index.html)을 열어 검색·진도·학습 경로를 사용하세요.",
        "",
        "**검증 경계:** 구현·실행·품질의 현재 상태는 [실행 보고서](validation/current/report.json)를 확인합니다. "
        "직접 실습, 조건부 실습, 설계, 참고를 구분하며 과거 결과를 재사용하지 않습니다.",
        "",
        "## 목차",
        "",
    ]
    book += [f'- [{c["number"]}. {c["title"]}](#{c["id"]})' for c in chapters]
    for chapter in chapters:
        book += [
            "", "---", "", f'<a id="{chapter["id"]}"></a>', "",
            f'# {chapter["number"]}. {chapter["title"]}', "",
            f'**{TRACKS[chapter["track"]]} · {chapter["status"]}**' + (f' · 약 {chapter["minutes"]}분' if chapter["minutes"] else ""),
            "", bodies[chapter["id"]], "", "### 공식 근거", "",
        ]
        book += [f'- [{sources[key]["title"]}]({sources[key]["url"]})' for key in chapter["sources"]]
    (ROOT / "GUIDE.ko.md").write_text("\n".join(book) + "\n", encoding="utf-8")
    print(f"Built {len(chapters)} pages (25 labs), {len(capabilities)} coverage rows, {len(sources)} official sources.")


if __name__ == "__main__":
    build()
