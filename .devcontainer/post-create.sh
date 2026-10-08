#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [[ ! -e .venv && ! -L .venv ]]; then
  python3.13 -m venv .venv
fi
if [[ ! -x .venv/bin/python ]]; then
  echo "ERROR: .venv exists but has no usable Python. Preserve it and inspect the setup log." >&2
  exit 1
fi

.venv/bin/python -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 13) else 'ERROR: Expected Python 3.13. Preserve the existing environment; do not overwrite it.')"
.venv/bin/python -m pip install -r requirements-tools.txt
.venv/bin/python -m pip check

if [[ ! -e .env && ! -L .env ]]; then
  cp .env.example .env
fi

echo "Lab tools ready. Open a new terminal and follow L01. No Microsoft Azure sign-in or resource creation was performed."
