import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("optimizer_responses_adapter", ROOT / "hosted/optimizer_responses.py")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class OptimizerAdapterTests(unittest.TestCase):
    def test_instruction_only_candidate_explicitly_inherits_baseline_model(self):
        self.assertEqual(adapter.resolved_model(None, "approved-model", optimizer_overlay=True),
                         ("approved-model", "explicit_baseline_inheritance"))

    def test_invalid_baseline_or_explicit_empty_model_is_not_silently_defaulted(self):
        for model, baseline, overlay in [
            (None, "approved-model", False), ("", "approved-model", True),
            (None, "", True), (None, "CONFIGURE-MODEL-BEFORE-DEPLOY", True),
        ]:
            with self.assertRaises(ValueError):
                adapter.resolved_model(model, baseline, optimizer_overlay=overlay)

    def test_explicit_candidate_model_is_not_replaced(self):
        self.assertEqual(adapter.resolved_model("candidate-model", "baseline-model", optimizer_overlay=True),
                         ("candidate-model", "candidate"))


if __name__ == "__main__":
    unittest.main()
