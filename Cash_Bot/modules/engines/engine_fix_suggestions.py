import time
import json
from pathlib import Path
from doctor_core.logging import log_doctor


class FixSuggestionEngine:
    """
    Phase‑7 Engine:
    Analysiert Logs, extrahiert Fehler, erzeugt Fix‑Vorschläge.
    Kompatibel mit Agent_Doctor.py (logger, logs_dir, state_file).
    """

    KEYWORDS = {
        "SyntaxError": "Syntax prüfen, insbesondere Anführungszeichen und Klammern.",
        "ConnectionError": "Netzwerkverbindung und API-URL prüfen.",
        "Timeout": "Timeout erhöhen oder Last reduzieren.",
        "KeyError": "Dictionary-Schlüssel prüfen oder Default-Werte setzen.",
        "FileNotFoundError": "Pfad und Dateinamen prüfen, ggf. Datei anlegen.",
    }

    def __init__(self, logger=log_doctor, logs_dir=None, state_file=None):
        self.logger = logger
        self.logs_dir = Path(logs_dir)
        self.state_file = Path(state_file)

        # Sicherstellen, dass Datei existiert
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.state_file.exists():
            self._save_suggestions({
                "last_update": None,
                "suggestions": [],
            })

    def _load_suggestions(self) -> dict:
        try:
            if not self.state_file.exists():
                return {"last_update": None, "suggestions": []}

            raw = self.state_file.read_text(encoding="utf-8")
            if not raw.strip():
                return {"last_update": None, "suggestions": []}

            return json.loads(raw)
        except Exception:
            return {"last_update": None, "suggestions": []}

    def _save_suggestions(self, data: dict):
        try:
            self.state_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            self.logger(f"FixSuggestionEngine: Fehler beim Speichern: {e}")

    def _scan_logs(self) -> list:
        suggestions = []

        if not self.logs_dir.exists():
            return suggestions

        for f in self.logs_dir.iterdir():
            if not f.is_file():
                continue
            if f.suffix not in [".log", ".txt"]:
                continue

            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            for kw, hint in self.KEYWORDS.items():
                if kw in content:
                    suggestions.append({
                        "file": str(f),
                        "keyword": kw,
                        "hint": hint,
                    })

        return suggestions

    def update(self) -> list:
        suggestions = self._scan_logs()

        data = {
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S"),
            "suggestions": suggestions,
        }

        self._save_suggestions(data)
        return suggestions
