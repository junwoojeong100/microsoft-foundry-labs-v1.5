"""Build bilingual narrated guide videos locally; never reads Azure execution evidence."""

import argparse
import html
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content/replay.json"


def run(command):
    subprocess.run(command, cwd=ROOT, check=True, timeout=1200)


def duration(path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
        check=True, capture_output=True, text=True, timeout=30,
    )
    return float(json.loads(result.stdout)["format"]["duration"])


def timestamp(seconds, separator=","):
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    whole, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{whole:02}{separator}{milliseconds:03}"


def build(language, source, work, destination):
    chapters = json.loads((ROOT / f"content/chapters{'.en' if language == 'en' else ''}.json").read_text())
    base = json.loads((ROOT / "content/chapters.json").read_text())
    expected = [chapter["id"] for chapter in base if chapter["track"] != "reference"]
    if [chapter["id"] for chapter in source["chapters"]] != expected or len(expected) != 20:
        raise ValueError("The video must cover exactly the twenty current modules in reader order.")
    titles = {chapter["id"]: chapter["title"] for chapter in chapters}
    numbers = {chapter["id"]: chapter["number"] for chapter in base}
    folder = work / language
    folder.mkdir(parents=True, exist_ok=True)
    run(["node", "scripts/render-replay.js", language, str(folder)])
    captions, vtt, timeline, segments = [], ["WEBVTT\n"], [], []
    position = 0.0
    caption_number = 0
    voice = "Yuna" if language == "ko" else "Samantha"
    for chapter in source["chapters"]:
        identifier = chapter["id"]
        narration = folder / f"{identifier}.txt"
        narration.write_text(chapter[language]["narration"], encoding="utf-8")
        audio = folder / f"{identifier}.aiff"
        run(["say", "-v", voice, "-r", "165", "-f", str(narration), "-o", str(audio)])
        length = duration(audio) + 0.7
        if length < 10:
            raise ValueError(f"{language}/{identifier}: incomplete narration.")
        frames = folder / f"{identifier}.frames.txt"
        frames.write_text(
            "".join(f"file '{identifier}-{step}.png'\nduration {length / 3:.6f}\n" for step in range(3))
            + f"file '{identifier}-2.png'\n", encoding="utf-8",
        )
        clip = folder / f"{identifier}.mp4"
        run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(frames),
            "-i", str(audio), "-t", f"{length:.6f}", "-vf", "fps=30,format=yuv420p",
            "-af", "apad", "-c:v", "libx264", "-preset", "fast", "-crf", "24", "-threads", "2",
            "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "1", str(clip),
        ])
        actual = duration(clip)
        timeline.append({"id": identifier, "number": numbers[identifier], "title": titles[identifier],
                         "start": round(position, 3), "end": round(position + actual, 3)})
        sentences = chapter[language]["narration"].split(". ")
        weights = [max(1, len(sentence)) for sentence in sentences]
        cursor = position
        for index, sentence in enumerate(sentences):
            end = min(position + actual, cursor + actual * weights[index] / sum(weights))
            caption_number += 1
            caption = sentence if sentence.endswith(".") else sentence + "."
            captions.append(f"{caption_number}\n{timestamp(cursor)} --> {timestamp(end)}\n{caption}\n")
            vtt.append(f"{timestamp(cursor, '.')} --> {timestamp(end, '.')}\n{caption}\n")
            cursor = end
        position += actual
        segments.append(clip)
    concat = folder / "segments.txt"
    concat.write_text("".join(f"file '{clip.name}'\n" for clip in segments), encoding="utf-8")
    metadata = folder / "chapters.txt"
    metadata.write_text(
        ";FFMETADATA1\n" + "".join(
            f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(item['start'] * 1000)}\n"
            f"END={round(item['end'] * 1000)}\ntitle=L{item['number']} {item['title']}\n"
            for item in timeline
        ), encoding="utf-8",
    )
    target = destination / f"Contoso-Foundry-Replay.{language}.mp4"
    subtitles = destination / f"Contoso-Foundry-Replay.{language}.srt"
    subtitles.write_text("\n".join(captions), encoding="utf-8")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
         "-i", str(concat), "-i", str(metadata), "-i", str(subtitles),
         "-map", "0:v", "-map", "0:a", "-map", "2:0", "-map_metadata", "1", "-map_chapters", "1",
         "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text", "-metadata:s:s:0",
         "language=" + ("kor" if language == "ko" else "eng"), "-disposition:s:0", "default",
         "-movflags", "+faststart", str(target)])
    (destination / f"Contoso-Foundry-Replay.{language}.vtt").write_text("\n".join(vtt), encoding="utf-8")
    (destination / f"chapters.{language}.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + "\n")
    return {"language": language, "file": target.name, "seconds": round(duration(target), 3),
            "chapters": len(timeline), "width": 1920, "height": 1080, "narration_voice": voice,
            "scope": source["notice"][language]}


def player(source, destination):
    title = "Contoso Foundry · 실습 요약 / Lab walkthrough"
    links = []
    for language in ("ko", "en"):
        chapters = json.loads((destination / f"chapters.{language}.json").read_text())
        buttons = "".join(
            f'<button type="button" data-language="{language}" data-time="{chapter["start"]}">'
            f'L{chapter["number"]} · {html.escape(chapter["title"])}</button>' for chapter in chapters
        )
        label = "한국어" if language == "ko" else "English"
        name = f"Contoso-Foundry-Replay.{language}"
        links.append(f"""<section lang="{language}"><h2>{label}</h2><p>{html.escape(source["notice"][language])}</p>
<video id="{language}" controls preload="metadata"><source src="{name}.mp4" type="video/mp4">
<track kind="subtitles" src="{name}.vtt" srclang="{language}" label="{label}"></video>
<p><a href="{name}.mp4" download>MP4</a> · <a href="{name}.srt" download>SRT</a> · <a href="chapters.{language}.json">Chapters</a></p>
<nav aria-label="{label} chapters">{buttons}</nav></section>""")
    (destination / "index.html").write_text(f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>body{{font:16px/1.6 system-ui,sans-serif;max-width:1160px;margin:32px auto;padding:0 20px;background:#081925;color:#e8f3f8}}a{{color:#66e0cb}}video{{width:100%;background:#000}}section{{margin:40px 0 70px}}nav{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:8px}}button{{background:#143344;border:1px solid #406170;color:#e8f3f8;padding:12px;text-align:left;cursor:pointer;border-radius:8px}}button:focus-visible{{outline:3px solid #66e0cb}}</style></head>
<body><h1>{title}</h1><p>20개 모듈 · 음성 내레이션 · 자막 · 장별 이동 / 20 modules · narration · captions · chapter navigation</p>
{''.join(links)}
<script>document.querySelectorAll('button[data-time]').forEach(button=>button.addEventListener('click',()=>{{const video=document.getElementById(button.dataset.language);video.currentTime=Number(button.dataset.time);video.scrollIntoView({{block:'center'}});video.play().catch(error=>{{if(error.name!=='NotAllowedError')console.error(error);}});}}));</script></body></html>""", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=["ko", "en", "both"], default="both")
    args = parser.parse_args()
    for tool in ("node", "ffmpeg", "ffprobe", "say"):
        if not shutil.which(tool):
            raise RuntimeError(f"Missing {tool}. This local renderer needs macOS voices, FFmpeg, and the declared Playwright dependency.")
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    work, destination = ROOT / ".build/replay-media", ROOT / "downloads/replay"
    destination.mkdir(parents=True, exist_ok=True)
    results = []
    for language in ("ko", "en") if args.language == "both" else (args.language,):
        results.append(build(language, source, work, destination))
    if all((destination / f"chapters.{language}.json").exists() for language in ("ko", "en")):
        player(source, destination)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
