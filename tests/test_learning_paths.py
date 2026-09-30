import json
from pathlib import Path
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
        self.assertEqual(set(paths), {f"l{i:02}" for i in range(13, 25)})
        self.assertEqual(paths["l14"]["mode"], "sequence")
        self.assertEqual(paths["l22"]["mode"], "sequence")
        self.assertEqual(paths["l20"]["mode"], "mixed")
        self.assertTrue(all(value["requires"] for value in paths.values()))

    def test_course_estimate_matches_module_durations(self):
        chapters = json.loads((ROOT / "content/chapters.json").read_text())
        self.assertEqual(sum(c["minutes"] for c in chapters if c["track"] == "core"), 320)
        self.assertEqual(sum(c["minutes"] for c in chapters if c["track"] == "advanced"), 440)


if __name__ == "__main__":
    unittest.main()
