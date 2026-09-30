import json
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import patch
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_guide
import check_pages
from check_guide import CONCEPT_LABELS, GuideParser, LAB_HEADINGS, command_coverage


def executable_blocks(text):
    blocks = re.findall(r"^```(bash|powershell|python|json|yaml)\n(.*?)^```\s*$", text, re.M | re.S)
    return [
        (language, "\n".join(
            line for line in body.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ))
        for language, body in blocks
    ]


class BilingualGuideTests(unittest.TestCase):
    def test_english_is_default_and_all_html_has_pages_links(self):
        release = build_guide.RELEASE
        self.assertEqual(release["default_language"], "en")
        self.assertEqual(release["languages"]["en"]["html"], "index.html")
        self.assertEqual(release["languages"]["ko"]["html"], "index.ko.html")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for language, edition in release["languages"].items():
            parser = GuideParser()
            parser.feed((ROOT / edition["html"]).read_text(encoding="utf-8"))
            self.assertEqual(parser.language, language)
            self.assertFalse(parser.remote_assets)
            self.assertIn(edition["markdown"], parser.links)
            self.assertIn(edition["pdf"], parser.links)
        for relative in ("index.ko.html", "data/receipt.html"):
            self.assertIn(release["site_url"] + relative, readme)
        self.assertIn(release["site_url"], readme)

    def test_translations_preserve_canonical_structure_and_evidence(self):
        korean, ko_sources, ko_capabilities = build_guide.load_content("ko")
        english, en_sources, en_capabilities = build_guide.load_content("en")
        self.assertEqual(len(english), 30)
        for original, translation in zip(korean, english, strict=True):
            for key in ("id", "number", "track", "minutes", "sources"):
                self.assertEqual(original[key], translation[key], (original["id"], key))
            if original["learning"]:
                self.assertEqual(original["learning"]["mode"], translation["learning"]["mode"])
        self.assertEqual(
            [(s["id"], s["title"], s["url"]) for s in ko_sources["sources"]],
            [(s["id"], s["title"], s["url"]) for s in en_sources["sources"]],
        )
        self.assertEqual(
            [(c["lab"], c["source"], c["mode"]) for c in ko_capabilities],
            [(c["lab"], c["source"], c["mode"]) for c in en_capabilities],
        )

    def test_all_modules_have_complete_english_authoring_structure(self):
        chapters, sources, capabilities = build_guide.load_content("en")
        total = {"blocks": 0, "commands": 0}
        for chapter in chapters:
            if chapter["track"] == "reference":
                continue
            text = (ROOT / chapter["file"]).read_text(encoding="utf-8")
            with self.subTest(chapter=chapter["id"]):
                for heading in LAB_HEADINGS["en"]:
                    self.assertRegex(text, rf"(?m)^## {re.escape(heading)}$")
                for label in CONCEPT_LABELS["en"]:
                    self.assertIn("**" + label, text)
                coverage = command_coverage(text, chapter["file"], "en")
                for key in total:
                    total[key] += coverage[key]
                normalized = build_guide.source_body(chapter, chapters, capabilities, sources, "en")
                self.assertNotRegex(normalized, r"\]\(\.\./")
                for link in re.findall(r"\]\((assets/[^)]+)\)", normalized):
                    self.assertTrue((ROOT / link).is_file(), link)
        self.assertEqual(total, {"blocks": 55, "commands": 120})

    def test_translation_does_not_change_executable_examples(self):
        chapters, _, _ = build_guide.load_content("en")
        for chapter in chapters:
            if "file" not in chapter:
                continue
            translated_path = ROOT / chapter["file"]
            original_path = ROOT / "docs" / translated_path.name
            with self.subTest(chapter=chapter["id"]):
                self.assertEqual(
                    executable_blocks(original_path.read_text(encoding="utf-8")),
                    executable_blocks(translated_path.read_text(encoding="utf-8")),
                )
                self.assertEqual(
                    re.findall(r"\]\((https://[^)]+)\)", original_path.read_text(encoding="utf-8")),
                    re.findall(r"\]\((https://[^)]+)\)", translated_path.read_text(encoding="utf-8")),
                    "Translation must preserve external reference links in order.",
                )

    def test_reader_labels_have_the_same_keys_and_are_translated(self):
        labels = build_guide.read_json("reader-labels.json")
        self.assertEqual(set(labels["en"]), set(labels["ko"]))
        self.assertEqual(set(labels["en"]["js"]), set(labels["ko"]["js"]))
        self.assertFalse(re.search(r"[가-힣]", json.dumps(labels["en"], ensure_ascii=False)))
        for original, translated in zip(*[
            build_guide.load_content(language)[0] for language in ("ko", "en")
        ], strict=True):
            for key in ("title", "summary", "status"):
                self.assertFalse(re.search(r"[가-힣]", translated[key]), (original["id"], key))

    def test_missing_translation_fails_instead_of_falling_back_to_korean(self):
        read_json = build_guide.read_json

        def missing_chapter(name):
            value = read_json(name)
            return value[:-1] if name == "chapters.en.json" else value

        with patch.object(build_guide, "read_json", side_effect=missing_chapter):
            with self.assertRaisesRegex(ValueError, "every canonical chapter"):
                build_guide.load_content("en")

    def test_markdown_html_links_use_pages(self):
        for edition in build_guide.RELEASE["languages"].values():
            text = (ROOT / edition["markdown"]).read_text(encoding="utf-8")
            html_links = re.findall(r"\]\(([^)]+\.html(?:#[^)]*)?)\)", text)
            self.assertTrue(html_links)
            self.assertTrue(all(link.startswith(build_guide.RELEASE["site_url"]) for link in html_links))

    def test_pages_checker_compares_both_editions_and_the_html_fixture(self):
        base = build_guide.RELEASE["site_url"]

        def local_response(address):
            self.assertTrue(address.startswith(base))
            relative = unquote(address.removeprefix(base)) or "index.html"
            return (ROOT / relative).read_bytes()

        with patch.object(check_pages, "fetch", side_effect=local_response), patch("builtins.print"):
            report = check_pages.check()
        self.assertEqual({row["url"] for row in report["html"]}, {
            base + "index.html", base + "index.ko.html", base + "data/receipt.html", base + "data/en/receipt.html",
        })
        self.assertGreater(report["linked_files_checked"], 50)

    def test_pages_checker_rejects_stale_published_content(self):
        with patch.object(check_pages, "fetch", return_value=b"outdated HTML"):
            with self.assertRaisesRegex(ValueError, "differs from the generated source"):
                check_pages.check()


if __name__ == "__main__":
    unittest.main()
