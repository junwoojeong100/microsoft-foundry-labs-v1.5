import csv
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import portal_inputs
import build_hosted


class PortalInputTests(unittest.TestCase):
    def test_fixed_questions_and_evaluator_only_requirements_are_preserved(self):
        for language in ("ko", "en"):
            data = ROOT / ("data/en" if language == "en" else "data")
            comparison = json.loads((data / "evaluation/instruction-comparison.json").read_text())
            files = portal_inputs.inputs(language)
            rows = list(csv.DictReader(io.StringIO(files["evaluation-12.csv"].decode())))
            with self.subTest(language=language):
                native_rows = [json.loads(line) for line in files["evaluation-12.jsonl"].decode().splitlines()]
                self.assertEqual(native_rows, rows, "Portal JSONL and review CSV must preserve identical fixed cases.")
                self.assertEqual(len(rows), 12)
                self.assertEqual([row["case_id"] for row in rows], [case["id"] for case in comparison["cases"]])
                self.assertEqual([row["query"] for row in rows], [case["query"] for case in comparison["cases"]])
                self.assertEqual([row["ground_truth"] for row in rows], [
                    "\n".join(check["requirement"] for check in case["checks"]) for case in comparison["cases"]
                ])
                self.assertNotIn("response", rows[0], "Responses must come from the actual evaluated agent.")
                contexts = []
                for version in ("v1", "v2"):
                    original = (data / f"prompts/agent-{version}.txt").read_text().rstrip() + "\n\n"
                    instructions = files[f"agent-{version}-with-context.txt"].decode()
                    self.assertTrue(instructions.startswith(original))
                    boundary, context = instructions[len(original):].split("\n", 1)
                    self.assertNotIn("\n", boundary)
                    document = json.loads(context)
                    self.assertEqual(set(document), {"grounding_context", "context_kind", "available_tools"})
                    self.assertEqual(document["available_tools"], [])
                    self.assertEqual(document["grounding_context"], portal_inputs.policy_chunks(data, language))
                    self.assertEqual(len(document["grounding_context"]), 13)
                    contexts.append(document)
                    self.assertTrue(all(case["query"] not in context for case in comparison["cases"]))
                self.assertEqual(*contexts, "Only the original v1/v2 instructions may differ.")
                self.assertTrue(all(json.loads(row["context"]) == contexts[0] for row in rows))
                checklist = list(csv.DictReader(io.StringIO(files["review-checklist.csv"].decode())))
                self.assertEqual([(row["case_id"], row["check_id"], row["requirement"]) for row in checklist], [
                    (case["id"], check["id"], check["requirement"])
                    for case in comparison["cases"] for check in case["checks"]
                ])
                for policy in (data / "policies").glob("*.md"):
                    self.assertEqual(files[f"policies/{policy.name}"], policy.read_bytes())

    def test_archive_is_reproducible_and_contains_only_the_uploadable_inputs(self):
        prepared = {language: portal_inputs.inputs(language) for language in ("en", "ko")}
        with tempfile.TemporaryDirectory() as temporary, patch.object(
            portal_inputs, "ROOT", Path(temporary),
        ), patch.object(portal_inputs, "inputs", side_effect=lambda language: prepared[language]):
            archive_path = Path(temporary) / "downloads/Contoso-Portal-Inputs.zip"
            portal_inputs.build()
            first = archive_path.read_bytes()
            portal_inputs.build()
            self.assertEqual(archive_path.read_bytes(), first)
            with zipfile.ZipFile(archive_path) as archive:
                self.assertEqual(archive.namelist(), [
                    f"{language}/{name}" for language in ("en", "ko") for name in sorted(prepared[language])
                ])
                for name in archive.namelist():
                    language, relative = name.split("/", 1)
                    self.assertEqual(archive.read(name), prepared[language][relative])
                    self.assertEqual((archive_path.parent / "portal-inputs" / name).read_bytes(), archive.read(name))

    def test_existing_hosted_distribution_can_still_read_the_policy_corpus_in_isolation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            for name in ("samples", "hosted"):
                shutil.copytree(ROOT / name, root / name, ignore=shutil.ignore_patterns("__pycache__"))
            for path in [*ROOT.glob("requirements*.txt"), ROOT / "THIRD_PARTY_NOTICES"]:
                shutil.copy2(path, root / path.name)
            data = root / build_hosted.DATA.relative_to(ROOT)
            shutil.copytree(build_hosted.DATA / "policies", data / "policies")
            shutil.copytree(build_hosted.DATA / "prompts", data / "prompts")
            shutil.copy2(build_hosted.DATA / "inventory.csv", data / "inventory.csv")
            target = root / ".build/contoso"
            with patch.object(build_hosted, "ROOT", root), patch.object(
                build_hosted, "DATA", data,
            ), patch.object(build_hosted, "TARGET", target), patch.object(
                build_hosted, "config_values", return_value={"FOUNDRY_MODEL_DEPLOYMENT_NAME": "test"},
            ):
                manifest = build_hosted.build()
            result = subprocess.run(
                [sys.executable, "-I", "-c",
                 "import json,sys; sys.path.insert(0,sys.argv[1]); "
                 "from search_lab import policy_chunks; print(json.dumps(policy_chunks()))",
                 str(target / "samples")],
                cwd=root, capture_output=True, text=True, check=True,
            )
            expected = portal_inputs.policy_chunks(build_hosted.DATA, build_hosted.LANGUAGE)
            self.assertEqual(json.loads(result.stdout), expected)
            self.assertIn("samples/policy_documents.py", manifest["runtime_contract"]["files"])


if __name__ == "__main__":
    unittest.main()
