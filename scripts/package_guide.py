"""Create a portable kit without virtualenvs, generated cloud results, or credentials."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlparse
import zipfile

from check_guide import GuideParser
from build_guide import load_portal_captures

ROOT = Path(__file__).resolve().parents[1]
RELEASE = json.loads((ROOT / "content/release.json").read_text())
NAME = RELEASE["artifact"]


def check_package_path(path):
    parts = Path(path).parts
    if any(
        part.startswith(".venv") or part in {"__pycache__", "results", ".azure", ".git", ".foundry", "node_modules"}
        for part in parts
    ) or parts[-1] == ".env":
        raise ValueError(f"Private or generated cloud data in package: {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-dir", type=Path, default=Path(RELEASE["documentation_validation"]))
    args = parser.parse_args()
    report_dir = (ROOT / args.report_dir).resolve()
    if not report_dir.is_relative_to(ROOT / "validation") or report_dir == ROOT / "validation":
        raise ValueError("Reports must be inside validation/.")
    files = [
        ROOT / name for name in (
            ".nojekyll",
            ".env.example", ".gitignore", "requirements.txt",
            "requirements-docs.txt", "requirements-advanced.txt", "requirements-local.txt", "requirements-qa.txt",
            "requirements-hosted.txt", "requirements-tools.txt", "requirements-live.lock.txt",
            "package.json", "package-lock.json", ".python-version", "azure.yaml", "AGENTS.md", "THIRD_PARTY_NOTICES",
        )
    ]
    for edition in RELEASE["languages"].values():
        files.extend(ROOT / edition[key] for key in ("readme", "html", "markdown", "pdf", "receipt_html", "validation"))
        files.append(ROOT / "content" / edition["portal_manifest"])
    directories = ("assets", "content", "data", "docs", "samples", "scripts", "tests", "hosted", "infra", "validation/current", RELEASE["documentation_validation"], ".github/workflows")
    for directory in {*(ROOT / name for name in directories), report_dir}:
        files.extend(
            path for path in directory.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix not in {".pyc", ".tmp"}
            and path != report_dir / "package.json"
        )
    for path in files:
        check_package_path(path.relative_to(ROOT))
        if not path.is_file() or any(
            part.is_symlink() for part in (path, *path.parents) if part.is_relative_to(ROOT)
        ):
            raise ValueError(f"Package input must be an existing regular file: {path.relative_to(ROOT)}")
    captures = {language: load_portal_captures(language) for language in RELEASE["languages"]}
    target = ROOT / RELEASE["archive"]
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(set(files)):
            archive.write(path, f"{NAME}/{path.relative_to(ROOT).as_posix()}")
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:
            raise ValueError("Archive integrity check failed.")
        names = archive.namelist()
        for name in names:
            check_package_path(name)
        essentials = [
            edition[key] for edition in RELEASE["languages"].values()
            for key in ("readme", "html", "markdown", "pdf", "receipt_html", "validation")
        ]
        essentials += ["content/" + edition["portal_manifest"] for edition in RELEASE["languages"].values()]
        for essential in (*essentials, "samples/workshop.py", "data/evaluation/cases.jsonl"):
            if f"{NAME}/{essential}" not in names:
                raise ValueError(f"Missing package artifact: {essential}")
        local_paths = set()
        for edition in RELEASE["languages"].values():
            book = ROOT / edition["markdown"]
            for address in re.findall(r"\]\(([^)\s]+)\)", book.read_text(encoding="utf-8")):
                parsed = urlparse(address)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                path = (book.parent / unquote(parsed.path)).resolve()
                if not path.is_relative_to(ROOT):
                    raise ValueError(f"Portable Markdown link escapes the kit: {address}")
                local_paths.add(path.relative_to(ROOT).as_posix())
            for key in ("html", "receipt_html"):
                parser = GuideParser()
                parser.feed((ROOT / edition[key]).read_text(encoding="utf-8"))
                for address in [*parser.links, *(image["src"] for image in parser.images)]:
                    parsed = urlparse(address)
                    if parsed.scheme or parsed.netloc or not parsed.path:
                        continue
                    path = (ROOT / Path(edition[key]).parent / unquote(parsed.path)).resolve()
                    if not path.is_relative_to(ROOT):
                        raise ValueError(f"Portable guide link escapes the kit: {address}")
                    relative = path.relative_to(ROOT).as_posix()
                    if relative != RELEASE["archive"]:
                        local_paths.add(relative)
        for local_path in local_paths:
            if f"{NAME}/{local_path}" not in names:
                raise ValueError(f"Portable guide link missing from ZIP: {local_path}")
        for localized_captures in captures.values():
            for capture in localized_captures:
                packed = archive.read(f"{NAME}/{capture['path']}")
                if hashlib.sha256(packed).hexdigest() != capture["sha256"]:
                    raise ValueError(f"Portal screenshot differs in ZIP: {capture['path']}")
    print(f"Packaged {len(names)} files: {target.name} ({target.stat().st_size / 1_000_000:.2f} MB)")
    report = {
        "created_at": datetime.now(timezone.utc).isoformat(), "archive": target.name,
        "files": len(names), "bytes": target.stat().st_size,
        "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "languages": list(RELEASE["languages"]), "default_language": RELEASE["default_language"],
        "integrity": "passed", "credential_and_virtualenv_exclusion": "passed",
        "portable_local_paths_checked": len(local_paths),
        "portal_screenshots": sum(len(items) for items in captures.values()),
        "portal_screenshots_by_language": {language: len(items) for language, items in captures.items()},
        "note": "This archive hash is kept outside the archive to avoid a self-referential checksum.",
    }
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "package.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
