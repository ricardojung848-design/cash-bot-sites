import time
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # .../Cash_Bot
CONFIG_DIR = BASE_DIR / "config"
DOCTOR_STATE_FILE = CONFIG_DIR / "doctor_state.json"
PREDICTIVE_STATE_FILE = CONFIG_DIR / "predictive_state.json"


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


class PredictiveEngine:
    """
    Sehr einfache Predictive-Engine:
    - liest doctor_state.json
    - berechnet einen groben Risiko-Score
    - speichert Verlauf in predictive_state.json
    """

    def __init__(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if not PREDICTIVE_STATE_FILE.exists():
            _safe_save_json(
                PREDICTIVE_STATE_FILE,
                {
                    "history": [],
                    "last_score": 0.0,
                    "last_update": None,
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

    def _load_predictive_state(self) -> dict:
        return _safe_load_json(
            PREDICTIVE_STATE_FILE,
            {
                "history": [],
                "last_score": 0.0,
                "last_update": None,
            },
        )

    def _save_predictive_state(self, state: dict):
        _safe_save_json(PREDICTIVE_STATE_FILE, state)

    def compute_risk(self) -> float:
        """
        Berechnet einen einfachen Risiko-Score basierend auf:
        - Anzahl Logs
        - Anzahl Commands
        - vorhandenem risk_score aus Doctor
        """
        ds = self._load_doctor_state()
        logs = ds.get("last_logs", [])
        cmds = ds.get("last_commands", [])
        base_risk = float(ds.get("risk_score", 0.0))

        risk = base_risk
        risk += min(len(logs) / 50.0, 5.0)
        risk += min(len(cmds) / 20.0, 3.0)

        return float(min(risk, 10.0))

    def update(self) -> float:
        """
        Aktualisiert den Predictive-State und gibt den aktuellen Risiko-Score zurück.
        """
        score = self.compute_risk()
        state = self._load_predictive_state()
        history = state.get("history", [])
        history.append(
            {
                "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                "score": score,
            }
        )
        if len(history) > 100:
            history = history[-100:]
        state["history"] = history
        state["last_score"] = score
        state["last_update"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self._save_predictive_state(state)
        return score
