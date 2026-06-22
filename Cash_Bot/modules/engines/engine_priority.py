import time
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # .../Cash_Bot
CONFIG_DIR = BASE_DIR / "config"
PRIORITY_FILE = CONFIG_DIR / "priority_plan.json"
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


class PriorityEngine:
    """
    Priorisiert Aufgaben basierend auf:
    - Risiko
    - Anzahl Logs
    - Anzahl Commands
    """

    def __init__(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if not PRIORITY_FILE.exists():
            _safe_save_json(
                PRIORITY_FILE,
                {
                    "last_update": None,
                    "tasks": [],
                },
            )

    def _load_doctor_state(self) -> dict:
        return _safe_load_json(
            DOCTOR_STATE_FILE,
            {
                "status": "unknown",
                "last_logs": [],
                "last_commands": [],
                "risk_score": 0.0,
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

    def _save_priority(self, data: dict):
        _safe_save_json(PRIORITY_FILE, data)

    def build_priority_list(self) -> list:
        ds = self._load_doctor_state()
        logs = ds.get("last_logs", [])
        cmds = ds.get("last_commands", [])
        risk = float(ds.get("risk_score", 0.0))

        tasks = []

        if risk >= 4.0:
            tasks.append(
                {
                    "name": "Systemprüfung & Self-Healing",
                    "reason": "Erhöhtes Risiko erkannt",
                    "priority": 1,
                }
            )

        if len(logs) > 20:
            tasks.append(
                {
                    "name": "Loganalyse & Optimierung",
                    "reason": "Viele Log-Einträge vorhanden",
                    "priority": 2,
                }
            )

        if len(cmds) > 10:
            tasks.append(
                {
                    "name": "Review der letzten Befehle",
                    "reason": "Viele Interaktionen mit Doctor",
                    "priority": 3,
                }
            )

        if not tasks:
            tasks.append(
                {
                    "name": "Regelmäßige Wartung",
                    "reason": "Keine akuten Probleme, aber Routine sinnvoll",
                    "priority": 4,
                }
            )

        tasks.sort(key=lambda t: t["priority"])
        return tasks

    def update(self) -> list:
        tasks = self.build_priority_list()
        data = {
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tasks": tasks,
        }
        self._save_priority(data)
        return tasks
