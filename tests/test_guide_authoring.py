import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_guide import command_coverage


def explanation(rows):
    return (
        '<div class="command-explanation" markdown="1">\n\n**명령 해설**\n\n'
        "| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |\n"
        "| --- | --- | --- |\n"
        + "\n".join(rows)
        + "\n\n</div>\n"
    )


class GuideAuthoringTests(unittest.TestCase):
    def test_all_25_labs_have_concepts_and_per_command_explanations(self):
        chapters = json.loads((ROOT / "content/chapters.json").read_text())
        labs = [chapter for chapter in chapters if chapter["track"] != "reference"]
        self.assertEqual(len(labs), 25)
        commands = 0
        for chapter in labs:
            text = (ROOT / chapter["file"]).read_text()
            with self.subTest(lab=chapter["id"]):
                self.assertIn("## 개념과 실습 지도", text)
                for label in ("경험할 기능", "무엇이며 왜 중요한가요?", "어떻게 사용하나요?", "어디서 실행하나요?"):
                    self.assertIn("**" + label, text)
                commands += command_coverage(text, chapter["file"])["commands"]
                for source in re.findall(r"\b(?:samples|scripts)/[\w.-]+\.py\b", text):
                    self.assertTrue((ROOT / source).is_file(), source)
        self.assertGreaterEqual(commands, 120)

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
