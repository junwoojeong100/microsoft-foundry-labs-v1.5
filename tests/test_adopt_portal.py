import contextlib
from copy import deepcopy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import adopt_portal
from model_capacity import Management, load_scope

SUBSCRIPTION = "11111111-2222-4333-8444-555555555555"
GROUP = "rg-contoso-portal-fixture"
RUN = "portal-fixture"
ENDPOINT = "https://ai-contoso-fixture.services.ai.azure.com/api/projects/contoso"
GROUP_ID = f"/subscriptions/{SUBSCRIPTION}/resourceGroups/{GROUP}"
ACCOUNT_ID = GROUP_ID + "/providers/Microsoft.CognitiveServices/accounts/ai-contoso-fixture"
PROJECT_ID = ACCOUNT_ID + "/projects/contoso"


def responses():
    return [
        {"id": SUBSCRIPTION, "tenantId": "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"},
        {"id": GROUP_ID, "tags": {"validationRun": RUN, "repository": "microsoft-foundry-labs-v1.5"}},
        {"id": ACCOUNT_ID, "kind": "AIServices", "location": "northcentralus",
         "properties": {"provisioningState": "Succeeded"}},
        {"id": PROJECT_ID, "properties": {
            "provisioningState": "Succeeded", "endpoints": {"AI Foundry API": ENDPOINT},
        }},
        {"id": ACCOUNT_ID + "/deployments/contoso-chat", "properties": {
            "provisioningState": "Succeeded", "model": {"name": "gpt-6-sol", "version": "2026-09-22"},
        }},
    ]


class PortalAdoptionTests(unittest.TestCase):
    def test_plan_never_reads_configuration_calls_azure_or_writes_a_receipt(self):
        with patch.object(adopt_portal, "read_config") as config, patch.object(
            adopt_portal, "verified_scope",
        ) as verify, contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(adopt_portal.main([
                "--subscription", SUBSCRIPTION, "--resource-group", GROUP, "--run-id", RUN,
            ]), 0)
        self.assertIn("PLAN ONLY", output.getvalue())
        config.assert_not_called()
        verify.assert_not_called()

    def test_exact_portal_scope_yields_a_compatible_private_receipt_using_only_reads(self):
        calls = []

        def az(*args, **kwargs):
            calls.append(args)
            return responses()[len(calls) - 1]

        state = adopt_portal.verified_scope(
            SUBSCRIPTION, GROUP, RUN, ENDPOINT, "contoso-chat", management=Management(az),
        )
        self.assertEqual(len(calls), 5)
        self.assertTrue(all(call[:2] in {("account", "show"), ("group", "show"), ("rest", "--method")} for call in calls))
        self.assertTrue(all("--subscription" in call and SUBSCRIPTION in call for call in calls))
        self.assertTrue(all("get" in call for call in calls[2:]))
        self.assertEqual(state["operations"][0]["resource_changes"], 0)
        self.assertEqual(state["foundation"]["projectId"]["value"], PROJECT_ID)
        self.assertEqual(state["model_configuration"], {
            "chatModel": "gpt-6-sol", "chatVersion": "2026-09-22",
        })
        with tempfile.TemporaryDirectory() as temporary:
            receipt = Path(temporary) / "scope.json"
            receipt.write_text(json.dumps(state))
            self.assertEqual(load_scope(receipt, roles=("chat",))["project_endpoint"], ENDPOINT)

    def test_mismatched_tags_resources_endpoints_and_incomplete_deployments_are_rejected(self):
        defects = (
            (1, lambda row: row["tags"].update(validationRun="not-my-run")),
            (1, lambda row: row["tags"].update(repository="another-repository")),
            (2, lambda row: row.update(id="/subscriptions/another-account")),
            (3, lambda row: row["properties"]["endpoints"].update({"AI Foundry API": ENDPOINT + "-other"})),
            (4, lambda row: row["properties"].update(provisioningState="Failed")),
            (4, lambda row: row["properties"].update(model={"name": "unversioned-model"})),
        )
        for index, change in defects:
            rows = deepcopy(responses())
            change(rows[index])
            with self.subTest(index=index), patch.object(
                adopt_portal, "Management", return_value=Management(lambda *a, **k: rows.pop(0)),
            ), self.assertRaises(ValueError):
                adopt_portal.verified_scope(SUBSCRIPTION, GROUP, RUN, ENDPOINT, "contoso-chat")

    def test_existing_receipts_are_never_overwritten_or_reverified(self):
        with tempfile.TemporaryDirectory() as temporary:
            receipt = Path(temporary) / "azure-environment.json"
            receipt.write_text('{"original":true}\n')
            with patch.object(adopt_portal, "LEDGER", receipt), patch.object(
                adopt_portal, "verified_scope",
            ) as verify, self.assertRaisesRegex(ValueError, "already exists"):
                adopt_portal.main([
                    "--subscription", SUBSCRIPTION, "--resource-group", GROUP, "--run-id", RUN, "--live",
                ])
            verify.assert_not_called()
            self.assertEqual(receipt.read_text(), '{"original":true}\n')

    def test_live_verification_writes_one_owner_only_receipt(self):
        state = {"ownership_source": "portal_read_only_verification"}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            receipt = root / "results/azure-environment.json"
            with patch.object(adopt_portal, "ROOT", root), patch.object(
                adopt_portal, "LEDGER", receipt,
            ), patch.object(adopt_portal, "read_config", return_value=(ENDPOINT, "contoso-chat")), patch.object(
                adopt_portal, "verified_scope", return_value=state,
            ) as verify, contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(adopt_portal.main([
                    "--subscription", SUBSCRIPTION, "--resource-group", GROUP, "--run-id", RUN, "--live",
                ]), 0)
            verify.assert_called_once_with(
                SUBSCRIPTION, GROUP, RUN, ENDPOINT, "contoso-chat",
                search_service=None, embedding_deployment=None,
            )
            self.assertEqual(json.loads(receipt.read_text()), state)
            self.assertEqual(receipt.stat().st_mode & 0o777, 0o600)

    def test_hosted_adoption_requires_both_scoped_dependencies_and_reads_at_most_seven_resources(self):
        rows = responses() + [
            {"id": GROUP_ID + "/providers/Microsoft.Search/searchServices/contoso-search",
             "properties": {"provisioningState": "succeeded"}},
            {"id": ACCOUNT_ID + "/deployments/contoso-embedding", "properties": {
                "provisioningState": "Succeeded", "model": {"name": "text-embedding-3-small", "version": "1"},
            }},
        ]
        management = Management(lambda *a, **k: rows.pop(0))
        state = adopt_portal.verified_scope(
            SUBSCRIPTION, GROUP, RUN, ENDPOINT, "contoso-chat", search_service="contoso-search",
            embedding_deployment="contoso-embedding", management=management,
        )
        self.assertEqual(management.calls, 7)
        self.assertEqual(state["search_endpoint"], "https://contoso-search.search.windows.net")
        self.assertEqual(state["model_deployments"]["embedding"], "contoso-embedding")
        self.assertEqual(state["model_configuration"]["embeddingModel"], "text-embedding-3-small")
        self.assertEqual(state["model_configuration"]["embeddingVersion"], "1")
        with self.assertRaisesRegex(ValueError, "both"):
            adopt_portal.verified_scope(
                SUBSCRIPTION, GROUP, RUN, ENDPOINT, "contoso-chat", search_service="contoso-search",
            )


if __name__ == "__main__":
    unittest.main()
