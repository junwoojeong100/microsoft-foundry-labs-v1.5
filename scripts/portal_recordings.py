"""Build the offline index for separately reviewed, genuine portal recordings."""

from __future__ import annotations

import hashlib
from html import escape
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "downloads/portal"
STATUSES = {
    "executed": ("실제 수행", "Executed"),
    "partial": ("일부 수행·제한 있음", "Partial; limitations recorded"),
    "inspection": ("화면 관찰만", "Inspection only"),
    "blocked": ("차단·호출 미실행", "Blocked; no invocation"),
    "not_run": ("미실행", "Not run"),
}


def load_recordings():
    source = json.loads((ROOT / "content/portal-recordings.json").read_text(encoding="utf-8"))
    chapters = json.loads((ROOT / "content/chapters.json").read_text(encoding="utf-8"))
    expected = [chapter["id"] for chapter in chapters if chapter["track"] != "reference"]
    if source.get("capture_method") != "playwright-record-video" or source.get("synthetic_ui") is not False:
        raise ValueError("Portal footage must be genuine browser recordings, not reconstructed UI.")
    if source.get("privacy_review", {}).get("status") != "passed":
        raise ValueError("Portal recordings require a completed privacy review before publishing.")
    if [row["lab"] for row in source["coverage"]] != expected:
        raise ValueError("Recording coverage must disclose every module exactly once in reader order.")
    identifiers = [clip["id"] for clip in source["clips"]]
    if not identifiers or len(identifiers) != len(set(identifiers)):
        raise ValueError("Portal recording identifiers must be nonempty and distinct.")
    for clip in source["clips"]:
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", clip["id"]):
            raise ValueError("Recording identifiers must be safe local basenames.")
        seconds = clip["seconds"]
        if type(seconds) not in (int, float) or not math.isfinite(seconds) or seconds <= 0:
            raise ValueError("Each recording needs a finite positive duration.")
        for suffix in ("mp4", "ko.vtt", "en.vtt"):
            path = DESTINATION / f"{clip['id']}.{suffix}"
            if not path.is_file() or path.is_symlink() or DESTINATION.is_symlink():
                raise ValueError(f"Missing or nonregular recording asset: {path.name}")
            data = path.read_bytes()
            if hashlib.sha256(data).hexdigest() != clip["sha256"][suffix]:
                raise ValueError(f"Recording asset hash mismatch: {path.name}")
            if suffix == "mp4" and data[4:8] != b"ftyp":
                raise ValueError(f"Recording must be an MP4: {path.name}")
            if suffix.endswith("vtt") and not data.startswith(b"WEBVTT\n"):
                raise ValueError(f"Recording captions must be WebVTT: {path.name}")
    evaluation = DESTINATION / "evaluation-summary.json"
    if not evaluation.is_file() or evaluation.is_symlink():
        raise ValueError("Missing or nonregular portal evaluation summary.")
    if hashlib.sha256(evaluation.read_bytes()).hexdigest() != source["evaluation_summary_sha256"]:
        raise ValueError("Portal evaluation summary hash mismatch.")
    for row in source["coverage"]:
        if row["status"] not in STATUSES or any(clip not in identifiers for clip in row["clips"]):
            raise ValueError(f"Invalid recording coverage: {row['lab']}")
        if row["status"] in {"executed", "partial", "inspection", "blocked"} and not row["clips"]:
            raise ValueError(f"Observed coverage needs an actual clip: {row['lab']}")
    return source, chapters


