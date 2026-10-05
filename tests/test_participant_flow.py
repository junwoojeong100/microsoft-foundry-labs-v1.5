import ast
from html import unescape
import json
from pathlib import Path
import re
import shlex
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_guide


def python_blocks(text):
    return re.findall(r"^```python\n(.*?)^```[^\S\n]*$", text, re.M | re.S)


def shell_commands(text):
    return [
        shlex.split(line)
        for body in re.findall(r"^```bash\n(.*?)^```[^\S\n]*$", text, re.M | re.S)
        for line in body.replace("\\\n", " ").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


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
        forbidden = r"(?i)강사|관리자|\b(?:instructors?|administrators?|deployment operators?)\b"
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
                plain = unescape(re.sub(r"<[^>]+>", "", build_guide.markdown.markdown(text)))
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

    def test_owned_setup_precedes_execution_and_connects_logs_before_agents(self):
        for language in ("ko", "en"):
            text = source(language, "01-setup.md")
            commands = shell_commands(text)
            live_steps = [
                command[command.index("scripts/azure_environment.py") + 1]
                for command in commands
                if "scripts/azure_environment.py" in command and "--live" in command
            ]
            with self.subTest(language=language):
                self.assertEqual(live_steps, ["create", "foundation", "roles", "monitoring"])
                creation = next(command for command in commands
                                if "scripts/azure_environment.py" in command and "create" in command and "--live" in command)
                for option in ("--subscription", "--location", "--cost-authorization"):
                    self.assertIn(option, creation)
                self.assertIn("roleAssignments/write", text)
                self.assertIn("Contributor", text)
                self.assertIn("Log Analytics Reader", text)
                self.assertIn("results/azure-environment.json", text)

    def test_tool_preparation_has_install_checks_and_a_matching_editor_environment(self):
        for language in ("ko", "en"):
            text = source(language, "01-setup.md")
            with self.subTest(language=language):
                anchors = ("l01-python", "l01-azure-cli", "l01-vscode", "l01-local", "l01-interpreter")
                positions = [text.index(f'<a id="{anchor}"></a>') for anchor in anchors]
                self.assertEqual(positions, sorted(positions))
                for marker in (
                    "Add python.exe to PATH", "pip", "Python launcher",
                    "py -3.13 --version", "python3.13 --version",
                    "sudo apt install python3.13 python3.13-venv",
                    "Install Certificates.command", "Microsoft Installer (MSI)", "Specific version",
                    "brew install azure-cli", "sudo apt install azure-cli", "az version",
                    "User Installer", "ms-python.python", "Python: Select Interpreter",
                    "Enter interpreter path", ".venv/bin/python", r".venv\Scripts\python.exe",
                ):
                    self.assertIn(marker, text)
                self.assertLess(text.index("az version"), text.index("az login"))
                self.assertLess(text.index("py -3.13 -m venv"), positions[-1])
                self.assertIn("python3.13 samples/workshop.py doctor", text)
                self.assertNotIn("python3 samples/workshop.py doctor", text)
                self.assertNotRegex(text, r"curl\b[^\n]*\|\s*(?:sudo\s+)?(?:ba)?sh\b")

    def test_self_created_search_and_evaluation_inputs_are_explicit(self):
        for language in ("ko", "en"):
            search = source(language, "13-iq.md")
            commands = shell_commands(search)
            create_at = next(index for index, command in enumerate(commands)
                             if "scripts/azure_environment.py" in command and "search" in command and "--live" in command)
            initialize_at = next(index for index, command in enumerate(commands)
                                 if "samples/search_lab.py" in command and "initialize" in command and "--live" in command)
            evaluation = source(language, "08-evaluation.md")
            with self.subTest(language=language):
                self.assertLess(create_at, initialize_at)
                self.assertIn("FOUNDRY_JUDGE_DEPLOYMENT_NAME=contoso-judge", evaluation)
                self.assertIn("results/azure-environment.json", evaluation)
                self.assertIn("instruction_prompt_agent_lab.py --live", evaluation)
                self.assertIn("instruction_evaluation.py --input", evaluation)
                self.assertIn("90%", evaluation)
                self.assertIn("safety/access", evaluation)

    def test_every_python_example_compiles_without_executing_live_calls(self):
        for language in ("ko", "en"):
            chapters, _, _ = build_guide.load_content(language)
            for chapter in chapters:
                if "file" not in chapter:
                    continue
                for index, block in enumerate(python_blocks((ROOT / chapter["file"]).read_text(encoding="utf-8"))):
                    with self.subTest(language=language, chapter=chapter["id"], block=index):
                        compile(block, chapter["file"], "exec")

    def test_purchase_function_example_matches_the_actual_business_logic(self):
        implementation = ast.parse((ROOT / "samples/workshop.py").read_text(encoding="utf-8"))
        actual = next(node for node in implementation.body
                      if isinstance(node, ast.FunctionDef) and node.name == "prepare_purchase_request")
        expected = ast.dump(ast.Module(body=actual.body, type_ignores=[]))
        for language in ("ko", "en"):
            examples = [
                node for block in python_blocks(source(language, "06-actions.md"))
                for node in ast.parse(block).body
                if isinstance(node, ast.FunctionDef) and node.name == actual.name
            ]
            with self.subTest(language=language):
                self.assertEqual(len(examples), 1)
                self.assertEqual(ast.dump(ast.Module(body=examples[0].body, type_ignores=[])), expected)

    def test_first_request_has_one_matching_budget_and_no_portal_python_execution_claim(self):
        for language in ("ko", "en"):
            text = source(language, "03-responses.md")
            calls = [
                node for block in python_blocks(text) for node in ast.walk(ast.parse(block))
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and ast.unparse(node.func) == "client.responses.create"
            ]
            with self.subTest(language=language):
                self.assertEqual(len(calls), 1)
                options = {keyword.arg: keyword.value for keyword in calls[0].keywords}
                self.assertEqual(ast.literal_eval(options["max_output_tokens"]), 512)
                self.assertIs(ast.literal_eval(options["store"]), False)
                self.assertIn("512", text)
                self.assertIn("first_response.py --live", text)
                self.assertNotIn("Send runs", text)
                self.assertNotIn("Send**가 Python", text)

    def test_core_and_hosted_authorization_and_memory_scope_are_not_conflated(self):
        for language in ("ko", "en"):
            safety = source(language, "09-safety.md")
            memory = source(language, "16-memory.md")
            with self.subTest(language=language):
                self.assertIn("L12 Hosted", safety)
                self.assertIn("request_contract.py", safety)
                self.assertNotIn("used by L06 has this shape", safety)
                self.assertNotIn("L06에서 호출하는 실제 계약 검사", safety)
                self.assertIn("scope", memory)
                self.assertIn("API caller", memory)


if __name__ == "__main__":
    unittest.main()
