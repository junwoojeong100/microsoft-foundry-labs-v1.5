from copy import deepcopy
from html import escape, unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_guide
from check_guide import BRIEF_LABELS, HANDOFF_LABELS, LAB_HEADINGS, command_coverage, portal_coverage


def explanation(rows):
    return (
        '<div class="command-explanation" markdown="1">\n\n**명령 해설**\n\n'
        "| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |\n"
        "| --- | --- | --- |\n"
        + "\n".join(rows)
        + "\n\n</div>\n"
    )


class ReadingSurfaceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.details = []
        self.exposed_python = []
        self.hidden_commands = []

    def handle_starttag(self, tag, attrs):
        classes = dict(attrs).get("class", "").split()
        if tag == "details":
            self.details.append("implementation-detail" in classes)
        elif tag == "code":
            if "language-python" in classes and not self.details:
                self.exposed_python.append(classes)
            if {"language-bash", "language-powershell"} & set(classes) and any(self.details):
                self.hidden_commands.append(classes)

    def handle_endtag(self, tag):
        if tag == "details":
            self.details.pop()


class GuideAuthoringTests(unittest.TestCase):
    def test_learner_prose_uses_full_product_names_without_renaming_literal_interfaces(self):
        for language in ("ko", "en"):
            chapters, _, _ = build_guide.load_content(language)
            texts = {chapter["file"]: (ROOT / chapter["file"]).read_text()
                     for chapter in chapters if "file" in chapter}
            readme = build_guide.RELEASE["languages"][language]["readme"]
            texts[readme] = (ROOT / readme).read_text()
            labels = build_guide.read_json("reader-labels.json")[language]
            texts["labels"] = json.dumps(labels, ensure_ascii=False)
            official = sorted(
                json.loads((ROOT / "content/product-names.json").read_text(encoding="utf-8"))["official"],
                key=len, reverse=True,
            )
            for name, text in texts.items():
                rendered = build_guide.markdown.markdown(text, extensions=["fenced_code", "tables", "md_in_html"])
                rendered = re.sub(r"<(?:pre|code)\b[^>]*>.*?</(?:pre|code)>", "", rendered, flags=re.S)
                plain = unescape(re.sub(r"<[^>]+>", " ", rendered))
                for literal in (*official, "Microsoft Azure", "Microsoft Foundry", "MICROSOFT AZURE",
                                "Azure AI User", "Foundry User", "New Foundry", "Azure OpenAI endpoint"):
                    plain = plain.replace(literal, "")
                with self.subTest(language=language, source=name):
                    self.assertNotRegex(plain, r"(?<![A-Za-z0-9_-])(?:Azure|Foundry|AZURE|FOUNDRY)(?![A-Za-z0-9_-])")
                    self.assertNotIn("Microsoft Microsoft", text)

    def test_service_names_follow_the_official_microsoft_spelling(self):
        names = json.loads((ROOT / "content/product-names.json").read_text(encoding="utf-8"))
        official = sorted([*names["official"], *names["incomplete"].values()], key=len, reverse=True)
        for language in ("ko", "en"):
            chapters, _, capabilities = build_guide.load_content(language)
            texts = {chapter["file"]: (ROOT / chapter["file"]).read_text()
                     for chapter in chapters if "file" in chapter}
            texts[build_guide.RELEASE["languages"][language]["readme"]] = (
                ROOT / build_guide.RELEASE["languages"][language]["readme"]).read_text()
            texts["samples/README"] = (ROOT / ("samples/README.ko.md" if language == "ko" else "samples/README.md")).read_text()
            texts["chapters"] = json.dumps(
                [{key: chapter.get(key, "") for key in ("title", "summary", "status")} for chapter in chapters],
                ensure_ascii=False,
            )
            texts["capabilities"] = json.dumps(capabilities, ensure_ascii=False)
            for name, text in texts.items():
                plain = re.sub(r"`[^`\n]*`", " ", re.sub(r"```.*?```", " ", text, flags=re.S))
                with self.subTest(language=language, source=name):
                    for inexact, exact in names["inexact"].items():
                        self.assertNotIn(inexact, plain, f"Write {exact!r}, not {inexact!r}.")
                    for exact in official:
                        plain = plain.replace(exact, " ")
                    for short, exact in names["incomplete"].items():
                        self.assertNotIn(short, plain, f"Write {exact!r}, not {short!r}.")

    def test_maintainer_codespaces_is_not_a_learner_installation_requirement(self):
        config = json.loads((ROOT / ".devcontainer/devcontainer.json").read_text())
        self.assertEqual(config["features"]["ghcr.io/devcontainers/features/azure-cli:1"]["version"],
                         build_guide.RELEASE["azure_cli"])
        self.assertIn("3.13", config["image"])
        self.assertEqual(config["otherPortsAttributes"]["onAutoForward"], "ignore")
        self.assertNotIn("forwardPorts", config)
        for directory in ("docs", "docs/en"):
            setup = (ROOT / directory / "01-setup.md").read_text()
            with self.subTest(directory=directory):
                self.assertIn('id="l01-codespaces"', setup)
                self.assertIn('id="l01-sign-in"', setup)
                self.assertIn("https://portal.azure.com/", setup)
                self.assertIn("https://ai.azure.com/", setup)
                self.assertNotIn('class="codespaces-path"', setup)
                self.assertNotRegex(setup, r"az login|pip install|python -m venv")

    def test_portal_guard_rejects_executable_blocks_and_unfenced_commands(self):
        steps = (
            "## Steps\n| Step | Click or enter | Expected screen or value | If it fails |\n"
            "| --- | --- | --- | --- |\n| 1 | Open. | Visible. | Stop. |\n"
        )
        self.assertEqual(portal_coverage(steps, "fixture", "en"), {"tables": 1, "steps": 1})
        for kind in ("bash", "powershell", "python", "env", "javascript", "yaml"):
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, "executable code"):
                portal_coverage(steps + f"\n```{kind}\nnot portal input\n```\n", "fixture", "en")
        for command in ("python samples/a.py", "az login", "azd deploy", "pip install sdk", "curl https://example.invalid"):
            with self.subTest(command=command), self.assertRaisesRegex(ValueError, "terminal commands"):
                portal_coverage(steps + "\n" + command, "fixture", "en")

    def test_portal_guard_rejects_missing_outcomes_failure_guidance_and_order_gaps(self):
        header = "## Steps\n| Step | Click or enter | Expected screen or value | If it fails |\n| --- | --- | --- | --- |\n"
        for rows in (
            "", "| 2 | Open. | Visible. | Stop. |\n",
            "| 1 | Open. | Visible. | Stop. |\n| 1 | Select. | Selected. | Stop. |\n",
            "| 1 | Open. | | Stop. |\n", "| 1 | Open. | Visible. | |\n",
            "| 1 | Open. | Visible. |\n",
        ):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                portal_coverage(header + rows, "fixture", "en")
        with self.assertRaisesRegex(ValueError, "ordered click/input"):
            portal_coverage("## Steps\nRead the docs.", "fixture", "en")
        self.assertEqual(portal_coverage(
            header + "| 1 | Open. | Visible. | Stop. |\n\n"
            + header.removeprefix("## Steps\n") + "| 1 | Select. | Selected. | Stop. |\n",
            "fixture", "en",
        ), {"tables": 2, "steps": 2})

    def test_all_modules_end_with_saved_results_and_resolvable_next_steps(self):
        for language in ("ko", "en"):
            chapters, _, _ = build_guide.load_content(language)
            for chapter in chapters:
                if chapter["track"] == "reference":
                    continue
                text = (ROOT / chapter["file"]).read_text()
                handoff = re.search(r'<div class="lab-handoff" markdown="1">(.*?)</div>', text, re.S)
                with self.subTest(language=language, chapter=chapter["id"]):
                    self.assertEqual(text.count('class="lab-handoff"'), 1)
                    self.assertIsNotNone(handoff)
                    self.assertGreater(handoff.start(), text.index("## " + LAB_HEADINGS[language][-1]))
                    for label in HANDOFF_LABELS[language]:
                        self.assertIn("**" + label, handoff[1])
                    self.assertRegex(handoff[1], r"\]\(#[\w-]+\)")

    def test_python_references_are_expandable_without_hiding_execution_commands(self):
        for language in ("ko", "en"):
            chapters, sources, capabilities = build_guide.load_content(language)
            captures = {item["path"]: item for item in build_guide.load_guide_captures(language)}
            ui = build_guide.read_json("reader-labels.json")[language]
            for chapter in chapters:
                if chapter["track"] == "reference":
                    continue
                body = build_guide.source_body(chapter, chapters, capabilities, sources, language)
                html = build_guide.render_chapter(
                    chapter, body, {item["id"]: item for item in sources["sources"]},
                    None, None, captures, ui,
                )
                parser = ReadingSurfaceParser()
                parser.feed(html)
                with self.subTest(language=language, chapter=chapter["id"]):
                    self.assertFalse(parser.exposed_python)
                    self.assertFalse(parser.hidden_commands)
                    self.assertFalse(parser.details)

    def test_reentry_reuses_owned_resources_without_recreating_or_reinstalling_them(self):
        for directory in ("docs", "docs/en"):
            text = (ROOT / directory / "01-setup.md").read_text()
            reentry = text.split('<a id="l01-new-terminal"></a>', 1)[1]
            with self.subTest(directory=directory):
                self.assertIn("portal" if directory.endswith("en") else "포털", reentry)
                self.assertIn("Do not recreate" if directory.endswith("en") else "다시 만들지 않습니다", reentry)
                self.assertNotIn("-m venv", reentry)
                self.assertNotIn("pip install", reentry)

    def test_evaluation_maps_agent_input_before_submission_and_preserves_failed_rows(self):
        for directory in ("docs", "docs/en"):
            text = (ROOT / directory / "08-evaluation.md").read_text()
            with self.subTest(directory=directory):
                self.assertLess(text.index("{{item.query}}"), text.index("`Submit`"))
                for field in ("ground_truth", "context", "case_id", "Partial/Failed", "12", "judge", "evaluation-12.jsonl"):
                    self.assertIn(field, text)
                self.assertNotIn("instruction_prompt_agent_lab.py --live", text)
                self.assertNotIn("instruction_evaluation.py --input", text)

    def test_extra_search_resources_and_routine_dispatch_are_not_default_actions(self):
        for directory in ("docs", "docs/en"):
            search = (ROOT / directory / "13-iq.md").read_text()
            hosted = (ROOT / directory / "14-hosted.md").read_text()
            routine = (ROOT / directory / "17-automation.md").read_text()
            with self.subTest(directory=directory):
                self.assertIn("approved" if directory.endswith("en") else "승인", search)
                self.assertIn("3072", search)
                self.assertIn("1536", search)
                self.assertIn('<a id="l12-azd"></a>', hosted)
                self.assertNotIn("azd deploy", hosted)
                self.assertIn("Create & start", routine)
                self.assertRegex(routine, r"(?i)browser|브라우저")
                self.assertIn("Cancel", routine)

    def test_concept_introductions_remain_compact_in_both_languages(self):
        for language in ("ko", "en"):
            chapters, _, _ = build_guide.load_content(language)
            for chapter in chapters:
                if chapter["track"] == "reference":
                    continue
                text = (ROOT / chapter["file"]).read_text()
                section = text.split("## " + LAB_HEADINGS[language][1], 1)[1]
                intro = re.split(r"^#{2,3} ", section, maxsplit=1, flags=re.M)[0]
                plain = unescape(re.sub(r"<[^>]+>", "", build_guide.markdown.markdown(intro)))
                with self.subTest(language=language, chapter=chapter["id"]):
                    if language == "ko":
                        self.assertLessEqual(len(plain), 500, "Keep the opening definition/method short.")
                    else:
                        self.assertLessEqual(len(plain.split()), 150, "Keep the opening definition/method short.")

    def test_blocks_target_portal_chat_and_do_not_create_environment_files(self):
        labels = build_guide.read_json("reader-labels.json")
        for language in ("ko", "en"):
            chapters, _, _ = build_guide.load_content(language)
            kinds = set()
            for chapter in chapters:
                if chapter["track"] == "reference":
                    continue
                text = (ROOT / chapter["file"]).read_text()
                kinds.update(re.findall(r"^```([a-z]+)\s*$", text, re.M))
            directory = ROOT / "docs" / ("en" if language == "en" else "")
            with self.subTest(language=language):
                self.assertLessEqual(kinds, set(labels[language]["js"]["code_labels"]))
                self.assertEqual(kinds, {"prompt"})
                self.assertNotEqual(
                    labels[language]["js"]["code_labels"]["prompt"],
                    labels[language]["js"]["code_labels"]["instructions"],
                )
                self.assertIn('id="l01-new-terminal"', (directory / "01-setup.md").read_text())
                self.assertIn("https://learn.microsoft.com/api/mcp", (directory / "07-toolbox.md").read_text())
                self.assertNotIn("workshop.py read-result --input", (directory / "06-actions.md").read_text())
                self.assertNotIn("workshop.py capstone --live", (directory / "11-capstone.md").read_text())

    def test_advanced_labs_explain_starting_paths_and_inputs_in_both_languages(self):
        for language in ("ko", "en"):
            chapters, _, _ = build_guide.load_content(language)
            for chapter in chapters:
                if chapter["track"] != "advanced":
                    continue
                text = (ROOT / chapter["file"]).read_text()
                with self.subTest(language=language, chapter=chapter["id"]):
                    prerequisites = "## " + LAB_HEADINGS[language][2]
                    self.assertLess(text.index(prerequisites), text.index("## " + LAB_HEADINGS[language][3]))
                    self.assertIn("**" + BRIEF_LABELS[language][1], text[:text.index(prerequisites)])
                    self.assertIn("portal" if language == "en" else "포털", text.lower())

    def test_advanced_result_reading_identifies_visible_fields_not_sdk_evidence(self):
        fields = {
            "13-iq.md": ("Search explorer", "Indexers", "3072", "1536"),
            "16-memory.md": ("scope", "TTL", "Setup incomplete", "Foundry User",
                             "Default time-to-live (seconds)", "Cancel", "CRUD"),
            "17-automation.md": ("Create & start", "Recurring", "One-time", "Identity", "Cancel"),
        }
        for directory in ("docs", "docs/en"):
            for filename, expected in fields.items():
                text = (ROOT / directory / filename).read_text()
                with self.subTest(directory=directory, filename=filename):
                    for field in expected:
                        self.assertIn(field, text)

    def test_all_bilingual_labs_start_with_format_action_and_expected_evidence(self):
        for language in ("ko", "en"):
            chapters, _, _ = build_guide.load_content(language)
            for chapter in chapters:
                if chapter["track"] == "reference":
                    continue
                text = (ROOT / chapter["file"]).read_text()
                with self.subTest(language=language, chapter=chapter["id"]):
                    self.assertEqual(text.count('class="lab-brief"'), 1)
                    brief = re.search(r'<div class="lab-brief" markdown="1">(.*?)</div>', text, re.S)
                    self.assertIsNotNone(brief)
                    self.assertLess(brief.start(), text.index("## " + LAB_HEADINGS[language][1]))
                    for label in BRIEF_LABELS[language]:
                        self.assertIn("**" + label, brief[1])

    def test_evaluation_chapter_uses_learner_results_not_embedded_measurements(self):
        for language in ("ko", "en"):
            directory = ROOT / "docs" / ("en" if language == "en" else "")
            text = (directory / "08-evaluation.md").read_text()
            with self.subTest(language=language):
                self.assertNotIn("validation/current", text)
                self.assertNotIn("instruction-reading-example", text)
                self.assertIn("evaluation-12.csv", text)
                self.assertIn("compound-request-no-tools", text)
                self.assertIn("contoso-compare-v1", text)
                self.assertIn("contoso-compare-v2", text)
                self.assertIn("90%", text)
                self.assertIn("safety/access", text)

    def test_reader_build_does_not_open_execution_records(self):
        original = Path.read_text

        def read(path, *args, **kwargs):
            if path.is_relative_to(ROOT) and path.relative_to(ROOT).parts[0] in {"validation", "results"}:
                raise AssertionError("A guide build must not read execution records.")
            return original(path, *args, **kwargs)

        with patch.object(Path, "read_text", read):
            for language in ("ko", "en"):
                chapters, sources, capabilities = build_guide.load_content(language)
                for chapter in chapters:
                    build_guide.source_body(chapter, chapters, capabilities, sources, language)

    def test_learner_text_keeps_capture_audits_in_maintenance_records(self):
        internal_markers = (
            "Playwright MCP", "Headless Chromium", 'class="provenance-note"',
            "portal-screenshots", "가이드 밖", "outside the guide", "outside this guide",
            "outside the reader", "제작자의", "author's execution",
            "이번 지침 수정", "This instruction update",
            "10/10 request trace IDs, only 7", "six bounded reconciliation sweeps",
        )
        labels = build_guide.read_json("reader-labels.json")
        for language in ("ko", "en"):
            chapters, sources, capabilities = build_guide.load_content(language)
            texts = {
                chapter["id"]: build_guide.source_body(chapter, chapters, capabilities, sources, language)
                for chapter in chapters
            }
            texts["reader-labels"] = json.dumps(labels[language], ensure_ascii=False)
            for name, text in texts.items():
                with self.subTest(language=language, source=name):
                    for marker in internal_markers:
                        self.assertNotIn(marker, text)
        replay = build_guide.read_json("replay.json")
        for language in ("ko", "en"):
            text = replay["notice"][language] + replay["chapters"][0][language]["narration"]
            self.assertNotIn("검증 보고서", text)
            self.assertNotIn("validation report", text)

    def test_learner_sources_have_no_historical_screen_blocks_or_images(self):
        for language in ("ko", "en"):
            chapters, _, _ = build_guide.load_content(language)
            for chapter in chapters:
                if "file" not in chapter:
                    continue
                text = (ROOT / chapter["file"]).read_text()
                with self.subTest(language=language, chapter=chapter["id"]):
                    self.assertNotIn("historical-screen", text)
                    for path in re.findall(r"!\[[^\]]*\]\(([^)]*assets/portal/[^)]*)\)", text):
                        self.assertIn("assets/portal/steps/", path)

    def test_official_links_render_without_internal_review_notes(self):
        for language in ("ko", "en"):
            _, sources, _ = build_guide.load_content(language)
            for source in sources["sources"]:
                source["basis"] = "INTERNAL_VERIFICATION_RECORD"
                source["note"] = "INTERNAL_SOURCE_REVIEW_NOTE"
            text = build_guide.sources_markdown(sources, language)
            with self.subTest(language=language):
                self.assertNotIn("INTERNAL_VERIFICATION_RECORD", text)
                self.assertNotIn("INTERNAL_SOURCE_REVIEW_NOTE", text)
                for source in sources["sources"]:
                    self.assertIn(f"[{source['title']}]({source['url']})", text)

    def test_all_active_labs_have_concepts_and_ordered_portal_actions(self):
        chapters = json.loads((ROOT / "content/chapters.json").read_text())
        labs = [chapter for chapter in chapters if chapter["track"] != "reference"]
        self.assertEqual(len(labs), 20)
        total = {"blocks": 0, "commands": 0}
        for chapter in labs:
            text = (ROOT / chapter["file"]).read_text()
            with self.subTest(lab=chapter["id"]):
                self.assertIn("## 개념과 실습 지도", text)
                for label in ("경험할 기능", "무엇이며 왜 중요한가요?", "어떻게 사용하나요?", "어디서 실행하나요?"):
                    self.assertIn("**" + label, text)
                coverage = command_coverage(text, chapter["file"])
                self.assertGreater(portal_coverage(text, chapter["file"])["steps"], 0)
                for key in total:
                    total[key] += coverage[key]
                for source in re.findall(r"\b(?:samples|scripts)/[\w.-]+\.py\b", text):
                    self.assertTrue((ROOT / source).is_file(), source)
        edition = json.loads((ROOT / "content/release.json").read_text())["languages"]["ko"]
        self.assertEqual(total, {"blocks": edition["shell_blocks"], "commands": edition["commands"]})

    def test_search_walkthrough_changes_mode_not_question(self):
        for directory in ("docs", "docs/en"):
            text = (ROOT / directory / "13-iq.md").read_text()
            with self.subTest(directory=directory):
                questions = re.findall(r"^```prompt\n(.*?)^```", text, re.M | re.S)
                self.assertEqual(len(questions), 1)
                self.assertIn("Search explorer", text)
                self.assertIn("keyword/vector/hybrid", text)
                self.assertNotIn("search_lab.py query", text)

    def test_tracing_uses_the_same_actual_request_and_does_not_invent_missing_spans(self):
        for directory in ("docs", "docs/en"):
            text = (ROOT / directory / "10-observability.md").read_text()
            with self.subTest(directory=directory):
                for marker in ("Traces", "span", "Application Insights", "Refresh", "403"):
                    self.assertIn(marker, text)
                self.assertIn("Do not invent" if directory.endswith("en") else "없는 span", text)
                self.assertNotRegex(text, r"^\|[^|]+\|\s*[\d,]+[~–][\d,]+\s*\|\s*[\d,]+ms\s*\|")

    def test_comments_and_continuations_do_not_inflate_command_count(self):
        text = (
            "```bash\n# comment\nKEY=value python sample.py \\\n"
            "  --flag value\n\npython second.py\n```\n"
            + explanation([
                "| 1. `sample.py` | Set the option. | Local output. |",
                "| 2. `second.py` | Run the second command. | No cloud calls. |",
            ])
        )
        self.assertEqual(command_coverage(text, "fixture"), {"blocks": 1, "commands": 2})

    def test_missing_explanation_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "adjacent command explanation"):
            command_coverage("```bash\npython sample.py\n```\n", "fixture")

    def test_one_row_cannot_explain_two_commands(self):
        text = "```bash\npython a.py\npython b.py\n```\n" + explanation([
            "| 1. both | Run both. | Output. |",
        ])
        with self.assertRaisesRegex(ValueError, "own ordered explanation"):
            command_coverage(text, "fixture")

    def test_duplicate_order_and_empty_explanations_are_rejected(self):
        for rows in (
            ["| 1. a | Run. | Output. |", "| 1. b | Run. | Output. |"],
            ["| 1. a | Run. | Output. |", "| 2. b |  | Output. |"],
        ):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                command_coverage("```bash\npython a.py\npython b.py\n```\n" + explanation(rows), "fixture")

    def test_powershell_command_is_explained(self):
        text = "```powershell\npy -3.13 -m venv .venv\n```\n" + explanation([
            "| 1. `py` | Select Python 3.13. | Create a local environment. |",
        ])
        self.assertEqual(command_coverage(text, "fixture")["commands"], 1)

    def test_dangling_continuation_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unfinished command"):
            command_coverage("```bash\npython sample.py \\\n```\n", "fixture")


if __name__ == "__main__":
    unittest.main()