def build():
    source, chapters = load_recordings()
    english = json.loads((ROOT / "content/chapters.en.json").read_text(encoding="utf-8"))
    titles = {chapter["id"]: chapter for chapter in chapters}
    en_titles = {chapter["id"]: chapter["title"] for chapter in english}
    videos = []
    for clip in source["clips"]:
        identifier = clip["id"]
        scenes = []
        for edit in clip["edits"]:
            seconds = int(edit["start_seconds"])
            scenes.append(
                f'<li><a href="{identifier}.mp4#t={seconds}">{seconds // 60:02}:{seconds % 60:02}</a> '
                f'{escape(edit["caption"]["ko"])}<br><span lang="en">{escape(edit["caption"]["en"])}</span></li>'
            )
        videos.append(
            f'<section id="{identifier}"><h2>{escape(clip["title"]["ko"])}'
            f' <small lang="en">{escape(clip["title"]["en"])}</small></h2>'
            f'<p>{escape(clip["note"]["ko"])}<br><span lang="en">{escape(clip["note"]["en"])}</span></p>'
            f'<video controls preload="none" playsinline data-recording="{identifier}" data-duration="{clip["seconds"]}" aria-label="{escape(clip["title"]["ko"])}">'
            f'<source src="{identifier}.mp4" type="video/mp4">'
            f'<track kind="subtitles" data-src="{identifier}.ko.vtt" srclang="ko" label="한국어" default>'
            f'<track kind="subtitles" data-src="{identifier}.en.vtt" srclang="en" label="English">'
            f'<a href="{identifier}.mp4">MP4 다운로드 / Download</a></video>'
            f'<p><a href="{identifier}.mp4" download>MP4</a> · '
            f'<a href="{identifier}.ko.vtt">한국어 VTT</a> · <a href="{identifier}.en.vtt">English VTT</a></p>'
            f'<details><summary>단계별 자막·시각 / Scene captions and timestamps</summary>'
            f'<ol>{"".join(scenes)}</ol></details></section>'
        )
    rows = []
    for row in source["coverage"]:
        chapter = titles[row["lab"]]
        status = STATUSES[row["status"]]
        links = " · ".join(f'<a href="#{clip}">{escape(clip)}</a>' for clip in row["clips"]) or "—"
        rows.append(
            f'<tr><th scope="row"><a href="../../index.ko.html#{row["lab"]}">L{chapter["number"]} '
            f'{escape(chapter["title"])}</a><br><span lang="en">{escape(en_titles[row["lab"]])}</span></th>'
            f'<td>{status[0]}<br><span lang="en">{status[1]}</span></td>'
            f'<td>{escape(row["note"]["ko"])}<br><span lang="en">{escape(row["note"]["en"])}</span></td>'
            f'<td>{links}</td></tr>'
        )
    captions = json.dumps({
        clip["id"]: [
            {"start": edit["start_seconds"], "end": edit["end_seconds"], "caption": edit["caption"]}
            for edit in clip["edits"]
        ] for clip in source["clips"]
    }, ensure_ascii=False).replace("<", "\\u003c")
    DESTINATION.mkdir(parents=True, exist_ok=True)
    (DESTINATION / "index.html").write_text(f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>실제 포털 실습 녹화 / Actual portal recordings</title>
<style>body{{font:16px/1.65 system-ui,sans-serif;max-width:1180px;margin:32px auto;padding:0 20px;background:#0b1c28;color:#eff8fc}}a{{color:#8ce5d8}}section{{margin:44px 0}}h2 small{{display:block;font-size:.7em}}video{{width:100%;background:#000}}table{{border-collapse:collapse;width:100%;font-size:.9em}}th,td{{border:1px solid #536a79;padding:12px;text-align:left;vertical-align:top}}td a{{overflow-wrap:anywhere}}th{{min-width:150px}}.table-scroll{{overflow-x:auto}}:focus-visible{{outline:3px solid #8ce5d8}}small,span[lang=en]{{color:#c1d4de}}</style></head>
<body><main><h1>실제 포털 실습 녹화<br><small lang="en">Actual Azure and Foundry portal recordings</small></h1>
<p><a href="../../index.ko.html">한국어 가이드</a> · <a href="../../index.html" lang="en">English guide</a>
 · <a href="../Contoso-Portal-Inputs.zip">포털 입력 ZIP / Portal inputs</a></p>
<p>촬영일 {escape(source["recorded_on"])}. 실제 로그인된 포털 화면을 녹화하고 대기·반복 구간을 잘랐습니다.
계정·식별자 영역은 자르거나 가렸습니다. <strong>무음 영상이며 한국어·영어 자막을 켜서 보세요.</strong>
각 단계의 전체 입력은 현재 가이드를 따르고, 화면을 멈춰 값을 대조하세요.</p>
<p lang="en">Genuine signed-in portal footage, trimmed to remove waits and repetition, with private areas cropped or redacted.
Silent videos include Korean and English subtitles. Pause to inspect values; follow the current guide for complete inputs.</p>
<p>로컬 파일로 열면 내장 자막을 사용합니다. 서버·CLI·브라우저 보안 설정 변경은 필요 없습니다.<br>
<span lang="en">Local files use embedded captions; no server, CLI, or browser security changes are needed.</span></p>
<p id="recording-link-status" role="status" hidden></p>
<noscript><p>JavaScript가 꺼져 있으면 아래 단계별 자막을 읽거나 MP4·VTT를 함께 내려받으세요.<br>
<span lang="en">Without JavaScript, read the scene captions below or download MP4 and VTT together.</span></p></noscript>
<p><strong>화면 관찰·수동 판단·미실행은 Azure 실행 성공이 아닙니다.</strong> 포털 점수는 기존 품질 ≥90%·safety/access 실패 0 게이트를 대체하지 않습니다.
표시된 비용 추정은 전체 Azure 청구액이 아닙니다. 자원은 삭제하지 않았으며 계속 비용이 발생할 수 있습니다.</p>
<p lang="en">Inspection, manual decisions, and not-run items are not successful Azure execution. Native scores do not replace
the unchanged business/safety gates. Displayed estimates are not total Azure billing. Resources are retained and may incur charges.</p>
<p><a href="../../content/portal-recordings.json">촬영·편집·해시·범위 provenance / Provenance</a>
 · <a href="evaluation-summary.json">실제 12쌍 응답·native 판정 / Actual twelve-pair evaluation</a>
 · <a href="../replay/index.html">과거 CLI 재구성 영상 — 현재 실습 아님 / Archived reconstruction</a></p>
<section id="portal-coverage"><h2>20모듈 수행 범위 / Coverage of all twenty modules</h2>
<div class="table-scroll"><table><thead><tr><th>모듈 / Module</th><th>수행 / Status</th><th>실제 범위·제한 / Scope and limits</th><th>영상 / Clip</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div></section>{''.join(videos)}</main>
<script type="application/json" id="portal-captions">{captions}</script>
<script>
"use strict";
// File-origin sidecar tracks are blocked; reuse the same cues without weakening browser security.
if (location.protocol === "file:") {{
  const captions = JSON.parse(document.getElementById("portal-captions").textContent);
  for (const video of document.querySelectorAll("video[data-recording]")) {{
    for (const element of video.querySelectorAll("track")) {{
      element.remove();
      const track = video.addTextTrack("subtitles", element.label, element.srclang);
      track.mode = "hidden";
      for (const cue of captions[video.dataset.recording]) {{
        track.addCue(new VTTCue(cue.start, cue.end, cue.caption[element.srclang]));
      }}
      track.mode = element.default ? "showing" : "disabled";
    }}
  }}
}} else {{
  for (const element of document.querySelectorAll("track[data-src]")) {{
    element.src = element.dataset.src;
  }}
}}
const params = new URLSearchParams(location.search);
if (["clip", "t", "lang"].some(key => params.has(key))) {{
  const status = document.getElementById("recording-link-status");
  const video = [...document.querySelectorAll("video[data-recording]")].find(
    item => item.dataset.recording === params.get("clip")
  );
  const seconds = Number(params.get("t"));
  const language = params.get("lang");
  const warn = () => {{
    status.hidden = false;
    status.dataset.state = "error";
    status.textContent = "영상 링크의 장면·시간·자막을 확인하세요. 아래 영상에서 직접 선택할 수 있습니다. / Invalid recording link or unavailable media. Select a clip below.";
    status.scrollIntoView();
  }};
  if (!["clip", "t", "lang"].every(key => params.getAll(key).length === 1)
      || !video || !/^\\d+(?:\\.\\d+)?$/.test(params.get("t"))
      || !Number.isFinite(seconds) || seconds < 0 || seconds >= Number(video.dataset.duration)
      || !["ko", "en"].includes(language)) {{
    warn();
  }} else {{
    video.addEventListener("error", warn, {{once: true}});
    video.addEventListener("loadedmetadata", () => {{
      if (!Number.isFinite(video.duration) || seconds >= video.duration) {{
        warn();
        return;
      }}
      for (const track of video.textTracks) {{
        track.mode = track.language === language ? "showing" : "disabled";
      }}
      const ready = () => {{
        if (Math.abs(video.currentTime - seconds) > .15) {{
          warn();
          return;
        }}
        video.closest("section").scrollIntoView();
        status.hidden = false;
        status.dataset.state = "ready";
        status.textContent = `선택한 장면 ${{seconds}}초 · ${{language}} 자막. 재생 버튼을 누르세요. / Selected ${{seconds}}s with ${{language}} captions. Press Play.`;
      }};
      if (seconds === 0) {{
        ready();
      }} else {{
        video.addEventListener("seeked", ready, {{once: true}});
        video.currentTime = seconds;
      }}
    }}, {{once: true}});
    video.preload = "metadata";
    video.load();
  }}
}}
</script></body></html>
""", encoding="utf-8")
    print(f"Built genuine portal recording index: {len(source['clips'])} clips, {len(rows)} module disclosures.")


if __name__ == "__main__":
    build()
