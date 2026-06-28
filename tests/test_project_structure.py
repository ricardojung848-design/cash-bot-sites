import json
import unittest
from pathlib import Path


class TestProjectStructure(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent

    def test_required_root_files_exist(self):
        required = [
            "README.md",
            "requirements.txt",
            "monetization_config.json",
            "start-dashboard.bat",
            "dashboard/backend/main.py",
            "dashboard/frontend/pages/index.html",
        ]
        for rel in required:
            self.assertTrue((self.root / rel).exists(), f"Fehlt: {rel}")

    def test_cash_bot_docs_exist(self):
        docs_dir = self.root / "Cash_Bot" / "docs"
        self.assertTrue(docs_dir.is_dir())
        self.assertTrue((docs_dir / "README.md").exists())
        self.assertTrue((docs_dir / "README_MODULES.md").exists())

    def test_config_files_are_initialized(self):
        cfg_dir = self.root / "Cash_Bot" / "config"
        with open(cfg_dir / "system_map.json", "r", encoding="utf-8") as f:
            system_map = json.load(f)
        with open(cfg_dir / "doctor_docs.json", "r", encoding="utf-8") as f:
            doctor_docs = json.load(f)

        self.assertGreater(len(system_map.get("modules", [])), 0)
        self.assertGreater(len(system_map.get("files", [])), 0)
        self.assertGreater(len(system_map.get("relations", [])), 0)
        self.assertTrue(bool(doctor_docs.get("summary", "").strip()))


if __name__ == "__main__":
    unittest.main()
