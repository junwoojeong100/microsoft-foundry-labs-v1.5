"""Create a portable kit without virtualenvs, generated cloud results, or credentials."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.parse import unquote, urlparse
import zipfile

from check_guide import GuideParser

ROOT = Path(__file__).resolve().parents[1]
RELEASE = json.loads((ROOT / "content/release.json").read_text())
NAME = RELEASE["artifact"]


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
            "requirements-docs.txt", "requirements-advanced.txt", "requirements-qa.txt",
            "requirements-hosted.txt", "requirements-tools.txt", "requirements-live.lock.txt",
            "package.json", "package-lock.json", ".python-version", "azure.yaml", "AGENTS.md", "THIRD_PARTY_NOTICES",
        )
    ]
    for edition in RELEASE["languages"].values():
        files.extend(ROOT / edition[key] for key in ("readme", "html", "markdown", "pdf"))
    directories = ("assets", "content", "data", "docs", "samples", "scripts", "tests", "hosted", "infra", "validation/current", "validation/automated-v3", RELEASE["documentation_validation"], ".github/workflows")
    for directory in {*(ROOT / name for name in directories), report_dir}:
        files.extend(
            path for path in directory.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix not in {".pyc", ".tmp"}
            and path != report_dir / "package.json"
        )
    if not all(path.is_file() and not path.is_symlink() for path in files):
        raise ValueError("Package inputs must be existing regular files.")
    target = ROOT / f"{NAME}.zip"
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(set(files)):
            archive.write(path, f"{NAME}/{path.relative_to(ROOT).as_posix()}")
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:
            raise ValueError("Archive integrity check failed.")
        names = archive.namelist()
        for name in names:
            parts = Path(name).parts
            if any(part.startswith(".venv") or part in {"__pycache__", "results", ".azure", ".git", ".foundry", "node_modules"} for part in parts) or parts[-1] == ".env":
                raise ValueError(f"Private or generated cloud data in archive: {name}")
        essentials = [
            edition[key] for edition in RELEASE["languages"].values()
            for key in ("readme", "html", "markdown", "pdf")
        ]
        for essential in (*essentials, "samples/workshop.py", "data/evaluation/cases.jsonl"):
            if f"{NAME}/{essential}" not in names:
                raise ValueError(f"Missing package artifact: {essential}")
        parser = GuideParser()
        for edition in RELEASE["languages"].values():
            parser.feed((ROOT / edition["html"]).read_text(encoding="utf-8"))
        local_paths = {
            unquote(parsed.path)
            for address in [*parser.links, *(image["src"] for image in parser.images)]
            if not (parsed := urlparse(address)).scheme and not parsed.netloc and parsed.path
        }
        for local_path in local_paths:
            if f"{NAME}/{local_path}" not in names:
                raise ValueError(f"Portable guide link missing from ZIP: {local_path}")
        captures = json.loads((ROOT / "content/portal-screenshots.json").read_text(encoding="utf-8"))["captures"]
        for capture in captures:
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
        "portable_local_paths_checked": len(local_paths), "portal_screenshots": len(captures),
        "note": "This archive hash is kept outside the archive to avoid a self-referential checksum.",
    }
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "package.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
