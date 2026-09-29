"""Check public documentation URLs only; does not authenticate to Azure."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import ssl
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def inspect_url(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "FoundryLabGuide-LinkCheck/1.0"})
    try:
        with urlopen(request, timeout=35) as response:
            page = response.read(1_500_000).decode("utf-8", errors="replace")
            title = re.search(r"<title[^>]*>(.*?)</title>", page, re.S | re.I)
            modified = re.search(r'<meta\s+name="ms.date"\s+content="([^"]+)"', page, re.I)
            text_title = re.sub(r"\s+", " ", title.group(1)).strip() if title else ""
            ok = response.status == 200 and not re.search(r"(^404\b|Page not found)", text_title, re.I)
            return {
                "url": url, "final_url": response.url, "http_status": response.status,
                "reachable": ok, "title": text_title,
                "document_ms_date": modified.group(1) if modified else None,
            }
    except HTTPError as error:
        return {"url": url, "reachable": False, "http_status": error.code, "error": error.reason}
    except (URLError, TimeoutError, ssl.SSLError, OSError) as error:
        return {"url": url, "reachable": False, "http_status": None, "error": str(error)}


def main() -> int:
    source_data = json.loads((ROOT / "content/sources.json").read_text(encoding="utf-8"))
    urls = {urldefrag(source["url"])[0] for source in source_data["sources"]}
    for path in (ROOT / "docs").glob("*.md"):
        for address in re.findall(r"\]\((https://[^\s)]+)\)", path.read_text(encoding="utf-8")):
            if urlparse(address).hostname == "learn.microsoft.com":
                urls.add(urldefrag(address)[0])
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(inspect_url, sorted(urls)))
    failed = [row for row in results if not row["reachable"]]
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Unauthenticated GET requests to public Microsoft Learn source URLs. HTTP reachability is not feature or Azure execution validation.",
        "checked": len(results), "passed": len(results) - len(failed), "failed": len(failed), "links": results,
    }
    target = ROOT / "validation/current/links.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Public source URLs: {report['passed']}/{report['checked']} reachable; report={target.relative_to(ROOT)}")
    for row in failed:
        print(f"FAILED {row['http_status']} {row['url']}: {row.get('error', row.get('title'))}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
