"""Verify every published guide HTML and its assets on this repository's GitHub Pages site."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.parse import quote, unquote, urljoin, urlparse
from urllib.request import Request, urlopen

from check_guide import GuideParser

ROOT = Path(__file__).resolve().parents[1]
RELEASE = json.loads((ROOT / "content/release.json").read_text(encoding="utf-8"))


def fetch(address):
    request = Request(address, headers={
        "User-Agent": "ContosoGuide-PagesCheck/1.0",
        "Cache-Control": "no-cache",
    })
    with urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise ValueError(f"Published file returned HTTP {response.status}: {address}")
        return response.read()


def check():
    base = RELEASE["site_url"]
    if base != "https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/":
        raise ValueError("Pages checks must target this repository's public site.")
    html_files = {
        edition["html"] for edition in RELEASE["languages"].values()
    } | {path.relative_to(ROOT).as_posix() for path in (ROOT / "data").rglob("*.html")}
    local_files = set()
    rows = []
    for relative in sorted(html_files):
        address = urljoin(base, quote(relative))
        published = fetch(address)
        local = (ROOT / relative).read_bytes()
        if published != local:
            raise ValueError(f"Published HTML differs from the generated source: {address}")
        parser = GuideParser()
        parser.feed(published.decode("utf-8"))
        for link in [*parser.links, *(image["src"] for image in parser.images)]:
            parsed = urlparse(link)
            if not parsed.scheme and not parsed.netloc and parsed.path:
                path = (Path(relative).parent / unquote(parsed.path)).as_posix()
                local_files.add(path)
        rows.append({
            "url": address, "http_status": 200, "language": parser.language,
            "sections": len(parser.articles), "sha256": hashlib.sha256(published).hexdigest(),
            "matches_generated_source": True,
        })
    default = fetch(base)
    if default != (ROOT / RELEASE["languages"][RELEASE["default_language"]]["html"]).read_bytes():
        raise ValueError("The public site root does not serve the default English reader.")
    assets = sorted(path for path in local_files if path not in html_files and not path.endswith((".pdf", ".zip")))
    for relative in assets:
        path = (ROOT / relative).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise ValueError(f"Unexpected linked public file: {relative}")
        if fetch(urljoin(base, quote(relative))) != path.read_bytes():
            raise ValueError(f"Published asset differs from the local source: {relative}")
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Unauthenticated GitHub Pages requests only; not Azure execution or quality evidence.",
        "site_url": base, "default_language": RELEASE["default_language"],
        "html": rows, "linked_files_checked": len(assets), "status": "passed",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    check()
