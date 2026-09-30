import os
import base64
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
sys.path.insert(0, str(ROOT / "scripts"))
import azure_environment
import lab_profile
import request_contract
from workshop import ToolInputError


class EnglishProfileTests(unittest.TestCase):
    def test_default_korean_and_explicit_english_paths(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(lab_profile.data_for(ROOT), ROOT / "data")
        with patch.dict(os.environ, {"FOUNDRY_LAB_LANGUAGE": "en"}):
            self.assertEqual(lab_profile.data_for(ROOT), ROOT / "data/en")

    def test_invalid_or_mismatched_packaged_language_is_rejected(self):
        with patch.dict(os.environ, {"FOUNDRY_LAB_LANGUAGE": "fr"}):
            with self.assertRaises(ValueError):
                lab_profile.language_for(ROOT)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "lab-profile.json").write_text('{"language":"en"}')
            with patch.dict(os.environ, {}, clear=True):
                self.assertEqual(lab_profile.data_for(root), root / "data/en")
            with patch.dict(os.environ, {"FOUNDRY_LAB_LANGUAGE": "ko"}):
                with self.assertRaisesRegex(ValueError, "packaged"):
                    lab_profile.language_for(root)

    def test_english_validation_cannot_overwrite_korean_evidence(self):
        with patch.dict(os.environ, {"FOUNDRY_LAB_LANGUAGE": "en"}):
            self.assertEqual(lab_profile.validation_for(ROOT), ROOT / "validation/english")
        with patch.dict(os.environ, {"FOUNDRY_LAB_LANGUAGE": "ko"}):
            self.assertEqual(lab_profile.validation_for(ROOT), ROOT / "validation")

    def test_administrator_identity_uses_the_owned_arm_tenant_without_graph(self):
        tenant = "00000000-0000-0000-0000-000000000001"
        principal = "00000000-0000-0000-0000-000000000002"
        state = {"subscription": "synthetic-subscription", "tenant": tenant}
        account = {"tenantId": tenant, "user": {"type": "user"}}
        for claim_tenant in (tenant, "different-tenant"):
            claims = base64.urlsafe_b64encode(json.dumps({"oid": principal, "tid": claim_tenant}).encode()).decode().rstrip("=")
            with patch.object(azure_environment, "az", side_effect=[account, f"fixture.{claims}.fixture"]) as az:
                if claim_tenant == tenant:
                    self.assertEqual(azure_environment.current_user_id(state), principal)
                else:
                    with self.assertRaises(ValueError):
                        azure_environment.current_user_id(state)
                self.assertTrue(all(call.args[0] == "account" for call in az.call_args_list))

    def test_natural_english_quantities_are_grounded_in_the_request(self):
        with patch.object(request_contract, "LANGUAGE", "en"):
            for query in (
                "Prepare a draft for two NB-14 laptops.",
                "Prepare a draft for NB-14, quantity two.",
                "I need 2 laptops, SKU NB-14. Prepare a purchase draft.",
                "Prepare a draft for two laptops (NB-14).",
                "Prepare a draft for NB-14, quantity 2.",
            ):
                with self.subTest(query=query):
                    request_contract.validate_draft_request(query, {"sku": "NB-14", "quantity": 2})

    def test_english_ambiguity_invalid_values_and_invention_still_fail(self):
        with patch.object(request_contract, "LANGUAGE", "en"):
            for query in (
                "Prepare a draft for NB-14.",
                "Prepare a draft for two or three NB-14 laptops.",
                "Prepare a draft for NB-14, quantity two or three.",
                "Prepare a draft for minus two NB-14 laptops.",
                "Prepare a draft for negative two NB-14 laptops.",
                "Prepare a draft for NB-14, quantity 1.5.",
                "Prepare a draft for twenty one NB-14 laptops.",
                "Prepare a draft for twenty-one NB-14 laptops.",
                "Prepare a draft for NB-14, quantity 0.",
                "Prepare a draft for NB-14, quantity 11.",
            ):
                with self.subTest(query=query), self.assertRaises(ToolInputError):
                    request_contract.validate_draft_request(query, {"sku": "NB-14", "quantity": 2})

    def test_quantities_do_not_transfer_between_skus(self):
        with patch.object(request_contract, "LANGUAGE", "en"):
            for query in (
                "Prepare drafts for two NB-14 laptops and one MON-27 monitor.",
                "Prepare drafts for NB-14 quantity two and MON-27 quantity one.",
                "Prepare drafts for 2 units of NB-14 and 1 unit of MON-27.",
            ):
                with self.subTest(query=query):
                    request_contract.validate_draft_request(query, {"sku": "NB-14", "quantity": 2})
                    request_contract.validate_draft_request(query, {"sku": "MON-27", "quantity": 1})
                    with self.assertRaises(ToolInputError):
                        request_contract.validate_draft_request(query, {"sku": "NB-14", "quantity": 1})


if __name__ == "__main__":
    unittest.main()
