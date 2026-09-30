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
            {path.name for path in ROOT.glob("*Foundry*Hands-on*.pdf")},
            {release["artifact"] + ".pdf"},
        )
        self.assertLessEqual(
            {path.name for path in ROOT.glob("*Foundry*Hands-on*.zip")},
            {release["artifact"] + ".zip"},
        )
        self.assertFalse((ROOT / "assets/favicon.svg").exists())

    def test_validation_has_no_superseded_snapshots(self):
        release = json.loads((ROOT / "content/release.json").read_text())
        self.assertEqual(release["documentation_validation"], "validation/docs")
        self.assertFalse(list((ROOT / "validation").glob("*.json")))
        for name in ("automated-v2", "history", "guide-refresh-20260930", "pages-20260930"):
            self.assertFalse((ROOT / "validation" / name).exists(), name)
        for name in ("ci.json", "quality.json", "dev-responses.jsonl", "holdout-responses.jsonl"):
            self.assertFalse((ROOT / "validation/current" / name).exists(), name)
        self.assertTrue((ROOT / "validation/automated-v3/quality.json").is_file())
        self.assertTrue((ROOT / release["validation"]).is_file())

    def test_historical_evidence_is_linked_to_an_immutable_commit(self):
        release = json.loads((ROOT / "content/release.json").read_text())
        address = urlparse(release["historical_validation"])
        self.assertEqual(address.scheme, "https")
        self.assertEqual(address.hostname, "github.com")
        self.assertRegex(address.path, r"/tree/[0-9a-f]{40}/validation$")

    def test_readme_html_link_opens_github_pages(self):
        readme = (ROOT / "README.md").read_text()
        links = re.findall(r"\[[^\]]*index\.html[^\]]*\]\(([^)]+)\)", readme)
        self.assertEqual(links, ["https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/"])
        self.assertNotRegex(readme, r"\]\((?:\./)?index\.html(?:[)#])")

    def test_active_documentation_links_use_main(self):
        readme = (ROOT / "README.md").read_text()
        delivery = (ROOT / "docs/22-delivery.md").read_text()
        self.assertIn("**`main` 브랜치의 루트**", readme)
        self.assertNotIn("docs/portal-walkthrough-20260930", readme + delivery)
        links = re.findall(r"\]\((https://github\.com/[^)]+/\.github/workflows/[^)]+)\)", delivery)
        self.assertEqual(len(links), 2)
        self.assertTrue(all("/blob/main/.github/workflows/" in link for link in links))


if __name__ == "__main__":
    unittest.main()
