import json
from pathlib import Path
import re
import unittest
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


class RepositoryLayoutTests(unittest.TestCase):
    def test_only_current_distributions_are_present(self):
        release = json.loads((ROOT / "content/release.json").read_text())
        self.assertEqual(
            {path.name for path in (ROOT / "downloads").glob("*Foundry*Hands-on*.pdf")},
            {Path(edition["pdf"]).name for edition in release["languages"].values()},
        )
        self.assertLessEqual(
            {path.name for path in (ROOT / "downloads").glob("*Foundry*Hands-on*.zip")},
            {Path(release["archive"]).name},
        )
        self.assertEqual(
            {path.name for path in (ROOT / "downloads").glob("GUIDE*.md")},
            {Path(edition["markdown"]).name for edition in release["languages"].values()},
        )
        for key in ("markdown", "pdf"):
            self.assertTrue(all(Path(edition[key]).parent == Path("downloads") for edition in release["languages"].values()))
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

    def test_pages_branch_is_explicit_and_runtime_workflows_still_use_main(self):
        release = json.loads((ROOT / "content/release.json").read_text())
        readme = (ROOT / "README.md").read_text()
        delivery = (ROOT / "docs/22-delivery.md").read_text()
        self.assertIn(f"**root of the `{release['pages_branch']}` branch**", readme)
        self.assertIn("Merging into `main`", readme)
        self.assertNotIn("docs/portal-walkthrough-20260930", readme + delivery)
        links = re.findall(r"\]\((https://github\.com/[^)]+/\.github/workflows/[^)]+)\)", delivery)
        self.assertEqual(len(links), 2)
        self.assertTrue(all("/blob/main/.github/workflows/" in link for link in links))


if __name__ == "__main__":
    unittest.main()
