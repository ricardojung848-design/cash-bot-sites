import time
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # .../Cash_Bot
CONFIG_DIR = BASE_DIR / "config"
LEARNING_FILE = CONFIG_DIR / "learning_state.json"
DOCTOR_STATE_FILE = CONFIG_DIR / "doctor_state.json"


def _safe_load_json(path: Path, default):
    try:
        if not path.exists():
            return default
        raw = path.read_text(encoding="utf-8")
        if not raw.strip():
            return default
        return json.loads(raw)
    except Exception:
        return default


def _safe_save_json(path: Path, data: dict):
    try:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass


class LearningEngine:
    """
    Sehr einfache Learning-Engine:
    - zählt, wie oft bestimmte Aktionen vorkommen
    - speichert Muster über Zeit
    """

    def __init__(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if not LEARNING_FILE.exists():
            _safe_save_json(
                LEARNING_FILE,
                {
                    "last_update": None,
                    "action_stats": {},
                    "notes": [],
                },
            )

    def _load_learning(self) -> dict:
        return _safe_load_json(
            LEARNING_FILE,
            {
                "last_update": None,
                "action_stats": {},
                "notes": [],
            },
        )

    def _save_learning(self, data: dict):
        _safe_save_json(LEARNING_FILE, data)

    def _load_doctor_state(self) -> dict:
        return _safe_load_json(
            DOCTOR_STATE_FILE,
            {
                "status": "unknown",
                "last_logs": [],
                "last_commands": [],
            },
        )

    def update_from_logs(self):
        learning = self._load_learning()
        stats = learning.get("action_stats", {})
        ds = self._load_doctor_state()
        logs = ds.get("last_logs", [])

        for line in logs:
            if "Systemprüfung" in line:
                stats["check_system"] = stats.get("check_system", 0) + 1
            if "Loganalyse" in line:
                stats["analyze_logs"] = stats.get("analyze_logs", 0) + 1
            if "Self-Healing" in line:
                stats["self_heal"] = stats.get("self_heal", 0) + 1
            if "Modul-Builder" in line:
                stats["module_builder"] = stats.get("module_builder", 0) + 1

        learning["action_stats"] = stats
        learning["last_update"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self._save_learning(learning)
        return learning

    def add_note(self, note: str):
        learning = self._load_learning()
        notes = learning.get("notes", [])
        notes.append(
            {
                "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                "note": note,
            }
        )
        if len(notes) > 100:
            notes = notes[-100:]
        learning["notes"] = notes
        learning["last_update"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self._save_learning(learning)
        return learning
