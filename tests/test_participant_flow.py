from html import unescape
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_guide
from check_guide import portal_coverage


def source(language, filename):
    folder = ROOT / "docs" / ("en" if language == "en" else "")
    return (folder / filename).read_text(encoding="utf-8")


class ParticipantFlowTests(unittest.TestCase):
    def test_current_korean_sources_use_agent_terminology(self):
        legacy = "\uB3C4\uC6B0\uBBF8"
        chapters, _, _ = build_guide.load_content("ko")
        sources = [ROOT / chapter["file"] for chapter in chapters if "file" in chapter]
        sources += [
            ROOT / path for path in (
                "README.ko.md", "content/chapters.json", "content/reader-labels.json",
                "content/replay.json", "samples/README.ko.md", "docs/11-capstone.md",
                "data/prompts/agent-v1.txt", "data/prompts/agent-v2.txt",
            )
        ]
        for path in sources:
            with self.subTest(source=path.relative_to(ROOT)):
                self.assertNotIn(legacy, path.read_text(encoding="utf-8"))

    def test_learner_copy_and_navigation_do_not_split_participant_personas(self):
        forbidden = r"(?i)강사용|관리자용|강사 전용|\b(?:instructor|administrator|deployment operator)(?:-only| route| path)\b"
        for language in ("ko", "en"):
            chapters, _, _ = build_guide.load_content(language)
            checklist = next(chapter for chapter in chapters if chapter["id"] == "instructor")
            self.assertEqual(checklist["file"], f"docs/{'en/' if language == 'en' else ''}instructor.md")
            texts = {
                chapter["id"]: (ROOT / chapter["file"]).read_text(encoding="utf-8")
                for chapter in chapters if "file" in chapter
            }
            texts["navigation"] = json.dumps(
                [{"title": chapter["title"], "summary": chapter["summary"], "learning": chapter["learning"]}
                 for chapter in chapters],
                ensure_ascii=False,
            )
            texts["README"] = (ROOT / build_guide.RELEASE["languages"][language]["readme"]).read_text(encoding="utf-8")
            replay = build_guide.read_json("replay.json")
            texts.update({f"replay:{chapter['id']}": chapter[language]["narration"] for chapter in replay["chapters"]})
            for name, text in texts.items():
                plain = unescape(re.sub(r"<[^>]+>", "", build_guide.markdown.markdown(
                    text, extensions=["tables", "fenced_code", "md_in_html"],
                )))
                for role in ("User Access Administrator", "Role Based Access Control Administrator"):
                    plain = plain.replace(role, "")
                with self.subTest(language=language, source=name):
                    self.assertNotRegex(plain, forbidden)
                    self.assertNotIn('class="operator-only"', text)

    def test_input_destination_inventory_matches_both_source_editions(self):
        for language in ("ko", "en"):
            chapters, _, _ = build_guide.load_content(language)
            text = "\n".join(
                (ROOT / chapter["file"]).read_text(encoding="utf-8")
                for chapter in chapters if chapter["track"] != "reference"
            )
            edition = build_guide.RELEASE["languages"][language]
            with self.subTest(language=language):
                self.assertEqual(len(re.findall(r"^```prompt$", text, re.M)), edition["prompt_blocks"])
                self.assertEqual(len(re.findall(r"^```env$", text, re.M)), edition["settings_blocks"])
                self.assertEqual(edition["shell_blocks"], 0)
                self.assertEqual(edition["commands"], 0)
                self.assertEqual(edition["settings_blocks"], 0)
            for chapter in chapters:
                if chapter["track"] != "reference":
                    with self.subTest(language=language, chapter=chapter["id"]):
                        coverage = portal_coverage(
                            (ROOT / chapter["file"]).read_text(), chapter["file"], language,
                        )
                        self.assertGreater(coverage["steps"], 0)

    def test_owned_setup_precedes_execution_and_connects_logs_before_agents(self):
        for language in ("ko", "en"):
            text = source(language, "01-setup.md")
            with self.subTest(language=language):
                for marker in (
                    "https://portal.azure.com/", "https://ai.azure.com/", "Resource groups",
                    "Microsoft Foundry resource (Recommended)", "Advanced options",
                    "validationRun", "View my access", "Log Analytics workspaces",
                    "Project Managed Identity", "Auth Type", "Connect",
                ):
                    self.assertIn(marker, text)
                self.assertLess(text.index("law-contoso-portal-"), text.index("appi-contoso-portal-"))
                self.assertIn("roleAssignments/write", text)
                self.assertIn("Contributor", text)
                self.assertIn("Log Analytics Reader", text)
                self.assertNotIn("scripts/azure_environment.py", text)

    def test_old_setup_bookmarks_lead_to_portal_resumption_not_installation(self):
        for language in ("ko", "en"):
            text = source(language, "01-setup.md")
            with self.subTest(language=language):
                anchors = ("l01-python", "l01-azure-cli", "l01-vscode", "l01-local", "l01-interpreter")
                positions = [text.index(f'<a id="{anchor}"></a>') for anchor in anchors]
                self.assertEqual(positions, sorted(positions))
                reentry = text.split('<a id="l01-new-terminal"></a>', 1)[1]
                self.assertIn("portal" if language == "en" else "포털", reentry)
                self.assertNotRegex(text, r"^```(?:bash|powershell|python|env)$")
                self.assertNotRegex(text, r"az login|pip install|python -m venv|brew install")

    def test_self_created_search_and_evaluation_inputs_are_explicit(self):
        for language in ("ko", "en"):
            search = source(language, "13-iq.md")
            evaluation = source(language, "08-evaluation.md")
            with self.subTest(language=language):
                for marker in ("Search explorer", "1536", "3072"):
                    self.assertIn(marker, search)
                for marker in (
                    "contoso-judge", "evaluation-12.csv", "{{item.query}}", "ground_truth",
                    "review-checklist.csv", "Partial/Failed", "compound-request-no-tools",
                ):
                    self.assertIn(marker, evaluation)
                self.assertIn("90%", evaluation)
                self.assertIn("safety/access", evaluation)

    def test_active_labs_do_not_execute_code_or_local_purchase_functions(self):
        for language in ("ko", "en"):
            chapters, _, _ = build_guide.load_content(language)
            for chapter in chapters:
                if "file" not in chapter:
                    continue
                text = (ROOT / chapter["file"]).read_text(encoding="utf-8")
                with self.subTest(language=language, chapter=chapter["id"]):
                    self.assertNotRegex(text, r"(?m)^```(?:bash|powershell|python|env|javascript|yaml)$")
                    self.assertNotRegex(text, r"python (?:samples|scripts)/|azd deploy|az login")

    def test_purchase_boundary_is_explicit_instead_of_a_fabricated_execution(self):
        for language in ("ko", "en"):
            text = source(language, "06-actions.md")
            with self.subTest(language=language):
                for marker in ("Function", "order_submitted", "draft_requires_human_approval", "2,900,000"):
                    self.assertIn(marker, text)
                self.assertNotIn("workshop.py capstone --live", text)

    def test_first_request_removes_unapproved_tools_and_sets_a_visible_budget(self):
        for language in ("ko", "en"):
            text = source(language, "03-responses.md")
            with self.subTest(language=language):
                for marker in ("512", "Max Completion Tokens", "Web search", "Remove", "Send"):
                    self.assertIn(marker, text)
                self.assertEqual(len(re.findall(r"^```prompt$", text, re.M)), 1)
                self.assertNotIn("first_response.py --live", text)
                self.assertNotIn("client.responses.create", text)

    def test_memory_scope_is_not_replaced_by_conversation_history(self):
        for language in ("ko", "en"):
            memory = source(language, "16-memory.md")
            with self.subTest(language=language):
                for marker in ("scope", "TTL", "CRUD", "Setup incomplete", "Resolve", "Cancel",
                               "Chat completions model", "Embedding model"):
                    self.assertIn(marker, memory)
                self.assertIn("Do not select Resolve" if language == "en" else "Resolve를 누르거나", memory)
                self.assertNotIn("memory_lab.py", memory)


if __name__ == "__main__":
    unittest.main()
