"""Create a portable kit without virtualenvs, generated cloud results, or credentials."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = json.loads((ROOT / "content/release.json").read_text())["artifact"]


def main():
    files = [
        ROOT / name for name in (
            "README.md", "index.html", "GUIDE.ko.md", f"{NAME}.pdf",
            ".env.example", ".gitignore", "requirements.txt",
            "requirements-docs.txt", "requirements-advanced.txt", "requirements-qa.txt",
            "requirements-hosted.txt", "requirements-tools.txt", "requirements-live.lock.txt",
            "package.json", "package-lock.json", ".python-version", "azure.yaml", "AGENTS.md", "THIRD_PARTY_NOTICES",
        )
    ]
    for name in ("assets", "content", "data", "docs", "samples", "scripts", "tests", "hosted", "infra", "validation/current", ".github/workflows"):
        files.extend(
            path for path in (ROOT / name).rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix not in {".pyc", ".tmp"}
            and path != ROOT / "validation/current/package.json"
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
        for essential in ("index.html", "GUIDE.ko.md", f"{NAME}.pdf", "samples/workshop.py", "data/evaluation/cases.jsonl"):
            if f"{NAME}/{essential}" not in names:
                raise ValueError(f"Missing package artifact: {essential}")
    print(f"Packaged {len(names)} files: {target.name} ({target.stat().st_size / 1_000_000:.2f} MB)")
    report = {
        "created_at": datetime.now(timezone.utc).isoformat(), "archive": target.name,
        "files": len(names), "bytes": target.stat().st_size,
        "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "integrity": "passed", "credential_and_virtualenv_exclusion": "passed",
        "note": "This archive hash is kept outside the archive to avoid a self-referential checksum.",
    }
    (ROOT / "validation/current/package.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
