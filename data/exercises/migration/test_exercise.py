"""Local wire-shape practice; existing Azure object IDs are not migrated."""

import json
import unittest

from exercise import continuation


class MigrationPractice(unittest.TestCase):
    def setUp(self):
        self.call = {"type": "function_call", "id": "fc_item_demo", "call_id": "call_demo_1",
                     "name": "get_stock", "arguments": '{"sku":"NB-14"}'}
        self.result = {"sku": "NB-14", "stock": 8}
        self.request = continuation("conv_new_demo", self.call, self.result)

    def test_conversation_is_preserved(self):
        self.assertEqual(self.request["conversation"], "conv_new_demo")

    def test_call_id_not_output_item_id(self):
        self.assertEqual(self.request["input"][0]["call_id"], "call_demo_1")

    def test_tool_output_is_json_string(self):
        self.assertIsInstance(self.request["input"][0]["output"], str)
        self.assertEqual(json.loads(self.request["input"][0]["output"]), self.result)

    def test_output_type_and_count(self):
        self.assertEqual(len(self.request["input"]), 1)
        self.assertEqual(self.request["input"][0]["type"], "function_call_output")


if __name__ == "__main__":
    unittest.main()
