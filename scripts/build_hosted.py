"""Generate a self-contained, allowlisted code-deployment package, without cloud calls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / ".build/contoso"
sys.path.insert(0, str(ROOT / "samples"))
from evidence import runtime_contract
from workshop import config_values


def pinned_requirements(path: Path, seen: set[Path] | None = None) -> list[str]:
    seen = set() if seen is None else seen
    if path in seen or path.parent != ROOT:
        raise ValueError("Cyclic or external requirements are not allowed.")
    seen.add(path)
    lines = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("-r "):
            lines += pinned_requirements((ROOT / line[3:]).resolve(), seen)
        elif "==" in line and "://" not in line:
            lines.append(line)
        else:
            raise ValueError("Hosted dependencies must be exact package pins.")
    return sorted(set(lines))


def build() -> dict:
    files = [
        *sorted((ROOT / "data/policies").glob("*.md")),
        ROOT / "data/inventory.csv", ROOT / "data/prompts/agent-v1.txt",
        ROOT / "data/prompts/agent-v2.txt",
        ROOT / "data/prompts/agent-v3.txt",
        ROOT / "data/prompts/agent-v4.txt",
        *[ROOT / "samples" / name for name in ("workshop.py", "evidence.py", "cloud.py", "search_lab.py", "hosted_runtime.py")],
        ROOT / "requirements-hosted.txt", ROOT / "THIRD_PARTY_NOTICES",
    ]
    TARGET.mkdir(parents=True, exist_ok=True)
    old = TARGET / "package-manifest.json"
    if old.exists():
        previous = json.loads(old.read_text())
        if previous.get("schema") != "contoso-package-v1":
            raise ValueError("Refusing to replace an unrecognized package.")
        for name in previous["files"]:
            target = (TARGET / name).resolve()
            if not target.is_relative_to(TARGET.resolve()) or target.is_symlink():
                raise ValueError("Invalid previous package path.")
            target.unlink(missing_ok=True)
    elif any(TARGET.iterdir()):
        raise ValueError("The generated package directory is not empty and has no ownership manifest.")
    for path in files:
        if path.is_symlink():
            raise ValueError("Symlinks are not allowed in a deployable package.")
        target = TARGET / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    shutil.copy2(ROOT / "hosted/main.py", TARGET / "main.py")
    shutil.copy2(ROOT / "hosted/responses_main.py", TARGET / "responses_main.py")
    shutil.copy2(ROOT / "hosted/.agentignore", TARGET / ".agentignore")
    (TARGET / "requirements.txt").write_text("\n".join(pinned_requirements(ROOT / "requirements-hosted.txt")) + "\n")
    model = config_values()["FOUNDRY_MODEL_DEPLOYMENT_NAME"] or "CONFIGURE-MODEL-BEFORE-DEPLOY"
    baseline = TARGET / ".agent_configs/baseline"
    baseline.mkdir(parents=True, exist_ok=True)
    (baseline / "metadata.yaml").write_text(f"model: {json.dumps(model)}\ninstruction_file: instructions.md\n")
    shutil.copy2(ROOT / "data/prompts/agent-v4.txt", baseline / "instructions.md")
    entries = {
        path.relative_to(TARGET).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(TARGET.rglob("*")) if path.is_file() and path.name != "package-manifest.json"
        and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }
    forbidden = {".env", "results", "evaluation", ".git", ".azure", ".foundry", "validation"}
    if any(set(Path(name).parts) & forbidden for name in entries):
        raise ValueError("Sensitive/local/evaluation state must not enter the Hosted package.")
    manifest = {"schema": "contoso-package-v1", "files": entries, "runtime_contract": runtime_contract(root=TARGET)}
    old.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    with zipfile.ZipFile(ROOT / ".build/contoso-code.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for name in [*entries, "package-manifest.json"]:
            archive.write(TARGET / name, name)
    print(json.dumps({"files": len(entries), "contract": manifest["runtime_contract"]["sha256"], "path": ".build/contoso"}))
    return manifest


if __name__ == "__main__":
    build()
