"""Check that executable surfaces are self-contained and current data is Contoso."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TEXT = {".py", ".txt", ".json", ".jsonl", ".md", ".js", ".yaml", ".yml", ".html", ".svg", ".bicep", ".sh"}


def check(root: Path = ROOT) -> dict:
    executable = [
        *[root / name for name in ("azure.yaml", "package.json")],
        *root.glob("requirements*.txt"),
        *[path for folder in ("samples", "scripts", "infra", "hosted", ".github", ".devcontainer") for path in (root / folder).rglob("*") if path.suffix in TEXT],
    ]
    # Learner-facing text must not point at the archived reference either (THIRD_PARTY_NOTICES and AGENTS.md name it on purpose).
    learner_facing = [
        *[root / name for name in ("README.md", "README.ko.md")],
        *[path for folder in ("docs", "content", "data", "assets") for path in (root / folder).rglob("*") if path.suffix in TEXT],
    ]
    forbidden_references = ("microsoft-" + "foundry-labs-v1.3", "eda75fa7f8a8d3548d21" + "c919d5c0b836c7d818e4")
    for path in [*executable, *learner_facing]:
        text = path.read_text(encoding="utf-8")
        if any(reference in text for reference in forbidden_references):
            raise ValueError(f"Reference repository appears in a surface that must be self-contained: {path.relative_to(root)}")
        if re.search(r"/Users/[A-Za-z0-9_.-]+/|\.{2}/\.{2}/.*foundry-labs", text):
            raise ValueError(f"Personal/external filesystem dependency: {path.relative_to(root)}")
    if (root / ".gitmodules").exists():
        raise ValueError("This workshop must not depend on git submodules.")
    for folder in ("docs", "data", "assets"):
        for path in (root / folder).rglob("*"):
            if path.suffix not in TEXT:
                continue
            text = path.read_text(encoding="utf-8")
            if re.search("한빛|Hanbit|hanbit|HB-|hb-", text):
                raise ValueError(f"Stale current-scenario name: {path.relative_to(root)}")
    return {"executable_files_checked": len(executable), "learner_facing_files_checked": len(learner_facing),
            "reference_repository_dependencies": 0, "personal_paths": 0, "current_branding": "Contoso"}


if __name__ == "__main__":
    import json
    print(json.dumps(check(), ensure_ascii=False, indent=2))
