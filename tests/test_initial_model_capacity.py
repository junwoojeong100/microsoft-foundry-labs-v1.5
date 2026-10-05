import argparse
import contextlib
from copy import deepcopy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
sys.path.insert(0, str(ROOT / "scripts"))
import azure_environment as environment
import model_capacity as capacity
from test_model_capacity import deployment, scope


def models():
    return {role: {"name": "model-" + role, "version": "fixture-version"} for role in capacity.ROLES}


def catalog():
    return [
        {
            "kind": "AIServices", "skuName": "S0",
            "model": {
                "format": "OpenAI", **model,
                "skus": [{
                    "name": "GlobalStandard", "usageName": "quota-" + role,
                    "capacity": {"minimum": 1, "maximum": 10000, "step": 1, "default": 10},
                    "rateLimits": [{
                        "count": 6, "renewalPeriod": 60,
                        "rules": [{"key": "token", "count": 1000, "renewalPeriod": 60}],
                    }],
                }],
            },
        }
        for role, model in models().items()
    ]


def quotas():
    return [{"name": {"value": "quota-" + role}, "limit": 1000, "currentValue": 0}
            for role in capacity.ROLES]


def arguments(**overrides):
    values = {
        "model_sku": "GlobalStandard", "learners": 1, "max_capacity": 100, "resume": False,
        **{role + "_model": model["name"] for role, model in models().items()},
        **{role + "_version": model["version"] for role, model in models().items()},
    }
    return argparse.Namespace(**{**values, **overrides})


