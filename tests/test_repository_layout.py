import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from urllib.parse import urlparse
import zipfile

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.name == "posix" and shutil.which("bash"), "Codespaces bootstrap targets Linux/Bash.")
class CodespacesSetupTests(unittest.TestCase):
    def prepare(self, root):
        (root / ".devcontainer").mkdir()
        shutil.copyfile(ROOT / ".devcontainer/post-create.sh", root / ".devcontainer/post-create.sh")
        (root / ".env.example").write_text("SYNTHETIC_SETTING=template\n")
        tools = root / "bin"
        tools.mkdir()
        python = tools / "python3.13"
        python.write_text(textwrap.dedent("""\
            #!/usr/bin/env bash
            set -eu
            printf '%s\\n' "$*" >> "$CALL_LOG"
            if [[ "$1" == "-m" && "$2" == "venv" ]]; then
              mkdir -p "$3/bin"
              cp "$0" "$3/bin/python"
            elif [[ "$1" == "-c" ]]; then
              exit "${WRONG_PYTHON:-0}"
            elif [[ "$1" == "-m" && "$2" == "pip" && "$3" == "install" ]]; then
              exit "${INSTALL_FAILURE:-0}"
            fi
        """))
        python.chmod(0o755)
        for name in ("az", "azd", "gh", "curl", "wget"):
            tool = tools / name
            tool.write_text("#!/bin/sh\nprintf 'Unexpected remote tool: %s\\n' \"$0\" >&2\nexit 96\n")
            tool.chmod(0o755)
        return {**os.environ, "PATH": str(tools) + os.pathsep + os.environ["PATH"],
                "CALL_LOG": str(root / "calls.log"), "WRONG_PYTHON": "0", "INSTALL_FAILURE": "0"}

    def run_setup(self, root, env):
        return subprocess.run(
            ["bash", str(root / ".devcontainer/post-create.sh")],
            cwd=root, env=env, text=True, capture_output=True, timeout=10,
        )

    def test_setup_and_resume_preserve_private_settings_and_receipts(self):
        with tempfile.TemporaryDirectory(prefix="codespaces setup ") as folder:
            root = Path(folder)
            env = self.prepare(root)
            first = self.run_setup(root, env)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual((root / ".env").read_text(), "SYNTHETIC_SETTING=template\n")
            (root / ".env").write_text("SYNTHETIC_SETTING=keep-my-value\n")
            (root / "results").mkdir()
            receipt = root / "results/azure-environment.json"
            receipt.write_text('{"synthetic":true,"keep":true}\n')
            second = self.run_setup(root, env)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertIn("Lab tools ready.", second.stdout)
            self.assertEqual((root / ".env").read_text(), "SYNTHETIC_SETTING=keep-my-value\n")
            self.assertEqual(receipt.read_text(), '{"synthetic":true,"keep":true}\n')
            calls = (root / "calls.log").read_text().splitlines()
            self.assertEqual(calls.count("-m venv .venv"), 1)
            self.assertIn("-m pip install -r requirements-tools.txt", calls)
            self.assertIn("-m pip check", calls)

    def test_setup_failures_stop_without_claiming_readiness(self):
        for failure in ("WRONG_PYTHON", "INSTALL_FAILURE"):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                env = self.prepare(root)
                env[failure] = "37"
                result = self.run_setup(root, env)
                self.assertEqual(result.returncode, 37, result.stderr)
                self.assertNotIn("Lab tools ready.", result.stdout)
                self.assertFalse((root / ".env").exists())
                calls = (root / "calls.log").read_text()
                self.assertNotIn("-m pip check", calls)
                if failure == "WRONG_PYTHON":
                    self.assertNotIn("-m pip install", calls)


class RepositoryLayoutTests(unittest.TestCase):
    def test_distributions_exclude_pdf_documents(self):
        with self.subTest(distribution="downloads"):
            self.assertEqual(list((ROOT / "downloads").rglob("*.pdf")), [])
        for path in (ROOT / "downloads").glob("*.zip"):
            with self.subTest(distribution=path.name), zipfile.ZipFile(path) as archive:
                self.assertFalse(any(name.lower().endswith(".pdf") for name in archive.namelist()))

    def test_only_current_distributions_are_present(self):
        release = json.loads((ROOT / "content/release.json").read_text())
        self.assertLessEqual(
            {path.name for path in (ROOT / "downloads").glob("*Foundry*Hands-on*.zip")},
            {Path(release["archive"]).name},
        )
        self.assertEqual(
            {path.name for path in (ROOT / "downloads").glob("GUIDE*.md")},
            {Path(edition["markdown"]).name for edition in release["languages"].values()},
        )
        self.assertTrue(all(
            Path(edition["markdown"]).parent == Path("downloads") for edition in release["languages"].values()
        ))
        self.assertEqual(Path(release["archive"]).parent, Path("downloads"))
        self.assertFalse((ROOT / "assets/favicon.svg").exists())

    def test_validation_has_no_superseded_snapshots(self):
        release = json.loads((ROOT / "content/release.json").read_text())
        self.assertEqual(release["documentation_validation"], "results/documentation")
        self.assertFalse(list((ROOT / "validation").rglob("*.json")))
        self.assertNotIn("validation", release)
        self.assertTrue(all("validation" not in edition for edition in release["languages"].values()))

    def test_readme_html_link_opens_github_pages(self):
        readme = (ROOT / "README.md").read_text()
        links = re.findall(r"\[[^\]]*index\.html[^\]]*\]\(([^)]+)\)", readme)
        self.assertEqual(links, ["https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/"])
        self.assertNotRegex(readme, r"\]\((?:\./)?index\.html(?:[)#])")

    def test_pages_publishes_main_and_preserves_runtime_workflow_links(self):
        release = json.loads((ROOT / "content/release.json").read_text())
        readme = (ROOT / "README.md").read_text()
        korean = (ROOT / "README.ko.md").read_text()
        delivery = (ROOT / "docs/22-delivery.md").read_text()
        self.assertEqual(release["pages_branch"], "main")
        self.assertIn(f"**root of the `{release['pages_branch']}` branch**", readme)
        self.assertIn("**`main` 브랜치의 루트(`/`)**", korean)
        self.assertIn("Merging into `main`", readme)
        self.assertIn("automatically publishes", readme)
        self.assertIn("Pages does not wait for validation to finish", readme)
        self.assertIn("Pages는 자동 검사가 끝나기를 기다리지 않습니다", korean)
        self.assertNotIn("docs/portal-walkthrough-20260930", readme + delivery)
        links = re.findall(r"\]\((https://github\.com/[^)]+/\.github/workflows/[^)]+)\)", delivery)
        self.assertEqual(len(links), 2)
        self.assertTrue(all("/blob/main/.github/workflows/" in link for link in links))


if __name__ == "__main__":
    unittest.main()
