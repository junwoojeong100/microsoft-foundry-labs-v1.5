import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import portal_steps


class PortalStepTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = json.loads((ROOT / "content/portal-steps.json").read_text())
        self.source["frames"] = self.source["frames"][:1]
        self.source["privacy_review"]["images"] = 1
        self.frame = self.source["frames"][0]
        self.asset = self.root / self.frame["path"]
        self.asset.parent.mkdir(parents=True)
        self.asset.write_bytes((ROOT / self.frame["path"]).read_bytes())
        (self.root / "content").mkdir()
        recordings = json.loads((ROOT / "content/portal-recordings.json").read_text())
        self.enterContext(patch.object(portal_steps, "ROOT", self.root))
        self.enterContext(patch.object(
            portal_steps.portal_recordings, "load_recordings", return_value=(recordings, []),
        ))
        self.save()

    def save(self, source=None):
        (self.root / "content/portal-steps.json").write_text(json.dumps(source or self.source))

    def test_reviewed_still_keeps_its_recording_identity(self):
        frame, = portal_steps.load_steps()
        self.assertEqual(frame["kind"], "video-frame")
        self.assertEqual(frame["clip"], self.frame["clip"])
        self.assertIn("recorded_on", frame)

    def test_rejects_reconstruction_wrong_language_and_incomplete_privacy_review(self):
        for key, value in (("capture_method", "reconstructed"), ("synthetic_ui", True),
                           ("execution_language", "en"), ("recording_manifest", "other.json")):
            with self.subTest(key=key):
                source = copy.deepcopy(self.source)
                source[key] = value
                self.save(source)
                with self.assertRaisesRegex(ValueError, "genuine Korean-run"):
                    portal_steps.load_steps()
        for key, value in (("status", "pending"), ("images", 2), ("ocr", "pending"),
                           ("visual", "pending"), ("flags", 1)):
            with self.subTest(review=key):
                source = copy.deepcopy(self.source)
                source["privacy_review"][key] = value
                self.save(source)
                with self.assertRaisesRegex(ValueError, "privacy review"):
                    portal_steps.load_steps()

    def test_rejects_wrong_source_hash_and_non_frame_timestamps(self):
        for key, value, message in (
            ("clip", "unknown", "source video/hash"),
            ("source_sha256", "0" * 64, "source video/hash"),
            ("seconds", -1, "in-range source frame"),
            ("seconds", 10_000, "in-range source frame"),
            ("seconds", 10.01, "in-range source frame"),
            ("seconds", float("nan"), "in-range source frame"),
            ("seconds", True, "in-range source frame"),
        ):
            with self.subTest(key=key, value=value):
                source = copy.deepcopy(self.source)
                source["frames"][0][key] = value
                self.save(source)
                with self.assertRaisesRegex(ValueError, message):
                    portal_steps.load_steps()

    def test_rejects_bad_crops_padding_dimensions_and_markers(self):
        for key, value, message in (
            ("crop_xywh", [-1, 0, 1000, 680], "crop escapes"),
            ("crop_xywh", [0, 0, 1601, 1000], "crop escapes"),
            ("crop_xywh", [0, 0, 0, 10], "crop escapes"),
            ("crop_xywh", [0, 20, 999, 680], "dimensions differ"),
            ("padding_ltrb", [65, 14, 14, 14], "annotation padding"),
            ("markers", [], "markers must"),
            ("markers", [{"number": 2, "x": 20, "y": 20}], "markers must"),
            ("markers", [{"number": 1, "x": 9999, "y": 20}], "markers must"),
        ):
            with self.subTest(key=key, value=value):
                source = copy.deepcopy(self.source)
                source["frames"][0][key] = value
                self.save(source)
                with self.assertRaisesRegex(ValueError, message):
                    portal_steps.load_steps()

    def test_rejects_image_tampering_escaping_paths_duplicates_and_symlinks(self):
        original = self.asset.read_bytes()
        self.asset.write_bytes(original + b"changed")
        with self.assertRaisesRegex(ValueError, "signature/hash"):
            portal_steps.load_steps()
        self.asset.write_bytes(original)
        self.frame["path"] = "../outside.png"
        self.save()
        with self.assertRaisesRegex(ValueError, "safe, scoped PNG"):
            portal_steps.load_steps()
        self.frame["path"] = self.asset.relative_to(self.root).as_posix()
        duplicate = copy.deepcopy(self.source)
        duplicate["frames"].append(copy.deepcopy(self.frame))
        duplicate["privacy_review"]["images"] = 2
        self.save(duplicate)
        with self.assertRaisesRegex(ValueError, "distinct"):
            portal_steps.load_steps()
        self.save()
        moved = self.root / "outside.png"
        self.asset.rename(moved)
        self.asset.symlink_to(moved)
        with self.assertRaisesRegex(ValueError, "nonregular"):
            portal_steps.load_steps()


if __name__ == "__main__":
    unittest.main()