class InitialCapacityPlanTests(unittest.TestCase):
    def test_recommended_tpm_is_converted_to_individual_initial_capacities(self):
        plan = capacity.initial_capacity_plan(catalog(), quotas(), models(), "GlobalStandard")
        self.assertEqual([plan["roles"][role]["capacity"] for role in capacity.ROLES], [100, 100, 10])
        self.assertEqual([plan["roles"][role]["planned_tpm"] for role in capacity.ROLES], [100000, 100000, 10000])
        self.assertEqual(plan["roles"]["chat"]["usage_name"], "quota-chat")

    def test_unit_rates_rpm_and_sku_increments_all_affect_initial_capacity(self):
        entries = catalog()
        chat = entries[0]["model"]["skus"][0]
        chat["rateLimits"] = [
            {"key": "token", "count": 5000, "renewalPeriod": 60},
            {"key": "request", "count": 3, "renewalPeriod": 60},
        ]
        chat["capacity"].update(minimum=8, step=8)
        judge = entries[1]["model"]["skus"][0]
        judge["rateLimits"][0]["count"] = 1
        judge["rateLimits"][0]["rules"][0]["count"] = 10000
        plan = capacity.initial_capacity_plan(entries, quotas(), models(), "GlobalStandard")
        self.assertEqual(plan["roles"]["chat"]["capacity"], 24)
        self.assertEqual(plan["roles"]["judge"]["capacity"], 60)
        self.assertEqual(capacity.aligned_capacity(20, {"allowedValues": [8, 16, 32, 64]}), 32)

    def test_missing_or_ambiguous_sku_metadata_cannot_silently_use_capacity_ten(self):
        for defect in ("model", "version", "sku", "rates", "quota-name", "step", "duplicate"):
            entries = catalog()
            first = entries[0]["model"]
            sku = first["skus"][0]
            if defect == "model":
                first["name"] = "different-model"
            elif defect == "version":
                first["version"] = "different-version"
            elif defect == "sku":
                sku["name"] = "GlobalProvisionedManaged"
            elif defect == "rates":
                sku["rateLimits"][0]["rules"] = []
            elif defect == "quota-name":
                sku.pop("usageName")
            elif defect == "step":
                sku["capacity"]["step"] = 0
            else:
                entries.append(deepcopy(entries[0]))
            with self.subTest(defect=defect), self.assertRaises(ValueError):
                capacity.initial_capacity_plan(entries, quotas(), models(), "GlobalStandard")

    def test_raw_catalog_selects_account_kind_and_base_model_not_fine_tuning(self):
        entries = catalog()
        other_kind = deepcopy(entries)
        for item in other_kind:
            item["kind"] = "OpenAI"
        tuned = deepcopy(entries[1]["model"]["skus"][0])
        tuned["usageName"] += "-finetune"
        entries[1]["model"]["skus"].append(tuned)
        for entry in entries:
            entry["model"]["skus"][0]["capacity"] = {"default": 10, "maximum": 10000}
        plan = capacity.initial_capacity_plan(entries + other_kind, quotas(), models(), "GlobalStandard")
        self.assertEqual([plan["roles"][role]["capacity"] for role in capacity.ROLES], [100, 100, 10])
        self.assertEqual(plan["roles"]["judge"]["usage_name"], "quota-judge")

    def test_raw_catalog_preserves_token_keys_and_rejects_partial_envelopes(self):
        callback = Mock(return_value={"value": catalog()})
        self.assertEqual(capacity.model_catalog(scope(), capacity.Management(callback)), catalog())
        args = callback.call_args.args
        self.assertEqual(args[:3], ("rest", "--method", "get"))
        self.assertIn("/models?api-version=2025-06-01", args[args.index("--url") + 1])
        for response in ({}, {"value": None}, {"value": catalog(), "nextLink": "https://example.invalid"}):
            with self.subTest(response=response), self.assertRaises(ValueError):
                capacity.model_catalog(scope(), capacity.Management(Mock(return_value=response)))

    def test_shared_quota_is_checked_for_the_combined_initial_allocation(self):
        entries = catalog()
        entries[1]["model"]["skus"][0]["usageName"] = "quota-chat"
        usage = quotas()
        usage[0]["limit"] = 199
        with self.assertRaisesRegex(ValueError, "quota"):
            capacity.initial_capacity_plan(entries, usage, models(), "GlobalStandard")
        usage[0]["limit"] = 200
        capacity.initial_capacity_plan(entries, usage, models(), "GlobalStandard")

    def test_ceiling_and_sku_maximum_block_instead_of_reducing_recommendation(self):
        with self.assertRaisesRegex(ValueError, "max-capacity"):
            capacity.initial_capacity_plan(catalog(), quotas(), models(), "GlobalStandard", max_capacity=99)
        entries = catalog()
        entries[0]["model"]["skus"][0]["capacity"]["maximum"] = 99
        with self.assertRaisesRegex(ValueError, "maximum"):
            capacity.initial_capacity_plan(entries, quotas(), models(), "GlobalStandard")

    def test_resume_preserves_larger_allocations_and_configuration(self):
        current = deployment(scope(), "chat", units=150)
        current["tags"] = {"purpose": "synthetic-fixture"}
        current["properties"]["spilloverDeploymentName"] = "owned-spillover"
        usage = quotas()
        usage[0].update(limit=150, currentValue=150)
        plan = capacity.initial_capacity_plan(
            catalog(), usage, models(), "GlobalStandard", existing={"chat": current},
        )
        self.assertEqual(plan["roles"]["chat"]["capacity"], 150)
        self.assertEqual(plan["roles"]["chat"]["additional_capacity"], 0)
        settings = plan["preserved_deployments"]["chat"]
        self.assertEqual(settings["properties"]["raiPolicyName"], "existing-policy")
        self.assertEqual(settings["properties"]["spilloverDeploymentName"], "owned-spillover")
        self.assertEqual(settings["tags"], current["tags"])

    def test_resume_cannot_change_model_or_upgrade_policy(self):
        for field, value in (("name", "different-model"), ("version", "different-version")):
            current = deployment(scope(), "chat")
            current["properties"]["model"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                capacity.initial_capacity_plan(catalog(), quotas(), models(), "GlobalStandard", existing={"chat": current})
        current = deployment(scope(), "chat")
        current["properties"]["versionUpgradeOption"] = "OnceNewDefaultVersionAvailable"
        with self.assertRaises(ValueError):
            capacity.initial_capacity_plan(catalog(), quotas(), models(), "GlobalStandard", existing={"chat": current})


class FoundationStub:
    def __init__(self, *, low_readback=False):
        self.state = {**scope(), "operations": [], "resources": []}
        self.catalog = catalog()
        self.quota = quotas()
        self.calls = []
        self.parameters = None
        self.low_readback = low_readback
        self.account_id = self.state["resource_group_id"] + "/providers/Microsoft.CognitiveServices/accounts/" + self.state["account_name"]

    def az(self, *args, **kwargs):
        self.calls.append(args)
        if args[:2] == ("group", "show"):
            return {"id": self.state["resource_group_id"], "location": self.state["location"],
                    "tags": {"validationRun": self.state["run_id"], "repository": "microsoft-foundry-labs-v1.5"}}
        if args[:2] == ("resource", "list"):
            return []
        if args[:3] == ("cognitiveservices", "model", "list"):
            return deepcopy(self.catalog)
        if args[:3] == ("cognitiveservices", "usage", "list"):
            return deepcopy(self.quota)
        if args[:3] == ("cognitiveservices", "account", "show"):
            return {"id": self.account_id, "location": self.state["location"]}
        if args[:3] == ("deployment", "group", "create"):
            self.parameters = {}
            for item in args[args.index("--parameters") + 1:]:
                key, value = item.split("=", 1)
                self.parameters[key] = json.loads(value) if key == "preservedDeployments" else value
            return {"properties": {"provisioningState": "Succeeded", "outputs": {
                "accountId": {"value": self.account_id},
                "projectId": {"value": self.account_id + "/projects/lab"},
                "projectPrincipalId": {"value": "fixture-principal"},
            }}}
        if args[0] == "rest":
            url = args[args.index("--url") + 1]
            if "/models?" in url:
                return {"value": deepcopy(self.catalog)}
            if "/projects/" in url:
                return {"properties": {"endpoints": {"AI Foundry API": self.state["project_endpoint"]}}}
            role = next(role for role in capacity.ROLES if "/deployments/contoso-" + role in url)
            units = int(self.parameters[role + "Capacity"])
            if self.low_readback and role == "chat":
                units = 10
            return deployment(self.state, role, units=units)
        raise AssertionError(f"Unexpected Azure operation in fixture: {args[:3]}")

    @property
    def creates(self):
        return [args for args in self.calls if args[:3] == ("deployment", "group", "create")]


class FoundationCapacityTests(unittest.TestCase):
    def run_foundation(self, stub, **args):
        with patch.object(environment, "owned", return_value=stub.state), \
                patch.object(environment, "az", side_effect=stub.az), \
                patch.object(environment, "persist") as persist, \
                patch.object(environment, "status"), contextlib.redirect_stdout(io.StringIO()):
            environment.foundation(arguments(**args))
        return persist

    def test_first_arm_submission_already_has_recommended_role_capacities(self):
        stub = FoundationStub()
        self.run_foundation(stub)
        self.assertEqual(len(stub.creates), 1)
        self.assertEqual([stub.parameters[role + "Capacity"] for role in capacity.ROLES], ["100", "100", "10"])
        self.assertNotIn("capacity", stub.parameters)
        self.assertTrue(all(item["ready"] for item in stub.state["initial_model_capacity_verified"]["deployments"].values()))
        create_index = stub.calls.index(stub.creates[0])
        self.assertTrue(any(args[:3] == ("rest", "--method", "get") and "/models?" in args[args.index("--url") + 1]
                            for args in stub.calls[:create_index]))
        self.assertTrue(any(args[:3] == ("cognitiveservices", "usage", "list") for args in stub.calls[:create_index]))
        self.assertFalse(any("--method" in args and args[args.index("--method") + 1] == "patch" for args in stub.calls))

    def test_insufficient_quota_or_metadata_blocks_all_foundation_mutations(self):
        for defect in ("quota", "rates"):
            stub = FoundationStub()
            if defect == "quota":
                stub.quota[0]["limit"] = 99
            else:
                stub.catalog[0]["model"]["skus"][0].pop("rateLimits")
            with self.subTest(defect=defect), self.assertRaises(ValueError):
                self.run_foundation(stub)
            self.assertEqual(stub.creates, [])

    def test_low_actual_rate_limits_fail_without_post_hoc_capacity_patch(self):
        stub = FoundationStub(low_readback=True)
        with self.assertRaisesRegex(ValueError, "TPM/RPM"):
            self.run_foundation(stub)
        self.assertEqual(len(stub.creates), 1)
        self.assertFalse(any("--method" in args and args[args.index("--method") + 1] == "patch" for args in stub.calls))

    def test_plan_is_offline_and_rejects_legacy_uniform_capacity(self):
        with patch.object(environment, "az") as az, patch.object(environment, "persist") as persist, \
                contextlib.redirect_stdout(io.StringIO()) as output:
            environment.main(["foundation"])
        self.assertIn("100000", output.getvalue())
        self.assertIn("Resolve SKU unit rates", output.getvalue())
        az.assert_not_called()
        persist.assert_not_called()
        with patch.object(environment, "az") as az, self.assertRaisesRegex(ValueError, "not --capacity"):
            environment.main(["foundation", "--capacity", "10"])
        az.assert_not_called()

    def test_foundation_region_must_match_the_owned_group(self):
        state = {**scope(), "operations": []}
        with tempfile.TemporaryDirectory() as temporary:
            ledger = Path(temporary) / "scope.json"
            ledger.write_text(json.dumps(state))
            group = {
                "id": state["resource_group_id"], "location": "otherregion",
                "tags": {"validationRun": state["run_id"], "repository": "microsoft-foundry-labs-v1.5"},
            }
            with patch.object(environment, "LEDGER", ledger), patch.object(environment, "az", return_value=group), \
                    self.assertRaisesRegex(ValueError, "region"):
                environment.owned(verify_location=True)

    def test_both_guides_configure_recommendations_during_creation(self):
        for directory in ("docs", "docs/en"):
            setup = (ROOT / directory / "01-setup.md").read_text()
            model = (ROOT / directory / "02-models.md").read_text()
            examples = [line for line in setup.splitlines() if "scripts/azure_environment.py foundation " in line]
            commands = [line for line in examples if "--live" in line]
            with self.subTest(directory=directory):
                self.assertEqual(len(commands), 1)
                self.assertEqual(len([line for line in examples if "--live" not in line]), 1)
                self.assertNotIn("--capacity ", commands[0])
                self.assertIn("--learners 1 --max-capacity 100", commands[0])
                self.assertIn("100,000", model)
                self.assertIn("Custom settings", model)
                self.assertIn("model_capacity.py test", model)


if __name__ == "__main__":
    unittest.main()
