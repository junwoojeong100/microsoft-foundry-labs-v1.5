"""Run the generated loopback Hosted server. It inherits your shell environment and adds the nonsecret project settings from .env."""

import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
from search_lab import configuration
from lab_cli import run
from workshop import config_values, read_config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", choices=["invocations", "responses"], default="invocations")
    parser.add_argument("--port", type=int, default=8088)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        raise ValueError("Local port must be 1024..65535.")
    endpoint, model = read_config()
    search = configuration()
    values = config_values()
    environment = {
        **os.environ, "FOUNDRY_PROJECT_ENDPOINT": endpoint, "FOUNDRY_MODEL_DEPLOYMENT_NAME": model,
        "FOUNDRY_SEARCH_ENDPOINT": search["endpoint"], "FOUNDRY_SEARCH_INDEX": search["index"],
        "FOUNDRY_KNOWLEDGE_BASE": search["knowledge_base"],
        "FOUNDRY_EMBEDDING_DEPLOYMENT_NAME": values["FOUNDRY_EMBEDDING_DEPLOYMENT_NAME"],
        "FOUNDRY_EMBEDDING_ENDPOINT": values["FOUNDRY_EMBEDDING_ENDPOINT"],
        "FOUNDRY_AUTH_MODE": "cli", "OTEL_SDK_DISABLED": "true",
        "CONTOSO_EVIDENCE_DIRECTORY": str(ROOT / "results"),
        "CONTOSO_LOCAL_PORT": str(args.port),
    }
    project = ROOT / ".build" / ("contoso-responses" if args.protocol == "responses" else "contoso")
    subprocess.run([sys.executable, str(project / "main.py")], env=environment, cwd=project, check=True)


if __name__ == "__main__":
    run(main)
