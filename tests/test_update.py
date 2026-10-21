import importlib.util
from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("update", Path(__file__).resolve().parents[1] / "scripts/update.py")
update = importlib.util.module_from_spec(spec)
spec.loader.exec_module(update)

class SummaryTests(unittest.TestCase):
    def test_classification_and_no_credentials(self):
        result = update.summarize({"accounts": [
            {"username": "private@example.test", "password": "SECRET_TEST_VALUE", "status": True},
            {"status": 0}, {"status": "1"}, {"status": False, "last_check_success": True}]})
        self.assertEqual(result, {"count": 4, "normal": 2, "abnormal": 1, "unknown": 1})
        self.assertNotIn("SECRET_TEST_VALUE", json.dumps(result))
        self.assertNotIn("username", result)

    def test_rejects_bad_payload(self):
        for payload in ({}, {"accounts": []}, {"accounts": [None]}, [], {"accounts": "bad"}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                update.summarize(payload)

    def test_invalid_template_keeps_old_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.template.md").write_text("{{UNKNOWN}}")
            (root / "README.md").write_text("previous")
            with patch.object(update, "ROOT", root), self.assertRaises(ValueError):
                update.publish([])
            self.assertEqual((root / "README.md").read_text(), "previous")
            self.assertFalse((root / "data/latest.json").exists())

if __name__ == "__main__":
    unittest.main()
