import asyncio
import contextlib
from copy import deepcopy
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, MagicMock, Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
import model_capacity as capacity


def scope():
    subscription = "00000000-0000-0000-0000-000000000001"
    group = "rg-contoso-capacity-fixture"
    return {
        "repository_id": 1396573688, "language": capacity.LANGUAGE,
        "subscription": subscription, "resource_group": group,
        "resource_group_id": f"/subscriptions/{subscription}/resourceGroups/{group}",
        "account_name": "contoso-capacity-fixture", "project_name": "lab",
        "project_endpoint": "https://contoso-capacity-fixture.services.ai.azure.com/api/projects/lab",
        "run_id": "contoso-capacity-fixture", "location": "fixtureregion",
        "model_deployments": {role: "contoso-" + role for role in capacity.ROLES},
    }


def deployment(state, role, units=10, tokens_per_unit=1000, rpm_per_unit=6):
    return {
        "id": capacity.deployment_id(state, role), "etag": '"fixture-etag"',
        "sku": {"name": "GlobalStandard", "capacity": units},
        "properties": {
            "provisioningState": "Succeeded",
            "model": {"name": "model-" + role, "version": "fixture-version", "format": "OpenAI"},
            "raiPolicyName": "existing-policy", "versionUpgradeOption": "NoAutoUpgrade",
            "rateLimits": [
                {"key": "token", "count": units * tokens_per_unit, "renewalPeriod": 60},
                {"key": "request", "count": units * rpm_per_unit, "renewalPeriod": 60},
            ],
        },
    }


class FakeARM:
    def __init__(self, state, deployments, *, quota=1000, corrupt_policy=False):
        self.state = state
        self.deployments = deepcopy(deployments)
        self.calls = []
        self.quota = quota
        self.corrupt_policy = corrupt_policy

    def usage_name(self, model):
        name = model["name"].replace("gpt-4.1", "gpt4.1")
        return "OpenAI.GlobalStandard." + name

    def __call__(self, *args, timeout):
        self.calls.append(args)
        if args[:2] == ("group", "show"):
            return {"id": self.state["resource_group_id"],
                    "tags": {"validationRun": self.state["run_id"], "repository": "microsoft-foundry-labs-v1.5"}}
        if args[:3] == ("cognitiveservices", "account", "show"):
            return {
                "id": self.state["resource_group_id"] + "/providers/Microsoft.CognitiveServices/accounts/" + self.state["account_name"],
                "location": self.state["location"],
            }
        if args[:3] == ("cognitiveservices", "usage", "list"):
            allocated = {}
            for item in self.deployments.values():
                key = self.usage_name(item["properties"]["model"])
                allocated[key] = allocated.get(key, 0) + item["sku"]["capacity"]
            return [{"name": {"value": key}, "limit": self.quota, "currentValue": value}
                    for key, value in allocated.items()]
        address = args[args.index("--url") + 1].split("?")[0]
        if address.endswith("/models"):
            models = {item["properties"]["model"]["name"]: item["properties"]["model"]
                      for item in self.deployments.values()}
            return {"value": [
                {"kind": "AIServices", "skuName": "S0", "model": {
                    **model, "skus": [{
                        "name": "GlobalStandard", "usageName": self.usage_name(model),
                        "capacity": {"default": 10, "maximum": 10000},
                    }],
                }}
                for model in models.values()
            ]}
        role = next(role for role, item in self.deployments.items() if item["id"] == address)
        current = self.deployments[role]
        if args[args.index("--method") + 1] == "patch":
            body = json.loads(args[args.index("--body") + 1])
            if set(body) != {"sku"}:
                raise AssertionError("A capacity patch may not change model/policy properties.")
            ratio = body["sku"]["capacity"] / current["sku"]["capacity"]
            current["sku"] = body["sku"]
            for rule in current["properties"]["rateLimits"]:
                rule["count"] = int(rule["count"] * ratio)
            if self.corrupt_policy:
                current["properties"]["raiPolicyName"] = "unexpected-policy"
        return deepcopy(current)

    @property
    def patches(self):
        return [args for args in self.calls if "--method" in args and args[args.index("--method") + 1] == "patch"]


