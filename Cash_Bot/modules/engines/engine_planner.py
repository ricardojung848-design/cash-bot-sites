import time
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # .../Cash_Bot
CONFIG_DIR = BASE_DIR / "config"
PLANNER_FILE = CONFIG_DIR / "planner_plan.json"
PRIORITY_FILE = CONFIG_DIR / "priority_plan.json"
OPTIMIZER_PLAN_FILE = CONFIG_DIR / "optimizer_plan.json"
FIX_SUGGESTIONS_FILE = CONFIG_DIR / "fix_suggestions.json"


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


class PlannerEngine:
    """
    Baut eine einfache Roadmap aus:
    - Prioritäten
    - Optimierungsdaten
    - Fix-Vorschlägen
    """

    def __init__(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if not PLANNER_FILE.exists():
            _safe_save_json(
                PLANNER_FILE,
                {
                    "last_update": None,
                    "roadmap": [],
                },
            )

    def _load_priority(self) -> dict:
        return _safe_load_json(
            PRIORITY_FILE,
            {
                "last_update": None,
                "tasks": [],
            },
        )

    def _load_optimizer(self) -> dict:
        return _safe_load_json(
            OPTIMIZER_PLAN_FILE,
            {
                "last_update": None,
                "modules": [],
            },
        )

    def _load_fixes(self) -> dict:
        return _safe_load_json(
            FIX_SUGGESTIONS_FILE,
            {
                "last_update": None,
                "suggestions": [],
            },
        )

    def _load_planner(self) -> dict:
        return _safe_load_json(
            PLANNER_FILE,
            {
                "last_update": None,
                "roadmap": [],
            },
        )

    def _save_planner(self, data: dict):
        _safe_save_json(PLANNER_FILE, data)

    def build_roadmap(self) -> list:
        priority = self._load_priority()
        optimizer = self._load_optimizer()
        fixes = self._load_fixes()

        roadmap = []

        for t in priority.get("tasks", []):
            roadmap.append(
                {
                    "type": "priority_task",
                    "name": t.get("name"),
                    "reason": t.get("reason"),
                }
            )

        for m in optimizer.get("modules", [])[:5]:
            roadmap.append(
                {
                    "type": "module_optimize",
                    "name": m.get("name"),
                    "info": f"Komplexität: {m.get('complexity')}, Zeilen: {m.get('lines')}",
                }
            )

        for s in fixes.get("suggestions", [])[:5]:
            roadmap.append(
                {
                    "type": "fix_suggestion",
                    "file": s.get("file"),
                    "keyword": s.get("keyword"),
                    "hint": s.get("hint"),
                }
            )

        return roadmap

    def update(self) -> list:
        roadmap = self.build_roadmap()
        data = {
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S"),
            "roadmap": roadmap,
        }
        self._save_planner(data)
        return roadmap
