"""Read current actual-cost data for the owned RG; empty billing rows never mean zero cost."""

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
from evidence import Evidence
from workshop import save_json
from azure_environment import az, owned


def main():
    state = owned()
    evidence = Evidence("cost-query")
    now = datetime.now(timezone.utc).isoformat()
    request = {
        "type": "ActualCost", "timeframe": "Custom", "timePeriod": {"from": state["created_at"], "to": now},
        "dataset": {"granularity": "None", "aggregation": {"totalCost": {"name": "Cost", "function": "Sum"}},
                    "grouping": [{"type": "Dimension", "name": "ServiceName"}]},
    }
    response = az(
        "rest", "--method", "post", "--url", state["resource_group_id"] + "/providers/Microsoft.CostManagement/query?api-version=2023-11-01",
        "--headers", "ClientType=GitHubCopilotForAzure", "--body", json.dumps(request),
    )
    evidence.append("actual_cost", response)
    properties = response["properties"]
    if properties.get("nextLink"):
        raise RuntimeError("Cost response is paginated; do not report a partial total.")
    report = {
        "checked_at": now, "resource_group": state["resource_group"],
        "time_period": request["timePeriod"], "columns": properties["columns"], "rows": properties["rows"],
        "billing_status": "reported_rows_available" if properties["rows"] else "not_yet_reported",
        "empty_rows_are_not_zero_cost": True, "cost_authorization": state["cost_authorization"],
        "resource_retention": "no resource deletion authorized", "next_check": "within 24 hours after closeout",
        "continuing_costs": ["Search Basic allocation", "File search storage above free allowance", "logs and retained storage", "future model and agent calls"],
    }
    pricing = ROOT / "validation/current/retail-pricing.json"
    if pricing.exists():
        report["search_retail_reference"] = json.loads(pricing.read_text())
    save_json(ROOT / "validation/current/cost.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