class ModelCapacityTests(unittest.TestCase):
    def test_minimums_are_calculated_with_headroom_and_cohort_scaling(self):
        plan = capacity.requirements()
        self.assertEqual([plan["roles"][role]["minimum_tpm"] for role in capacity.ROLES], [100000, 100000, 10000])
        self.assertEqual([plan["roles"][role]["minimum_rpm"] for role in capacity.ROLES], [60, 60, 6])
        for role in capacity.ROLES:
            self.assertEqual(capacity.requirements(3)["roles"][role]["minimum_tpm"],
                             3 * plan["roles"][role]["minimum_tpm"])
        for invalid in (0, -1, 21, True, 1.5):
            with self.subTest(value=invalid), self.assertRaises(ValueError):
                capacity.requirements(invalid)

    def test_plan_does_not_read_scope_initialize_clients_or_write_evidence(self):
        with patch.object(capacity, "load_scope") as load, patch.object(capacity, "Management") as management, \
                patch.object(capacity, "Evidence") as evidence, contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(capacity.main(["test", "--roles", "chat"]), 0)
        self.assertEqual(list(json.loads(output.getvalue())["roles"]), ["chat"])
        load.assert_not_called()
        management.assert_not_called()
        evidence.assert_not_called()

    def test_receipt_scope_rejects_cross_project_language_and_bad_names(self):
        with tempfile.TemporaryDirectory() as temporary:
            receipt = Path(temporary) / "scope.json"
            for field, value in (
                ("repository_id", 1390444066), ("language", "other"),
                ("project_endpoint", "https://outside.invalid/project"),
                ("resource_group_id", "/subscriptions/other/resourceGroups/other"),
                ("account_name", "../outside"),
            ):
                broken = {**scope(), field: value}
                receipt.write_text(json.dumps(broken))
                with self.subTest(field=field), self.assertRaises(ValueError):
                    capacity.load_scope(receipt)
            state = scope()
            state["model_deployments"] = {"chat": "contoso-chat"}
            receipt.write_text(json.dumps(state))
            self.assertEqual(capacity.load_scope(receipt, roles=("chat",)), state)
            with self.assertRaises(ValueError):
                capacity.load_scope(receipt)

    def test_rate_limits_normalize_seconds_and_require_both_metrics(self):
        item = deployment(scope(), "chat")
        item["properties"]["rateLimits"] = [
            {"key": "token", "count": 100000, "renewalPeriod": 60},
            {"key": "request", "count": 1, "renewalPeriod": 1},
        ]
        self.assertEqual(capacity.rate_limits(item), {"tpm": 100000, "rpm": 60})
        item["properties"]["rateLimits"].pop()
        with self.assertRaises(ValueError):
            capacity.rate_limits(item)

    def test_model_specific_units_and_rpm_are_used_instead_of_assuming_1000_tpm(self):
        state = scope()
        arm = FakeARM(state, {"chat": deployment(state, "chat", tokens_per_unit=5000, rpm_per_unit=3)})
        report, _ = capacity.inspect_deployments(state, capacity.requirements(), ["chat"], capacity.Management(arm))
        self.assertEqual(report["chat"]["proposed_capacity"], 20)
        self.assertFalse(report["chat"]["ready"])
        with self.assertRaises(ValueError):
            capacity.require_ready(report)
        self.assertEqual(arm.patches, [])

    def test_rpm_shortfall_blocks_even_when_tpm_is_sufficient(self):
        state = scope()
        arm = FakeARM(state, {"chat": deployment(state, "chat", tokens_per_unit=10000, rpm_per_unit=1)})
        report, _ = capacity.inspect_deployments(state, capacity.requirements(), ["chat"], capacity.Management(arm))
        self.assertEqual(report["chat"]["tpm"], 100000)
        self.assertEqual(report["chat"]["proposed_capacity"], 60)
        with self.assertRaises(ValueError):
            capacity.require_ready(report)
        with self.assertRaises(ValueError):
            capacity.require_ready({})

    def test_management_deadline_prevents_an_extra_request(self):
        callback = Mock()
        management = capacity.Management(callback)
        management.started -= capacity.MAX_SECONDS + 1
        with self.assertRaisesRegex(RuntimeError, "deadline"):
            management.call("group", "show")
        callback.assert_not_called()

    def test_wrong_execution_snapshot_is_rejected_before_any_azure_call(self):
        with tempfile.TemporaryDirectory() as temporary:
            receipt = Path(temporary) / "scope.json"
            receipt.write_text(json.dumps(scope()))
            arm = Mock()
            with self.assertRaises(ValueError):
                capacity.check_ready(receipt, az_call=arm, expected_endpoint="https://other.invalid")
            with self.assertRaises(ValueError):
                capacity.check_ready(receipt, az_call=arm, expected_deployment="other-deployment")
            arm.assert_not_called()

    def test_account_region_must_match_before_quota_or_deployment_changes(self):
        state = scope()
        arm = FakeARM(state, {"chat": deployment(state, "chat")})

        def wrong_region(*args, **kwargs):
            result = arm(*args, **kwargs)
            if args[:3] == ("cognitiveservices", "account", "show"):
                result["location"] = "anotherregion"
            return result

        with self.assertRaisesRegex(ValueError, "region"):
            capacity.inspect_deployments(state, capacity.requirements(), ["chat"], capacity.Management(wrong_region))
        self.assertEqual(arm.patches, [])
        self.assertEqual(len(arm.calls), 2)

    def test_apply_only_patches_sku_and_preserves_existing_models_policies_and_etag(self):
        state = scope()
        arm = FakeARM(state, {"chat": deployment(state, "chat")})
        management = capacity.Management(arm)
        report, originals = capacity.inspect_deployments(state, capacity.requirements(), ["chat"], management)
        result = capacity.apply_capacity(state, report, originals, management, Mock(), 100)
        self.assertTrue(result["chat"]["ready"])
        self.assertEqual(result["chat"]["capacity"], 100)
        self.assertEqual(len(arm.patches), 1)
        args = arm.patches[0]
        self.assertEqual(args[args.index("--headers") + 1], 'If-Match="fixture-etag"')
        self.assertNotIn("properties", json.loads(args[args.index("--body") + 1]))

    def test_quota_is_aggregated_before_any_partial_model_updates(self):
        state = scope()
        items = {role: deployment(state, role) for role in ("chat", "judge")}
        for item in items.values():
            item["properties"]["model"]["name"] = "shared-quota-model"
        arm = FakeARM(state, items, quota=190)
        management = capacity.Management(arm)
        report, originals = capacity.inspect_deployments(state, capacity.requirements(), ["chat", "judge"], management)
        with self.assertRaisesRegex(ValueError, "quota"):
            capacity.apply_capacity(state, report, originals, management, Mock(), 100)
        self.assertEqual(arm.patches, [])

    def test_apply_uses_catalog_quota_name_instead_of_model_name(self):
        state = scope()
        item = deployment(state, "judge")
        item["properties"]["model"]["name"] = "gpt-4.1"
        arm = FakeARM(state, {"judge": item})
        management = capacity.Management(arm)
        report, originals = capacity.inspect_deployments(state, capacity.requirements(), ["judge"], management)
        result = capacity.apply_capacity(state, report, originals, management, Mock(), 100)
        self.assertTrue(result["judge"]["ready"])
        self.assertEqual(len(arm.patches), 1)

    def test_capacity_ceiling_and_policy_readback_are_enforced(self):
        state = scope()
        arm = FakeARM(state, {"chat": deployment(state, "chat")}, corrupt_policy=True)
        management = capacity.Management(arm)
        report, originals = capacity.inspect_deployments(state, capacity.requirements(), ["chat"], management)
        with self.assertRaisesRegex(ValueError, "ceiling|exceeds"):
            capacity.apply_capacity(state, report, originals, management, Mock(), 50)
        self.assertEqual(arm.patches, [])
        with self.assertRaisesRegex(RuntimeError, "raiPolicyName"):
            capacity.apply_capacity(state, report, originals, management, Mock(), 100)

    def test_existing_sufficient_capacity_is_never_reduced(self):
        state = scope()
        arm = FakeARM(state, {"chat": deployment(state, "chat", units=150)})
        management = capacity.Management(arm)
        report, originals = capacity.inspect_deployments(state, capacity.requirements(), ["chat"], management)
        capacity.apply_capacity(state, report, originals, management, Mock(), 100)
        self.assertEqual(arm.patches, [])

    def test_missing_confirmation_blocks_apply_and_test_before_management(self):
        for action in ("apply", "test"):
            with self.subTest(action=action), patch.object(capacity, "load_scope", return_value=scope()), \
                    patch.object(capacity, "Management") as management, self.assertRaises(ValueError):
                capacity.main([action, "--live"])
            management.assert_not_called()

    def test_insufficient_capacity_never_starts_the_paid_smoke_test(self):
        report = {"chat": {"ready": False}}
        with patch.object(capacity, "load_scope", return_value=scope()), \
                patch.object(capacity, "Management"), patch.object(capacity, "Evidence") as evidence, \
                patch.object(capacity, "inspect_deployments", return_value=(report, {})), \
                patch.object(capacity, "smoke_test", new_callable=AsyncMock) as smoke, \
                contextlib.redirect_stdout(io.StringIO()), self.assertRaises(ValueError):
            capacity.main(["test", "--live", "--confirm", scope()["run_id"]])
        smoke.assert_not_awaited()
        evidence.return_value.failure.assert_called_once()

    def test_smoke_test_is_bounded_and_closes_its_clients(self):
        state = scope()
        report = {role: {"ready": True, "deployment": state["model_deployments"][role]} for role in capacity.ROLES}
        for outcome in ("completed", "incomplete", "error"):
            client = MagicMock()
            client.__aenter__.return_value = client
            client.responses.create = AsyncMock(side_effect=RuntimeError("429 fixture") if outcome == "error" else [
                SimpleNamespace(status=outcome, output_text="Synthetic fixture answer", id=f"fixture-{i}", usage=None)
                for i in range(4)
            ])
            embedding_client = MagicMock()
            embedding_client.__aenter__.return_value = embedding_client
            embedding_client.embeddings.create = AsyncMock(return_value=SimpleNamespace(
                data=[SimpleNamespace(embedding=[0.1, 0.2])], usage=SimpleNamespace(prompt_tokens=10),
            ))
            project = MagicMock()
            project.__aenter__.return_value = project
            project.get_openai_client.return_value = client
            credential = MagicMock()
            credential.__aenter__.return_value = credential
            with self.subTest(outcome=outcome), patch("azure.ai.projects.aio.AIProjectClient", return_value=project), \
                    patch("azure.identity.aio.AzureCliCredential", return_value=credential) as identity, \
                    patch("openai.AsyncOpenAI", return_value=embedding_client) as direct, \
                    patch.object(capacity, "MIN_START_INTERVAL", 0):
                if outcome == "completed":
                    result = asyncio.run(capacity.smoke_test(state, report, capacity.Management(Mock()), Mock()))
                    self.assertEqual(len(result), 5)
                else:
                    with self.assertRaises(RuntimeError):
                        asyncio.run(capacity.smoke_test(state, report, capacity.Management(Mock()), Mock()))
            self.assertEqual(client.responses.create.await_count, 4 if outcome == "completed" else 1)
            self.assertEqual(embedding_client.embeddings.create.await_count, 1 if outcome == "completed" else 0)
            client.embeddings.create.assert_not_called()
            if outcome == "completed":
                self.assertEqual(direct.call_args.kwargs["base_url"],
                                 "https://contoso-capacity-fixture.openai.azure.com/openai/v1/")
                self.assertEqual(direct.call_args.kwargs["max_retries"], 0)
                embedding_client.__aexit__.assert_awaited_once()
            identity.assert_called_once_with(subscription=state["subscription"], process_timeout=30)
            project.get_openai_client.assert_called_once_with(max_retries=0, timeout=30)
            client.__aexit__.assert_awaited_once()
            project.__aexit__.assert_awaited_once()
            credential.__aexit__.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
