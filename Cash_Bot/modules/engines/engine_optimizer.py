import time
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # .../Cash_Bot
CONFIG_DIR = BASE_DIR / "config"
OPTIMIZER_PLAN_FILE = CONFIG_DIR / "optimizer_plan.json"
MODULES_DIR = BASE_DIR / "modules"


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


class OptimizerEngine:
    """
    Erzeugt eine einfache Optimierungs-Übersicht:
    - Welche Module existieren?
    - Welche sind groß / komplex?
    """

    def __init__(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if not OPTIMIZER_PLAN_FILE.exists():
            _safe_save_json(
                OPTIMIZER_PLAN_FILE,
                {
                    "last_update": None,
                    "modules": [],
                },
            )

    def _load_plan(self) -> dict:
        return _safe_load_json(
            OPTIMIZER_PLAN_FILE,
            {
                "last_update": None,
                "modules": [],
            },
        )

    def _save_plan(self, data: dict):
        _safe_save_json(OPTIMIZER_PLAN_FILE, data)

    def analyze_modules(self) -> list:
        modules_info = []
        if not MODULES_DIR.exists():
            return modules_info

        for f in MODULES_DIR.iterdir():
            if f.is_file() and f.suffix == ".py":
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    lines = len(content.splitlines())
                except Exception:
                    lines = 0

                complexity = "niedrig"
                if lines > 400:
                    complexity = "hoch"
                elif lines > 150:
                    complexity = "mittel"

                modules_info.append(
                    {
                        "name": f.name,
                        "lines": lines,
                        "complexity": complexity,
                    }
                )

        modules_info.sort(key=lambda m: m["lines"], reverse=True)
        return modules_info

    def update(self) -> list:
        modules_info = self.analyze_modules()
        data = {
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S"),
            "modules": modules_info,
        }
        self._save_plan(data)
        return modules_info
