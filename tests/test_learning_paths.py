import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
from evaluation_data import load_cases, policy
from evaluation_lab import audit_items


class LearningPathTests(unittest.TestCase):
    def test_basic_evaluation_has_no_hosted_or_holdout_requirement(self):
        cases = load_cases("basic-learning", "dev")
        self.assertEqual(len(cases), 10)
        with self.assertRaises(ValueError):
            load_cases("basic-learning", "holdout")
        rows = [{"datasource_item": {"id": c["id"]},
                 "results": [{"name": "contoso_business", "score": 5, "passed": True}]} for c in cases]
        audit = audit_items(rows, suite="basic-learning", split="dev")
        self.assertTrue(audit["business_gate_passed"])
        self.assertTrue(audit["learning_only"])
        self.assertFalse(audit["quality_release"])
        self.assertFalse(audit["human_review_required"])

    def test_all_advanced_modules_are_classified(self):
        paths = json.loads((ROOT / "content/learning-paths.json").read_text())
        self.assertEqual(list(paths), [f"l{i:02}" for i in (*range(13, 18), 21, 22)])
        english = json.loads((ROOT / "content/learning-paths.en.json").read_text())
        self.assertEqual(list(english), list(paths))
        self.assertEqual(paths["l14"]["mode"], "sequence")
        self.assertEqual(paths["l22"]["mode"], "sequence")
        self.assertEqual(paths["l17"]["mode"], "mixed")
        self.assertTrue(all(value["requires"] for value in paths.values()))
        self.assertTrue(all(value["requires"] for value in english.values()))

    def test_course_preserves_original_ids_numbers_and_reference_order(self):
        chapters = json.loads((ROOT / "content/chapters.json").read_text())
        numbers = [f"{i:02}" for i in (*range(18), 21, 22)]
        labs = [chapter for chapter in chapters if chapter["track"] != "reference"]
        self.assertEqual([chapter["number"] for chapter in labs], numbers)
        self.assertEqual([chapter["id"] for chapter in labs], ["l" + number for number in numbers])
        self.assertEqual([chapter["track"] for chapter in labs], ["core"] * 13 + ["advanced"] * 7)
        expected_ids = [*("l" + number for number in numbers), "troubleshooting", "instructor", "glossary", "coverage", "sources"]
        self.assertEqual([chapter["id"] for chapter in chapters], expected_ids)
        translated = json.loads((ROOT / "content/chapters.en.json").read_text())
        self.assertEqual([chapter["id"] for chapter in translated], expected_ids)

    def test_pruned_lessons_are_absent_from_active_sources_and_recommendations(self):
        removed = ("18-multimodal.md", "19-voice.md", "20-optimization.md", "23-extensions.md", "24-migration.md")
        chapters = json.loads((ROOT / "content/chapters.json").read_text())
        stale_reference = r"\b[lL](?:18|19|20|23|24)\b|" + "|".join(re.escape(name) for name in removed)
        for directory in (ROOT / "docs", ROOT / "docs/en"):
            for name in removed:
                self.assertFalse((directory / name).exists(), directory / name)
            for chapter in chapters:
                if "file" not in chapter:
                    continue
                path = directory / Path(chapter["file"]).name
                with self.subTest(path=path):
                    self.assertNotRegex(path.read_text(), stale_reference)
        for name in ("README.md", "README.ko.md"):
            self.assertNotRegex((ROOT / name).read_text(), stale_reference)
        for name in ("capabilities.json", "capabilities.en.json"):
            capabilities = json.loads((ROOT / "content" / name).read_text())
            self.assertEqual(len(capabilities), 68)
            self.assertLessEqual({item["lab"] for item in capabilities}, {chapter["id"] for chapter in chapters})

    def test_course_estimate_matches_module_durations(self):
        chapters = json.loads((ROOT / "content/chapters.json").read_text())
        self.assertEqual(sum(c["minutes"] for c in chapters if c["track"] == "core"), 320)
        self.assertEqual(sum(c["minutes"] for c in chapters if c["track"] == "advanced"), 310)

    def test_current_evaluation_path_is_consistent_in_both_guides(self):
        for directory, marker, stale in (
            ("docs", "도구 없는 Prompt Agent", "L08의 Hosted"),
            ("docs/en", "tool-free Prompt Agent", "L08's Hosted"),
        ):
            with self.subTest(directory=directory):
                instructor = (ROOT / directory / "instructor.md").read_text()
                evaluation = (ROOT / directory / "08-evaluation.md").read_text()
                self.assertIn(marker, instructor)
                self.assertNotIn(stale, instructor)
                self.assertIn("12", instructor)
                self.assertIn("samples/instruction_prompt_agent_lab.py", evaluation)

    def test_delivery_default_is_local_with_explicit_optional_hosted_prerequisite(self):
        paths = json.loads((ROOT / "content/learning-paths.json").read_text())
        english = json.loads((ROOT / "content/learning-paths.en.json").read_text())
        self.assertIn("L14는 선택형", paths["l22"]["requires"])
        self.assertIn("L14 is needed only", english["l22"]["requires"])
        for directory in ("docs", "docs/en"):
            text = (ROOT / directory / "22-delivery.md").read_text()
            with self.subTest(directory=directory):
                self.assertIn("acknowledge_cost", text)
                self.assertIn("repository_id", text)
                self.assertIn("RTO", text)
                self.assertIn("RPO", text)
                self.assertNotIn("--live", text)
                self.assertNotIn("azd deploy", text)


if __name__ == "__main__":
    unittest.main()
