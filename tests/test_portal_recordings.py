import copy
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import portal_recordings


class PortalRecordingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.destination = self.root / "downloads/portal"
        self.destination.mkdir(parents=True)
        (self.root / "content").mkdir()
        for filename in ("chapters.json", "chapters.en.json"):
            (self.root / "content" / filename).write_bytes((ROOT / "content" / filename).read_bytes())
        chapters = json.loads((self.root / "content/chapters.json").read_text())
        payloads = {"mp4": b"\x00\x00\x00\x18ftypisom", "ko.vtt": b"WEBVTT\n",
                    "en.vtt": b"WEBVTT\n"}
        for suffix, payload in payloads.items():
            (self.destination / f"native-clip.{suffix}").write_bytes(payload)
        evaluation = b'{"test_fixture":true}\n'
        (self.destination / "evaluation-summary.json").write_bytes(evaluation)
        self.source = {
            "capture_method": "playwright-record-video",
            "synthetic_ui": False,
            "privacy_review": {"status": "passed"},
            "recorded_on": "2026-11-04 UTC",
            "evaluation_summary_sha256": hashlib.sha256(evaluation).hexdigest(),
            "clips": [{
                "id": "native-clip", "seconds": 2,
                "title": {"ko": "실제 화면", "en": "Actual screen"},
                "note": {"ko": "관찰 <실행 아님>", "en": "Inspection, not execution"},
                "edits": [{"start_seconds": 0, "end_seconds": 2,
                           "caption": {"ko": "점검", "en": "Inspect"}}],
                "sha256": {suffix: hashlib.sha256(payload).hexdigest()
                           for suffix, payload in payloads.items()},
            }],
            "coverage": [
                {"lab": chapter["id"], "status": "inspection", "clips": ["native-clip"],
                 "note": {"ko": "관찰", "en": "Inspection"}}
                for chapter in chapters if chapter["track"] != "reference"
            ],
        }
        self.enterContext(patch.object(portal_recordings, "ROOT", self.root))
        self.enterContext(patch.object(portal_recordings, "DESTINATION", self.destination))
        self.save()

    def save(self, source=None):
        (self.root / "content/portal-recordings.json").write_text(json.dumps(source or self.source))

    def test_build_preserves_all_module_disclosures_and_bilingual_tracks(self):
        self.source["coverage"][-1].update(status="not_run", clips=[])
        self.save()
        portal_recordings.build()
        html = (self.destination / "index.html").read_text()
        self.assertEqual(html.count('<tr><th scope="row">'), 20)
        self.assertIn("관찰 &lt;실행 아님&gt;", html)
        self.assertIn('data-src="native-clip.ko.vtt" srclang="ko"', html)
        self.assertIn('data-src="native-clip.en.vtt" srclang="en"', html)
        self.assertIn("Not run", html)
        self.assertIn('index.html?clip=native-clip&amp;t=0&amp;lang=en#native-clip', html)

    def test_scene_links_keep_fractional_times_and_open_the_captioned_language_player(self):
        self.source["clips"][0]["edits"][0]["start_seconds"] = 1.5
        self.save()
        portal_recordings.build()
        html = (self.destination / "index.html").read_text()
        for language in ("ko", "en"):
            self.assertIn(
                f'<a lang="{language}" href="index.html?clip=native-clip&amp;t=1.5&amp;lang={language}#native-clip">',
                html,
            )
        self.assertIn("00:01.5 · English captions", html)
        self.assertNotIn(".mp4#t=", html)
        self.assertIn("original portal filming", html)

    def test_embedded_offline_captions_preserve_timing_and_cannot_close_the_data_script(self):
        caption = "Inspect </script><script>unexpected</script>"
        self.source["clips"][0]["edits"][0]["caption"]["en"] = caption
        self.save()
        portal_recordings.build()
        html = (self.destination / "index.html").read_text()
        payload = re.search(
            r'<script type="application/json" id="portal-captions">(.*?)</script>', html, re.S,
        )[1]
        self.assertNotIn("</script>", payload)
        self.assertEqual(json.loads(payload)["native-clip"], [{
            "start": 0, "end": 2, "caption": {"ko": "점검", "en": caption},
        }])

    def test_rejects_reconstruction_unreviewed_media_and_incomplete_coverage(self):
        for modification, message in (
            (lambda s: s.update(synthetic_ui=True), "genuine"),
            (lambda s: s["privacy_review"].update(status="pending"), "privacy review"),
            (lambda s: s["coverage"].pop(), "every module"),
            (lambda s: s["coverage"].reverse(), "reader order"),
            (lambda s: s["coverage"][0].update(clips=[]), "actual clip"),
            (lambda s: s["coverage"][0].update(clips=["missing"]), "Invalid recording coverage"),
        ):
            with self.subTest(message=message):
                source = copy.deepcopy(self.source)
                modification(source)
                self.save(source)
                with self.assertRaisesRegex(ValueError, message):
                    portal_recordings.load_recordings()

    def test_rejects_asset_and_evaluation_tampering(self):
        for filename in ("native-clip.mp4", "native-clip.ko.vtt", "evaluation-summary.json"):
            with self.subTest(filename=filename):
                path = self.destination / filename
                original = path.read_bytes()
                path.write_bytes(original + b"changed")
                with self.assertRaisesRegex(ValueError, "hash mismatch"):
                    portal_recordings.load_recordings()
                path.write_bytes(original)

    def test_rejects_escaping_names_and_symlinked_assets(self):
        source = copy.deepcopy(self.source)
        source["clips"][0]["id"] = "../outside"
        self.save(source)
        with self.assertRaisesRegex(ValueError, "safe local basenames"):
            portal_recordings.load_recordings()
        self.save()
        asset = self.destination / "native-clip.mp4"
        moved = self.root / "outside.mp4"
        asset.rename(moved)
        asset.symlink_to(moved)
        with self.assertRaisesRegex(ValueError, "nonregular"):
            portal_recordings.load_recordings()


if __name__ == "__main__":
    unittest.main()
