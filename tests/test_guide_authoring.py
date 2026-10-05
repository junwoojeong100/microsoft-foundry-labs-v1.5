from copy import deepcopy
from html import escape, unescape
import json
from pathlib import Path
import re
import shlex
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_guide
from check_guide import BRIEF_LABELS, LAB_HEADINGS, command_coverage


def explanation(rows):
    return (
        '<div class="command-explanation" markdown="1">\n\n**명령 해설**\n\n'
        "| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |\n"
        "| --- | --- | --- |\n"
        + "\n".join(rows)
        + "\n\n</div>\n"
    )


class GuideAuthoringTests(unittest.TestCase):
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

    def test_block_destinations_and_local_reentry_are_explicit(self):
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
                self.assertLessEqual({"prompt", "env", "output"}, kinds)
                self.assertNotEqual(
                    labels[language]["js"]["code_labels"]["prompt"],
                    labels[language]["js"]["code_labels"]["instructions"],
                )
                self.assertIn('id="l01-new-terminal"', (directory / "01-setup.md").read_text())
                self.assertIn("#l01-new-terminal", (directory / "07-toolbox.md").read_text())
                self.assertIn("workshop.py read-result --input", (directory / "06-actions.md").read_text())
                self.assertNotIn("workshop.py capstone --live", (directory / "11-capstone.md").read_text())

    def test_advanced_labs_explain_starting_paths_and_inputs_in_both_languages(self):
        for language, heading in (("ko", "### 먼저 경로 정하기"), ("en", "### Choose your starting path")):
            chapters, _, _ = build_guide.load_content(language)
            for chapter in chapters:
                if chapter["track"] != "advanced":
                    continue
                text = (ROOT / chapter["file"]).read_text()
                with self.subTest(language=language, chapter=chapter["id"]):
                    self.assertIn(heading, text)
                    self.assertLess(text.index(heading), text.index("## " + LAB_HEADINGS[language][3]))
                    self.assertTrue("results/" in text or "practice/" in text)

    def test_advanced_result_reading_identifies_real_output_fields(self):
        fields = {
            "13-iq.md": ("FOUNDRY_EMBEDDING_ENDPOINT", "knowledge_source", "CONTOSO-PROC-2026-09-s3", "CONTOSO-EXP-2026-09-s1"),
            "14-hosted.md": ("results/search.json", "results/azure-environment.json", "/readiness", "order_submitted=false"),
            "15-collaboration.md": ("paths.group-chat.stages", "paths.handoff.stages", "handoff_calls", "final_messages"),
            "16-memory.md": ("memory_created", "memory_search", "scope_label=scope_a", "scope_label=scope_b", "memory_id"),
            "17-automation.md": ("trigger_at", "marker", "enabled=false", ".dispatch.json"),
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
                self.assertIn("results/azure-environment.json", text)
                self.assertIn("compound-request-no-tools", text)
                self.assertIn("instruction_prompt_agent_lab.py --live", text)
                self.assertIn("instruction_evaluation.py --input", text)
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
            "과거 검증", "공개 검증", "이번 지침 수정", "This instruction update",
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

    def test_screen_examples_keep_learner_context_and_completion_criteria(self):
        expected = {
            "ko": {
                "00-start.md": ("권한, 지역, 업데이트", "성공 기준", "자신의 프로젝트"),
                "03-responses.md": ("모델 응답 예시", "출력 한도 설정 예시"),
                "04-agent.md": ("구성 예시", "L04에서는 지시문만"),
                "13-iq.md": ("Search 연결 설정 예시", "Entra"),
                "16-memory.md": ("Memory store 설정 예시", "사용자별 검색", "승인된 삭제"),
            },
            "en": {
                "00-start.md": ("permissions, region, and updates", "Success criteria", "your own project"),
                "03-responses.md": ("Model response example", "Output-limit setting example"),
                "04-agent.md": ("configuration example", "Save only the instructions in L04"),
                "13-iq.md": ("Knowledge-list example", "Project Managed Identity"),
                "16-memory.md": ("Stored-item example", "user-specific searches", "approved deletion"),
            },
        }
        for language, files in expected.items():
            directory = ROOT / "docs" / ("en" if language == "en" else "")
            for filename, markers in files.items():
                text = (directory / filename).read_text()
                with self.subTest(language=language, source=filename):
                    for marker in markers:
                        self.assertIn(marker, text)

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

    def test_all_active_labs_have_concepts_and_per_command_explanations(self):
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
                for key in total:
                    total[key] += coverage[key]
                for source in re.findall(r"\b(?:samples|scripts)/[\w.-]+\.py\b", text):
                    self.assertTrue((ROOT / source).is_file(), source)
        edition = json.loads((ROOT / "content/release.json").read_text())["languages"]["ko"]
        self.assertEqual(total, {"blocks": edition["shell_blocks"], "commands": edition["commands"]})

    def test_search_walkthrough_changes_mode_not_question(self):
        for directory in ("docs", "docs/en"):
            text = (ROOT / directory / "13-iq.md").read_text()
            commands = [
                shlex.split(line) for line in text.splitlines()
                if line.startswith("python samples/search_lab.py query ")
            ]
            with self.subTest(directory=directory):
                self.assertEqual(len(commands), 3)
                self.assertEqual({c[c.index("--mode") + 1] for c in commands}, {"keyword", "hybrid", "iq"})
                self.assertEqual(len({c[c.index("--query") + 1] for c in commands}), 1)
                self.assertTrue(all("--live" in command for command in commands))

    def test_trace_timing_example_uses_intervals_without_double_counting(self):
        for directory in ("docs", "docs/en"):
            text = (ROOT / directory / "10-observability.md").read_text()
            rows = re.findall(r"^\|[^|]+\|\s*([\d,]+)[~–]([\d,]+)\s*\|\s*([\d,]+)ms\s*\|", text, re.M)
            with self.subTest(directory=directory):
                self.assertEqual(len(rows), 4)
                intervals = [tuple(int(value.replace(",", "")) for value in row) for row in rows]
                for start, end, duration in intervals:
                    self.assertEqual(end - start, duration)
                parent = intervals[0][2]
                children = sum(row[2] for row in intervals[1:])
                self.assertIn(f"{children:,}ms", text)
                self.assertIn(f"{parent - children}ms", text)
                self.assertLessEqual(children, parent)
                for previous, following in zip(intervals[1:], intervals[2:]):
                    self.assertLessEqual(previous[1], following[0])

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
