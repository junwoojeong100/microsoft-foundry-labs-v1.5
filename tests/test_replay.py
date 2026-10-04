import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_replay import player, timestamp


class ReplaySourceTests(unittest.TestCase):
    def test_both_videos_cover_every_active_module_in_reader_order(self):
        source = json.loads((ROOT / "content/replay.json").read_text())
        chapters = json.loads((ROOT / "content/chapters.json").read_text())
        expected = [row["id"] for row in chapters if row["track"] != "reference"]
        self.assertEqual(len(expected), 20)
        self.assertEqual([row["id"] for row in source["chapters"]], expected)
        for chapter in source["chapters"]:
            self.assertTrue(chapter["commands"])
            for language in ("ko", "en"):
                self.assertEqual(len(chapter[language]["steps"]), 3)
                self.assertGreater(len(chapter[language]["narration"]), 180)
        self.assertIn("not a live portal recording", source["notice"]["en"])

    def test_replay_source_never_imports_execution_results_into_the_guide(self):
        code = (ROOT / "scripts/build_replay.py").read_text()
        renderer = (ROOT / "scripts/render-replay.js").read_text()
        self.assertNotIn("validation/current", code + renderer)
        self.assertNotIn("instructions.json", code + renderer)
        source = (ROOT / "content/replay.json").read_text()
        self.assertIn("azure_environment.py foundation", source)
        self.assertIn("operations_status.py", source)
        self.assertNotIn("measured_v2_improvement", source)

    def test_caption_timestamps_preserve_hour_and_millisecond_boundaries(self):
        self.assertEqual(timestamp(0), "00:00:00,000")
        self.assertEqual(timestamp(59.999), "00:00:59,999")
        self.assertEqual(timestamp(3600.005, "."), "01:00:00.005")

    def test_player_displays_current_numbers_not_legacy_ids(self):
        source = json.loads((ROOT / "content/replay.json").read_text())
        chapters = json.loads((ROOT / "content/chapters.json").read_text())
        labs = [chapter for chapter in chapters if chapter["track"] != "reference"]
        timeline = [
            {"id": chapter["id"], "number": chapter["number"], "title": chapter["title"],
             "start": index * 30, "end": (index + 1) * 30}
            for index, chapter in enumerate(labs)
        ]
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            for language in ("ko", "en"):
                (destination / f"chapters.{language}.json").write_text(json.dumps(timeline))
            player(source, destination)
            html = (destination / "index.html").read_text()
        for chapter in labs:
            self.assertIn(f'L{chapter["number"]} · {chapter["title"]}</button>', html)
        self.assertNotIn("L21 ·", html)
        self.assertNotIn("L22 ·", html)


if __name__ == "__main__":
    unittest.main()
