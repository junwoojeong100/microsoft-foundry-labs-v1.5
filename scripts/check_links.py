"""Check public documentation URLs only; does not authenticate to Azure."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import ssl
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


RETRY_STATUS = {429, 500, 502, 503, 504}


def inspect_once(url: str) -> dict:
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


def inspect_url(url: str, attempts: int = 3) -> dict:
    """Retry rate limits, server errors and network hiccups so a transient failure is not reported as a broken link."""
    for attempt in range(attempts):
        result = inspect_once(url)
        if result["reachable"] or (result["http_status"] is not None and result["http_status"] not in RETRY_STATUS):
            return result
        if attempt + 1 < attempts:
            time.sleep(2 ** attempt)
    return result


def changed_since_review(results: list[dict], review_date: str) -> list[dict]:
    """Pages whose Learn `ms.date` is later than the guide's last source review need a fresh read."""
    return sorted(
        ({"url": row["url"], "document_ms_date": row["document_ms_date"][:10]}
         for row in results if row.get("document_ms_date") and row["document_ms_date"][:10] > review_date),
        key=lambda row: (row["document_ms_date"], row["url"]), reverse=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fail-on-changed", action="store_true",
                        help="Also fail when a cited page changed after the recorded source review date.")
    args = parser.parse_args()
    source_data = json.loads((ROOT / "content/sources.json").read_text(encoding="utf-8"))
    urls = {urldefrag(source["url"])[0] for source in source_data["sources"]}
    for path in [*(ROOT / "docs").glob("*.md"), *(ROOT / "docs/en").glob("*.md")]:
        for address in re.findall(r"\]\((https://[^\s)]+)\)", path.read_text(encoding="utf-8")):
            if urlparse(address).hostname == "learn.microsoft.com":
                urls.add(urldefrag(address)[0])
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(inspect_url, sorted(urls)))
    failed = [row for row in results if not row["reachable"]]
    review_date = max(source_data.get("checked_on", ""), source_data.get("execution_api_rechecked_on", ""))
    changed = changed_since_review(results, review_date) if review_date else []
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Unauthenticated GET requests to public Microsoft Learn source URLs. HTTP reachability is not feature or Azure execution validation.",
        "checked": len(results), "passed": len(results) - len(failed), "failed": len(failed),
        "source_review_date": review_date, "changed_since_review": changed, "links": results,
    }
    release = json.loads((ROOT / "content/release.json").read_text(encoding="utf-8"))
    target = ROOT / release["documentation_validation"] / "links.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Public source URLs: {report['passed']}/{report['checked']} reachable; report={target.relative_to(ROOT)}")
    for row in failed:
        print(f"FAILED {row['http_status']} {row['url']}: {row.get('error', row.get('title'))}")
    if changed:
        print(f"{len(changed)} cited pages changed after the {review_date} source review; read them again before the next release:")
        for row in changed:
            print(f"  {row['document_ms_date']} {row['url']}")
    return 1 if failed or (changed and args.fail_on_changed) else 0


if __name__ == "__main__":
    raise SystemExit(main())
