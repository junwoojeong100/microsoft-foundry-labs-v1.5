"""Bind azd locally to the owned project; never provisions or prints credentials."""

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
from workshop import config_values, read_config
from search_lab import configuration


def main():
    state = json.loads((ROOT / "results/azure-environment.json").read_text())
    endpoint, model = read_config()
    if endpoint != state["project_endpoint"]:
        raise ValueError("Local endpoint differs from the owned environment; binding refused.")
    search = configuration()
    environment = state["run_id"]
    config_file = ROOT / ".azure" / environment / ".env"
    if not config_file.exists():
        subprocess.run(["azd", "env", "new", environment, "--no-prompt"], cwd=ROOT, check=True, timeout=60)
    values = {
        "AZURE_SUBSCRIPTION_ID": state["subscription"], "AZURE_TENANT_ID": state["tenant"],
        "AZURE_RESOURCE_GROUP": state["resource_group"], "AZURE_LOCATION": state["location"],
        "AZURE_AI_PROJECT_ID": state["foundation"]["projectId"]["value"],
        "AZURE_AI_PROJECT_ENDPOINT": endpoint, "FOUNDRY_PROJECT_ENDPOINT": endpoint,
        "FOUNDRY_MODEL_DEPLOYMENT_NAME": model, "FOUNDRY_SEARCH_ENDPOINT": search["endpoint"],
        "FOUNDRY_SEARCH_INDEX": search["index"], "FOUNDRY_KNOWLEDGE_BASE": search["knowledge_base"],
        "FOUNDRY_EMBEDDING_DEPLOYMENT_NAME": config_values()["FOUNDRY_EMBEDDING_DEPLOYMENT_NAME"],
        "FOUNDRY_EMBEDDING_ENDPOINT": config_values()["FOUNDRY_EMBEDDING_ENDPOINT"],
    }
    for key, value in values.items():
        if not value:
            raise ValueError(f"Missing {key}.")
        subprocess.run(["azd", "env", "set", key, value, "--environment", environment], cwd=ROOT, check=True, timeout=60, stdout=subprocess.DEVNULL)
    print(f"Bound azd environment {environment}. No provision/deploy or Azure mutation performed.")


if __name__ == "__main__":
    main()
