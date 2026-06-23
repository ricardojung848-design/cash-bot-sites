from pathlib import Path
import json
import time

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"

PREDICTIVE_STATE_FILE = CONFIG_DIR / "predictive_state.json"
PRIORITY_FILE = CONFIG_DIR / "priority_plan.json"
FIX_SUGGESTIONS_FILE = CONFIG_DIR / "fix_suggestions.json"
OPTIMIZER_PLAN_FILE = CONFIG_DIR / "optimizer_plan.json"
LEARNING_FILE = CONFIG_DIR / "learning_state.json"
PLANNER_FILE = CONFIG_DIR / "planner_plan.json"


class DoctorState:
    def __init__(self):
        self._ensure_files()

    def _ensure_files(self):
        defaults = {
            PREDICTIVE_STATE_FILE: {"history": [], "last_score": 0.0, "last_update": None},
            PRIORITY_FILE: {"last_update": None, "tasks": []},
            FIX_SUGGESTIONS_FILE: {"last_update": None, "suggestions": []},
            OPTIMIZER_PLAN_FILE: {"last_update": None, "modules": []},
            LEARNING_FILE: {"last_update": None, "action_stats": {}, "notes": []},
            PLANNER_FILE: {"last_update": None, "roadmap": []},
        }
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        for path, default in defaults.items():
            if not path.exists():
                path.write_text(json.dumps(default, indent=2), encoding="utf-8")

    def _load(self, path: Path) -> dict:
        try:
            raw = path.read_text(encoding="utf-8")
            return json.loads(raw) if raw.strip() else {}
        except Exception:
            return {}

    def _save(self, path: Path, data: dict):
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load_all(self) -> dict:
        return {
            "priority": self._load(PRIORITY_FILE),
            "fixes": self._load(FIX_SUGGESTIONS_FILE),
            "optimizer": self._load(OPTIMIZER_PLAN_FILE),
            "planner": self._load(PLANNER_FILE),
        }

    def update_planner(self, roadmap: list):
        data = {
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S"),
            "roadmap": roadmap,
        }
        self._save(PLANNER_FILE, data)
