"""flatness.definition：定義檔讀取與驗證（3.7.1、DEF-02）。"""

import json
import tempfile
import unittest
from pathlib import Path

from helpers import NET, ROOT

from flatness import bootp, definition


class DefinitionTest(unittest.TestCase):
    def setUp(self):
        self.sample = json.loads((ROOT / "installer" / "dl-en1.json").read_text(encoding="utf-8"))

    def test_schema_and_rules_accept_installer_sample(self):
        self.assertEqual(definition.validate(self.sample, NET), [])

    def test_rule_errors_reported_with_location(self):
        self.sample["dl_en1"][0]["probes"][0]["id"] = 9
        errors = definition.validate(self.sample, NET)
        self.assertIn("dl_en1[0].probes[0].id", [w for w, _ in errors])

    def test_zero_devices_valid_nine_invalid(self):  # DEF-01：0～8 台（DSC-18 可刪除最後一台）
        self.assertEqual(definition.validate({"version": 1, "dl_en1": []}, NET), [])
        dev = self.sample["dl_en1"][0]
        nine = {"version": 1, "dl_en1": [dict(dev) for _ in range(9)]}
        self.assertTrue(definition.validate(nine, NET))

    def test_load_missing_file_is_empty(self):
        self.assertEqual(definition.load_definition(Path("/nonexistent/dl-en1.json")), {"version": 1, "dl_en1": []})

    def test_load_syntax_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "x.json")
            path.write_text('{"version": 1,\n "dl_en1": [}', encoding="utf-8")
            with self.assertRaises(bootp.DefinitionError) as ctx:
                definition.load_definition(path)
            self.assertIn("第 2 行", ctx.exception.errors[0][0])

    def test_dumps_round_trip(self):
        self.assertEqual(json.loads(definition.dumps(self.sample)), self.sample)


if __name__ == "__main__":
    unittest.main()
