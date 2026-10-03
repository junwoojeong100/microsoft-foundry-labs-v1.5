"""Synthetic CI failure/repair exercise, not the repository's release gate."""

import unittest

from exercise import choose_version


class DeliveryPractice(unittest.TestCase):
    def setUp(self):
        self.checks = {"status": "completed", "quality_passed": True, "critical_failures": 0, "missing_rows": 0}

    def test_complete_candidate(self):
        self.assertEqual(choose_version("approved-1", "candidate-2", self.checks), "candidate-2")

    def test_failed_run_keeps_previous(self):
        self.checks["status"] = "failed"
        self.assertEqual(choose_version("approved-1", "candidate-2", self.checks), "approved-1")

    def test_quality_failure_keeps_previous(self):
        self.checks["quality_passed"] = False
        self.assertEqual(choose_version("approved-1", "candidate-2", self.checks), "approved-1")

    def test_critical_failure_keeps_previous(self):
        self.checks["critical_failures"] = 1
        self.assertEqual(choose_version("approved-1", "candidate-2", self.checks), "approved-1")

    def test_missing_row_keeps_previous(self):
        self.checks["missing_rows"] = 1
        self.assertEqual(choose_version("approved-1", "candidate-2", self.checks), "approved-1")


if __name__ == "__main__":
    unittest.main()
