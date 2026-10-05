from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import re
import shlex
import sys
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_guide
import check_pages
import package_guide
from check_guide import CONCEPT_LABELS, GuideParser, LAB_HEADINGS, command_coverage


def executable_blocks(text):
    return re.findall(r"^```(bash|powershell|python|json|yaml|prompt|instructions|env)\n(.*?)^```[^\S\n]*$", text, re.M | re.S)


def shell_commands(text):
    return [
        shlex.split(line) for language, body in executable_blocks(text) if language == "bash"
        for line in body.replace("\\\n", " ").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def command_boundaries(commands):
    contracts = []
    for command in commands:
        for index, token in enumerate(command):
            if not re.fullmatch(r"(?:samples|scripts)/[\w.-]+\.py", token):
                continue
            if token == "scripts/setup_oidc.py":
                continue
            action = command[index + 1] if index + 1 < len(command) and not command[index + 1].startswith("-") else ""
            flags = tuple(flag for flag in ("--live", "--local", "--approve-tool", "--confirm", "--require-oidc", "--resume") if flag in command)
            bounds = tuple(
                (flag, command[command.index(flag) + 1])
                for flag in ("--max-seconds", "--delay-seconds", "--wait-seconds", "--capacity") if flag in command
            )
            contracts.append((token, action, flags, bounds))
    return Counter(contracts)


REPOSITORY = "https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5"
EXECUTION_BRANCH = "docs/english-live-validation"
WORKFLOWS = (".github/workflows/validate.yml", ".github/workflows/azure-validation.yml")


def english_evidence_path(address):
    for kind in ("blob", "tree"):
        prefix = f"{REPOSITORY}/{kind}/{EXECUTION_BRANCH}/"
        if address.startswith(prefix + "validation/english/"):
            path = unquote(urlparse(address.removeprefix(prefix)).path)
            if ".." in Path(path).parts or not Path(path).is_relative_to("validation/english"):
                raise ValueError(f"English evidence link escapes its scope: {address}")
            return path
    return None


def reference_links(text, source):
    references = []
    for address in re.findall(r"\]\(([^)]+)\)", text):
        if source.startswith("docs/en/") and address in {f"{REPOSITORY}/blob/main/{path}" for path in WORKFLOWS}:
            raise ValueError("English workflow links must use the reviewed branch or checked-out sources.")
        workflow = next((
            path for path in WORKFLOWS
            if address in {f"{REPOSITORY}/blob/{branch}/{path}" for branch in ("main", EXECUTION_BRANCH)}
            or re.fullmatch(rf"{re.escape(REPOSITORY)}/blob/[0-9a-f]{{40}}/{re.escape(path)}", address)
        ), None)
        parsed = urlparse(address)
        if not parsed.scheme and not parsed.netloc and parsed.path:
            path = ((ROOT / source).parent / unquote(parsed.path)).resolve().relative_to(ROOT).as_posix()
            workflow = path if path in WORKFLOWS else None
        if workflow:
            references.append("repository:" + workflow)
        elif (parsed.scheme or parsed.netloc) and not english_evidence_path(address) and not address.startswith(REPOSITORY + "/"):
            references.append(address)
    return references


def render_without_writing(language):
    edition = build_guide.RELEASE["languages"][language]
    artifacts = {}

    def collect(path, text, **kwargs):
        if path not in {ROOT / edition["html"], ROOT / edition["markdown"]}:
            raise AssertionError(f"Unexpected generator output: {path}")
        artifacts[path.name] = text
        return len(text)

    with patch.object(Path, "write_text", autospec=True, side_effect=collect), patch("builtins.print"):
        build_guide.build_language(language)
    return artifacts


class BilingualGuideTests(unittest.TestCase):
    def test_release_metadata_pins_each_language_without_changing_artifact_identity(self):
        release = build_guide.RELEASE
        self.assertEqual(release["edition"], "2026-09-30")
        self.assertEqual(release["artifact"], "Contoso-Foundry-Hands-on-2026-09-30")
        self.assertEqual(release["default_language"], "en")
        self.assertEqual(release["pages_branch"], "main")
        expected = {
            "en": ("index.html", "downloads/GUIDE.en.md", "downloads/" + release["artifact"] + ".en.pdf",
                   "portal-screenshots.en.json", 16, "data/en/receipt.html"),
            "ko": ("index.ko.html", "downloads/GUIDE.ko.md", "downloads/" + release["artifact"] + ".pdf",
                   "portal-screenshots.json", 15, "data/receipt.html"),
        }
        for language, values in expected.items():
            edition = release["languages"][language]
            self.assertEqual(tuple(edition[key] for key in (
                "html", "markdown", "pdf", "portal_manifest", "portal_screenshots",
                "receipt_html",
            )), values)
        self.assertEqual(release["archive"], "downloads/" + release["artifact"] + ".zip")

    def test_translations_preserve_canonical_structure_and_evidence(self):
        korean, ko_sources, ko_capabilities = build_guide.load_content("ko")
        english, en_sources, en_capabilities = build_guide.load_content("en")
        for chapters, sources, capabilities in (
            (korean, ko_sources, ko_capabilities), (english, en_sources, en_capabilities),
        ):
            self.assertEqual(len(chapters), 25)
            self.assertEqual(len([c for c in chapters if c["track"] != "reference"]), 20)
            self.assertEqual(len(capabilities), 68)
            self.assertEqual(len(sources["sources"]), 80)
            self.assertEqual(sum(c["minutes"] for c in chapters if c["track"] == "core"), 285)
            self.assertEqual(sum(c["minutes"] for c in chapters if c["track"] == "advanced"), 335)
            self.assertEqual(sum(c["minutes"] for c in chapters if c["track"] == "wrapup"), 10)
        for original, translation in zip(korean, english, strict=True):
            for key in ("id", "number", "track", "minutes", "sources"):
                self.assertEqual(original[key], translation[key], (original["id"], key))
            if original["learning"]:
                self.assertEqual(original["learning"]["mode"], translation["learning"]["mode"])
        self.assertEqual(
            [(s["id"], s["title"], s["url"]) for s in ko_sources["sources"]],
            [(s["id"], s["title"], s["url"]) for s in en_sources["sources"]],
        )
        self.assertEqual(
            [(c["lab"], c["source"], c["mode"]) for c in ko_capabilities],
            [(c["lab"], c["source"], c["mode"]) for c in en_capabilities],
        )

    def test_orchestration_coverage_distinguishes_hands_on_patterns_from_protocol_references(self):
        for language in ("ko", "en"):
            _, _, capabilities = build_guide.load_content(language)
            rows = {row["source"]: row for row in capabilities if row["lab"] in {"l15", "l15-collaboration"}}
            with self.subTest(language=language):
                self.assertEqual(rows["maf"]["mode"], "직접 실습")
                for pattern in ("sequential", "concurrent", "group-chat", "handoff"):
                    self.assertIn(pattern, rows["maf"]["name"])
                self.assertEqual(rows["a2a"]["mode"], "참고")
                self.assertEqual(rows["hitl"]["mode"], "참고")
                self.assertNotIn("Magentic", json.dumps(rows))

    def test_topbar_names_the_localized_agent_without_the_edition_date(self):
        names = {"ko": "Contoso 구매 에이전트", "en": "Contoso Purchasing Agent"}
        for language, name in names.items():
            edition = build_guide.RELEASE["languages"][language]
            artifacts = render_without_writing(language)
            html = artifacts[edition["html"]]
            with self.subTest(language=language):
                topbar = re.search(r'<header class="topbar">(.*?)</header>', html, re.S)[1]
                label = re.search(
                    r'<span class="edition"><span aria-hidden="true"></span>(.*?)</span>', topbar, re.S,
                )[1]
                self.assertEqual(label, name)
                self.assertNotIn(build_guide.RELEASE["edition"], topbar)
                cover = re.search(r'<section class="print-cover"[^>]*>(.*?)</section>', html, re.S)[1]
                self.assertIn(build_guide.RELEASE["edition"], cover)
                self.assertIn(
                    build_guide.RELEASE["edition"],
                    artifacts[Path(edition["markdown"]).name].split("## ", 1)[0],
                )

    def test_rendered_curriculum_counts_and_order_follow_the_manifest(self):
        for language, edition in build_guide.RELEASE["languages"].items():
            chapters, _, _ = build_guide.load_content(language)
            lab_ids = [chapter["id"] for chapter in chapters if chapter["track"] != "reference"]
            artifacts = render_without_writing(language)
            html = artifacts[edition["html"]]
            parser = GuideParser()
            parser.feed(html)
            labels = build_guide.read_json("reader-labels.json")[language]
            with self.subTest(language=language):
                self.assertEqual(parser.articles, [chapter["id"] for chapter in chapters])
                self.assertEqual(re.findall(r'data-complete="([^"]+)"', html), lab_ids)
                hero = re.search(r'<div class="hero-stats">(.*?)\n', html)[1]
                self.assertEqual(re.findall(r"<strong>(\d+)</strong>", hero), ["11", "8", "1"])
                cover = re.search(r'<section class="print-cover"[^>]*>(.*?)</section>', html, re.S)[1]
                self.assertIn(labels["cover_edition"].format(count=len(lab_ids)), cover)
                self.assertIn(
                    labels["book_intro"].format(count=len(lab_ids)),
                    artifacts[Path(edition["markdown"]).name],
                )

    def test_all_modules_have_complete_english_authoring_structure(self):
        chapters, sources, capabilities = build_guide.load_content("en")
        total = {"blocks": 0, "commands": 0}
        for chapter in chapters:
            if chapter["track"] == "reference":
                continue
            text = (ROOT / chapter["file"]).read_text(encoding="utf-8")
            with self.subTest(chapter=chapter["id"]):
                for heading in LAB_HEADINGS["en"]:
                    self.assertRegex(text, rf"(?m)^## {re.escape(heading)}$")
                for label in CONCEPT_LABELS["en"]:
                    self.assertIn("**" + label, text)
                coverage = command_coverage(text, chapter["file"], "en")
                for key in total:
                    total[key] += coverage[key]
                normalized = build_guide.source_body(chapter, chapters, capabilities, sources, "en")
                self.assertNotRegex(normalized, r"\]\(\.\./")
        edition = build_guide.RELEASE["languages"]["en"]
        self.assertEqual(total, {"blocks": edition["shell_blocks"], "commands": edition["commands"]})

    def test_english_examples_use_english_inputs_and_resolvable_profile_paths(self):
        chapters, _, _ = build_guide.load_content("en")
        for chapter in chapters:
            if "file" not in chapter:
                continue
            text = (ROOT / chapter["file"]).read_text(encoding="utf-8")
            with self.subTest(chapter=chapter["id"]):
                for _, body in executable_blocks(text):
                    self.assertNotRegex(body, r"[가-힣ㄱ-ㅎㅏ-ㅣ\u1100-\u11ff]", "English executable inputs must not reuse Korean literals.")
                    for path in re.findall(r"(?<![\w/])(?:samples|scripts|data)/[\w./-]+|\brequirements[\w.-]*\.txt", body):
                        if path.startswith("data/"):
                            self.assertTrue(path.startswith("data/en/"), path)
                        self.assertTrue((ROOT / path).is_file(), path)
        setup = (ROOT / "docs/en/01-setup.md").read_text(encoding="utf-8")
        self.assertIn("export FOUNDRY_LAB_LANGUAGE=en", setup)
        self.assertIn('$env:FOUNDRY_LAB_LANGUAGE = "en"', setup)

    def test_english_commands_preserve_live_approval_confirmation_and_request_bounds(self):
        chapters, _, _ = build_guide.load_content("en")
        for chapter in chapters:
            if "file" not in chapter:
                continue
            translated_path = ROOT / chapter["file"]
            english = translated_path.read_text(encoding="utf-8")
            korean = (ROOT / "docs" / translated_path.name).read_text(encoding="utf-8")
            with self.subTest(chapter=chapter["id"]):
                korean_commands, english_commands = shell_commands(korean), shell_commands(english)
                self.assertEqual(command_boundaries(korean_commands), command_boundaries(english_commands))
                for command in english_commands:
                    if "samples/toolbox_lab.py" in command and "call" in command:
                        self.assertIn("--approve-tool", command)
                        self.assertEqual(command[command.index("--approve-tool") + 1], command[command.index("--tool") + 1])
                    if "samples/memory_lab.py" in command and "forget" in command:
                        self.assertIn("--live", command)
                        self.assertEqual(command[command.index("--confirm") + 1], "ACTUAL_MEMORY_ID")
                    if "samples/optimizer_lab.py" in command and "--require-oidc" in command:
                        self.assertIn("--live", command)
                        self.assertNotIn("holdout", command)
                        if "--suite" in command:
                            self.assertEqual(
                                command[command.index("--suite") + 1],
                                "automated-v3" if "--resume" in command else "automated-v5",
                            )


    def test_business_and_quality_gates_are_unchanged_without_opening_the_holdout(self):
        profile = json.loads((ROOT / "data/en/profile-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(profile["business_contract"], {
            "currency": "KRW", "price_caps_include_vat": True,
            "per_item_caps": {"laptop": 1500000, "monitor": 350000, "keyboard": 120000},
            "regular_laptop_replacement_months": 36,
            "team_lead_only_up_to_and_including_krw": 2000000,
            "additional_procurement_approval_strictly_above_krw": 2000000,
            "draft_integer_quantity_minimum": 1, "draft_integer_quantity_maximum": 10,
            "draft_status": "draft_requires_human_approval", "order_submitted": False,
            "actual_orders_payments_approvals": False,
            "sku_ids": ["NB-14", "MON-27", "KB-01"],
            "policy_ids": ["CONTOSO-PROC-2026-09", "CONTOSO-EXP-2026-09", "CONTOSO-SEC-2026-09"],
        })
        gates = {
            "required_dev_cases": 30, "required_holdout_cases": 10, "minimum_pass_rate": 0.9,
            "native_pass_threshold": 4, "zero_tolerance_categories": ["safety", "access"],
        }
        for directory in ("data", "data/en"):
            rubric = json.loads((ROOT / directory / "evaluation/v3/rubric.json").read_text(encoding="utf-8"))
            self.assertEqual({key: rubric[key] for key in gates}, gates)
            self.assertFalse(rubric["human_review"]["required"])
            self.assertEqual(rubric["human_review"]["status"], "optional_guidance_only")
        self.assertEqual({key: profile["v3_gate"][key] for key in gates}, gates)
        self.assertEqual(profile["v3_gate"]["calibration_controls"], 8)
        action_examples = dict(executable_blocks((ROOT / "docs/en/06-actions.md").read_text(encoding="utf-8")))
        self.assertEqual(json.loads(action_examples["json"]), {
            "sku": "NB-14", "quantity": 2, "total_krw": 2900000,
            "status": "draft_requires_human_approval", "required_approvals": ["team_lead", "procurement"],
            "order_submitted": False,
        })

    def test_official_and_historical_urls_survive_profile_specific_workflow_links(self):
        chapters, _, _ = build_guide.load_content("en")
        for chapter in chapters:
            if "file" not in chapter:
                continue
            english = (ROOT / chapter["file"]).read_text(encoding="utf-8")
            original = "docs/" + Path(chapter["file"]).name
            with self.subTest(chapter=chapter["id"]):
                self.assertEqual(
                    reference_links((ROOT / original).read_text(encoding="utf-8"), original),
                    reference_links(english, chapter["file"]),
                    "Only the reviewed workflow/evidence links may differ; official and historical sources must remain exact.",
                )

    def test_english_workflow_sources_do_not_link_to_pages_hidden_directory(self):
        text = (ROOT / "docs/en/22-delivery.md").read_text(encoding="utf-8")
        links = re.findall(r"\]\(([^)]+/\.github/workflows/[^)]+)\)", text)
        self.assertEqual(len(links), 2)
        for address in links:
            self.assertRegex(address, rf"^{re.escape(REPOSITORY)}/blob/[0-9a-f]{{40}}/\.github/workflows/")

    def test_source_image_sets_are_english_16_and_korean_15(self):
        paths = {}
        for language, edition in build_guide.RELEASE["languages"].items():
            chapters, sources, capabilities = build_guide.load_content(language)
            images = set()
            for chapter in chapters:
                body = build_guide.source_body(chapter, chapters, capabilities, sources, language)
                images.update(re.findall(r"!\[[^\]]*\]\((assets/portal/[^)]+)\)", body))
            self.assertEqual(len(images), edition["portal_screenshots"])
            self.assertEqual(images, {capture["path"] for capture in build_guide.load_portal_captures(language)})
            archived = build_guide.read_json(edition["portal_manifest"])["archived_captures"]
            self.assertTrue(images.isdisjoint(capture["path"] for capture in archived))
            directory = "assets/portal/en" if language == "en" else "assets/portal"
            self.assertTrue(all(Path(path).parent == Path(directory) for path in images))
            paths[language] = {Path(path).name for path in images}
        self.assertEqual(paths["en"], paths["ko"] | {"18-resource-group.png"})

    def test_archived_captures_keep_original_fingerprints_and_capture_times(self):
        expected = {
            "ko": [
                ("14-fine-tuning.png", "2026-09-30T07:30:08.887Z", "7704db26c5dbad1c9ff85d30d85782017d586f94c7b7dba06f905d3bf805844b"),
                ("15-voice-setup.png", "2026-09-30T07:31:46.072Z", "01cea0d080fe6d926ca36a30157e6952b7e3886c86c19963cb2d78185ac7dfff"),
            ],
            "en": [
                ("14-fine-tuning.png", "2026-09-30T13:42:59.449Z", "ff932830fb6f47665d3ce63eb952e3ef488b647799080bb3b0c914dfbb1e25bb"),
                ("15-voice-setup.png", "2026-09-30T13:44:56.166Z", "8d89de499d03f6aacc6063a40803ab65c11370bf5539f0f5557b0a29df970781"),
            ],
        }
        for language, edition in build_guide.RELEASE["languages"].items():
            manifest = build_guide.read_json(edition["portal_manifest"])
            archived = manifest["archived_captures"]
            with self.subTest(language=language):
                self.assertEqual(
                    [(Path(item["path"]).name, item["captured_at"], item["sha256"]) for item in archived],
                    expected[language],
                )
                self.assertEqual(
                    build_guide.load_portal_captures(language, include_archived=True),
                    [*manifest["captures"], *archived],
                )

    def test_archived_captures_still_require_unique_paths_and_full_provenance(self):
        for language, edition in build_guide.RELEASE["languages"].items():
            original = build_guide.read_json(edition["portal_manifest"])
            for defect in ("duplicate", "sha256", "captured_at", "route", "masked", "purpose"):
                manifest = deepcopy(original)
                if defect == "duplicate":
                    manifest["archived_captures"].append(deepcopy(manifest["captures"][0]))
                else:
                    manifest["archived_captures"][0][defect] = ""
                with self.subTest(language=language, defect=defect), patch.object(
                    build_guide, "read_json", return_value=manifest,
                ), self.assertRaises(ValueError):
                    build_guide.load_portal_captures(language)

    def test_reader_labels_have_the_same_keys_and_are_translated(self):
        labels = build_guide.read_json("reader-labels.json")
        self.assertEqual(set(labels["en"]), set(labels["ko"]))
        self.assertEqual(set(labels["en"]["js"]), set(labels["ko"]["js"]))
        self.assertFalse(re.search(r"[가-힣]", json.dumps(labels["en"], ensure_ascii=False)))
        self.assertNotIn("Korean fixture", json.dumps(labels["en"]))
        for language, edition in build_guide.RELEASE["languages"].items():
            for key in ("cover_boundary", "book_boundary"):
                self.assertNotIn("{validation}", labels[language][key])
                self.assertNotIn("validation/current", labels[language][key])
        for original, translated in zip(*[
            build_guide.load_content(language)[0] for language in ("ko", "en")
        ], strict=True):
            for key in ("title", "summary", "status"):
                self.assertFalse(re.search(r"[가-힣]", translated[key]), (original["id"], key))

    def test_both_readers_keep_execution_records_outside_the_guide(self):
        labels = build_guide.read_json("reader-labels.json")
        for language, reading in (("en", "Read → do one step"), ("ko", "읽기 → 한 단계 실행")):
            self.assertIn(reading, labels[language]["reader_note"])
            self.assertNotIn("validation/current", labels[language]["book_boundary"])
            directory = "docs/en" if language == "en" else "docs"
            text = (ROOT / directory / "08-evaluation.md").read_text()
            self.assertNotIn("validation/current", text)
            self.assertNotIn("4.9167", text)
            self.assertIn("results/azure-environment.json", text)

    def test_missing_translation_fails_instead_of_falling_back_to_korean(self):
        read_json = build_guide.read_json

        def missing_chapter(name):
            value = read_json(name)
            return value[:-1] if name == "chapters.en.json" else value

        with patch.object(build_guide, "read_json", side_effect=missing_chapter):
            with self.assertRaisesRegex(ValueError, "every canonical chapter"):
                build_guide.load_content("en")

    def test_missing_english_capture_manifest_stops_build_without_writing_artifacts(self):
        edition = build_guide.RELEASE["languages"]["en"]
        with patch.dict(edition, {"portal_manifest": "missing-english-captures.json"}):
            with patch.object(Path, "write_text") as write:
                with self.assertRaisesRegex(ValueError, "Missing or nonregular portal manifest"):
                    build_guide.build_language("en")
                write.assert_not_called()

    def test_english_cannot_reuse_the_korean_capture_manifest(self):
        edition = build_guide.RELEASE["languages"]["en"]
        with patch.dict(edition, {"portal_manifest": build_guide.RELEASE["languages"]["ko"]["portal_manifest"]}):
            with self.assertRaisesRegex(ValueError, "owned contoso-workshop-en project"):
                build_guide.load_portal_captures("en")

    def test_capture_files_and_parent_directories_cannot_be_symlinks(self):
        captures = build_guide.load_portal_captures("ko")
        image = ROOT / captures[0]["path"]
        is_symlink = Path.is_symlink
        for target in (image, image.parent):
            with self.subTest(target=target), patch.object(
                Path, "is_symlink", autospec=True,
                side_effect=lambda path: path == target or is_symlink(path),
            ):
                with self.assertRaisesRegex(ValueError, "nonregular portal screenshot"):
                    build_guide.load_portal_captures("ko")

    def test_missing_or_changed_portal_images_are_rejected(self):
        image = ROOT / build_guide.load_portal_captures("ko")[0]["path"]
        is_file = Path.is_file
        with patch.object(Path, "is_file", autospec=True, side_effect=lambda path: path != image and is_file(path)):
            with self.assertRaisesRegex(ValueError, "Missing or nonregular portal screenshot"):
                build_guide.load_portal_captures("ko")
        read_bytes = Path.read_bytes
        with patch.object(
            Path, "read_bytes", autospec=True,
            side_effect=lambda path: read_bytes(path) + (b"changed" if path == image else b""),
        ):
            with self.assertRaisesRegex(ValueError, "signature/hash mismatch"):
                build_guide.load_portal_captures("ko")

    def test_portal_images_without_localized_provenance_cannot_render(self):
        chapters, sources, capabilities = build_guide.load_content("ko")
        body = build_guide.source_body(chapters[0], chapters, capabilities, sources, "ko")
        with self.assertRaisesRegex(ValueError, "no capture in this language's manifest"):
            build_guide.render_chapter(
                chapters[0], body, {}, None, chapters[1], {}, build_guide.read_json("reader-labels.json")["ko"],
            )

    def test_korean_render_preserves_its_evidence_and_receipt_paths(self):
        artifacts = render_without_writing("ko")
        parser = GuideParser()
        parser.feed(artifacts["index.ko.html"])
        self.assertEqual(parser.language, "ko")
        self.assertFalse(parser.remote_assets)
        self.assertFalse(any(link.startswith(("validation/", "results/")) for link in parser.links))
        self.assertIn("data/receipt.html", parser.links)
        self.assertNotIn("data/en/receipt.html", parser.links)
        self.assertEqual(len({image["src"] for image in parser.images if image["src"].startswith("assets/portal/")}), 15)
        self.assertIn("](" + build_guide.RELEASE["site_url"] + "data/receipt.html)", artifacts["GUIDE.ko.md"])
        self.assertIn("[English](GUIDE.en.md)", artifacts["GUIDE.ko.md"])

    def test_package_rejects_private_state_including_nested_english_evidence(self):
        for path in (
            ".env", ".venv/lib/package.py", "data/.azure/config.json", "content/.git/config",
            "samples/.foundry/results.json", "assets/node_modules/package.json",
            "validation/english/results/response.json", "tests/__pycache__/test.pyc",
            "validation/current/instructions.json", "validation/automated-v3/ci-release.json",
        ):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "Private or generated cloud data"):
                package_guide.check_package_path(path)
        for path in (
            "assets/portal/en/18-resource-group.png", "data/en/receipt.html", ".env.example",
            "downloads/replay/Contoso-Foundry-Replay.en.mp4",
        ):
            package_guide.check_package_path(path)


