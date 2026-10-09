"""Tests that need the maintainer-only validation assets skip in the learner kit, which does not ship them."""

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATHS = tuple(json.loads((ROOT / "content/maintainer-only.json").read_text(encoding="utf-8"))["paths"])
IN_KIT = not any((ROOT / path).exists() for path in PATHS)
requires_maintainer_assets = unittest.skipIf(IN_KIT, "Maintainer-only validation assets are not part of the learner kit.")