class BilingualGuideArtifactTests(unittest.TestCase):
    def test_english_is_default_and_all_html_has_pages_links(self):
        release = build_guide.RELEASE
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for language, edition in release["languages"].items():
            html = (ROOT / edition["html"]).read_text(encoding="utf-8")
            parser = GuideParser()
            parser.feed(html)
            self.assertEqual(parser.language, language)
            self.assertFalse(parser.remote_assets)
            self.assertIn(edition["markdown"], parser.links)
            self.assertIn(edition["pdf"], parser.links)
            for section in (
                re.search(r'<footer class="site-footer">(.*?)</footer>', html, re.S)[1],
                re.search(r'<section class="print-cover"[^>]*>(.*?)</section>', html, re.S)[1],
            ):
                links = GuideParser()
                links.feed(section)
                self.assertFalse(any(link.startswith(("validation/", "results/")) for link in links.links))
                self.assertIn(edition["receipt_html"], links.links)
        for relative in ("index.ko.html", "data/receipt.html", "data/en/receipt.html"):
            self.assertIn(release["site_url"] + relative, readme)
        self.assertIn(release["site_url"], readme)

    def test_english_render_requires_actual_english_capture_assets(self):
        artifacts = render_without_writing("en")
        parser = GuideParser()
        parser.feed(artifacts["index.html"])
        self.assertEqual(parser.language, "en")
        self.assertEqual(len({image["src"] for image in parser.images if image["src"].startswith("assets/portal/en/")}), 16)
        self.assertFalse(any(link.startswith(("validation/", "results/")) for link in parser.links))
        self.assertIn("data/en/receipt.html", parser.links)
        reader_note = re.search(
            r'<div class="reader-note" id="reader-note">(.*?)</div>', artifacts["index.html"], re.S,
        )[1]
        self.assertIn("Read → do one step → check the result", reader_note)
        self.assertIn("approve live costs", reader_note)
        note_links = GuideParser()
        note_links.feed(reader_note)
        self.assertIn("#sources", note_links.links)
        boundary = artifacts["GUIDE.en.md"].split("## ", 1)[0]
        self.assertIn("Execution boundary", boundary)
        self.assertNotIn("../validation/", boundary)
        self.assertIn("](" + build_guide.RELEASE["site_url"] + "data/en/receipt.html)", boundary)

    def test_all_source_links_resolve_without_fallbacks(self):
        for language in build_guide.RELEASE["languages"]:
            chapters, sources, capabilities = build_guide.load_content(language)
            for chapter in chapters:
                body = build_guide.source_body(chapter, chapters, capabilities, sources, language)
                for address in re.findall(r"\]\(([^)]+)\)", body):
                    parsed = urlparse(address)
                    local = english_evidence_path(address)
                    if local is None and not parsed.scheme and not parsed.netloc:
                        local = unquote(parsed.path)
                    if not local:
                        continue
                    with self.subTest(language=language, chapter=chapter["id"], address=address):
                        path = (ROOT / local).resolve()
                        self.assertTrue(path.is_relative_to(ROOT))
                        self.assertTrue(path.is_file(), f"Missing required source asset/evidence: {local}")

    def test_markdown_html_links_use_pages(self):
        for edition in build_guide.RELEASE["languages"].values():
            text = (ROOT / edition["markdown"]).read_text(encoding="utf-8")
            html_links = re.findall(r"\]\(([^)]+\.html(?:#[^)]*)?)\)", text)
            self.assertTrue(html_links)
            self.assertTrue(all(link.startswith(build_guide.RELEASE["site_url"]) for link in html_links))
            boundary = text.split("## ", 1)[0]
            self.assertNotIn("../validation/", boundary)
            self.assertIn(f"]({build_guide.RELEASE['site_url']}{edition['receipt_html']})", boundary)

    def test_markdown_download_links_resolve_from_downloads_directory(self):
        for language, edition in build_guide.RELEASE["languages"].items():
            book = ROOT / edition["markdown"]
            links = re.findall(r"\]\(([^)\s]+)\)", book.read_text(encoding="utf-8"))
            checked = set()
            for link in links:
                address = urlparse(link)
                if address.scheme or address.netloc or not address.path:
                    continue
                target = (book.parent / unquote(address.path)).resolve()
                with self.subTest(book=book.name, link=link):
                    self.assertTrue(target.is_relative_to(ROOT))
                    self.assertTrue(target.is_file(), "Images and source links must work inside the extracted kit.")
                checked.add(target)
            chapters, sources, capabilities = build_guide.load_content(language)
            required = set()
            for chapter in chapters:
                body = build_guide.source_body(chapter, chapters, capabilities, sources, language)
                for link in re.findall(r"\]\(([^)\s]+)\)", body):
                    address = urlparse(link)
                    if address.scheme or address.netloc or not address.path or address.path.endswith(".html"):
                        continue
                    required.add((ROOT / unquote(address.path)).resolve())
            self.assertLessEqual(required, checked, "Every active source link must survive portable Markdown generation.")

    def test_book_link_rebasing_preserves_fragments_queries_and_external_links(self):
        source = (
            "[file](data/policy.md#rule) ![image](assets/portal/a%20b.png) "
            "[English](downloads/GUIDE.en.md) [section](#l08) "
            "[web](index.ko.html?print=1#l08) [external](https://example.invalid/a)"
        )
        converted = build_guide.portable_book_links(source, "downloads/GUIDE.ko.md")
        self.assertIn("](../data/policy.md#rule)", converted)
        self.assertIn("](../assets/portal/a%20b.png)", converted)
        self.assertIn("[English](GUIDE.en.md)", converted)
        self.assertIn("[section](#l08)", converted)
        self.assertIn(f"]({build_guide.RELEASE['site_url']}index.ko.html?print=1#l08)", converted)
        self.assertIn("[external](https://example.invalid/a)", converted)

    def test_pages_checker_compares_both_editions_and_both_receipts(self):
        base = build_guide.RELEASE["site_url"]

        def local_response(address):
            self.assertTrue(address.startswith(base))
            relative = unquote(address.removeprefix(base)) or "index.html"
            return (ROOT / relative).read_bytes()

        with patch.object(check_pages, "fetch", side_effect=local_response), patch("builtins.print"):
            report = check_pages.check()
        self.assertEqual({row["url"] for row in report["html"]}, {
            base + "index.html", base + "index.ko.html", base + "data/receipt.html", base + "data/en/receipt.html",
        })
        self.assertGreater(report["linked_files_checked"], 50)

    def test_pages_checker_rejects_stale_published_content(self):
        with patch.object(check_pages, "fetch", return_value=b"outdated HTML"):
            with self.assertRaisesRegex(ValueError, "differs from the generated source"):
                check_pages.check()


if __name__ == "__main__":
    unittest.main()
