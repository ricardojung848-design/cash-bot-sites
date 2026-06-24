import time
import json
import re
from pathlib import Path
from doctor_core.logging import log_doctor


TRACEBACK_FILE_RE = re.compile(r'File "(.+?)", line (\d+), in (.+)')


class FixSuggestionEngine:
    """
    Phase‑7 PRO:
    - scannt alle Logs (.log, .txt)
    - erkennt Exceptions, Tracebacks, typische Fehlermuster
    - versucht, die betroffene Quell‑Datei + Zeile zu ermitteln
    """

    KEYWORDS = {
        "SyntaxError": "Syntax prüfen (Klammern, Anführungszeichen, Einrückung).",
        "ConnectionError": "Netzwerkverbindung, API‑URL und Zeitüberschreitungen prüfen.",
        "Timeout": "Timeout erhöhen oder Last reduzieren.",
        "KeyError": "Dictionary‑Zugriffe prüfen, .get() mit Default verwenden.",
        "FileNotFoundError": "Pfad und Dateinamen prüfen, Datei ggf. anlegen.",
    }

    GENERIC_PATTERNS = [
        r"Traceback \(most recent call last\):",
        r"\bException\b",
        r"\bError\b",
        r"\bRuntimeError\b",
        r"\bValueError\b",
        r"\bTypeError\b",
        r"\bNameError\b",
        r"\bImportError\b",
        r"\bIndexError\b",
    ]

    def __init__(self, logger=log_doctor, logs_dir=None, state_file=None):
        self.logger = logger
        self.logs_dir = Path(logs_dir)
        self.state_file = Path(state_file)

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

    def _extract_traceback_info(self, content: str) -> dict | None:
        """
        Nimmt den letzten 'File "...", line X, in ...' Block aus einem Traceback.
        """
        matches = list(TRACEBACK_FILE_RE.finditer(content))
        if not matches:
            return None
        m = matches[-1]
        return {
            "source_file": m.group(1),
            "line": int(m.group(2)),
            "function": m.group(3),
        }

    def _scan_logs(self) -> list:
        suggestions = []

        if not self.logs_dir.exists():
            self.logger(f"FixSuggestionEngine: logs_dir existiert nicht: {self.logs_dir}")
            return suggestions

        for f in self.logs_dir.iterdir():
            if not f.is_file():
                continue
            if f.suffix not in [".log", ".txt"]:
                continue

            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except Exception as e:
                self.logger(f"FixSuggestionEngine: Fehler beim Lesen von {f}: {e}")
                continue

            tb_info = self._extract_traceback_info(content)

            # 1) Spezifische Keywords
            for kw, hint in self.KEYWORDS.items():
                if kw in content:
                    s = {
                        "log_file": str(f),
                        "keyword": kw,
                        "hint": hint,
                    }
                    if tb_info:
                        s.update(tb_info)
                    suggestions.append(s)

            # 2) Generische Fehler
            for pattern in self.GENERIC_PATTERNS:
                if re.search(pattern, content):
                    s = {
                        "log_file": str(f),
                        "keyword": pattern,
                        "hint": (
                            "Allgemeiner Fehler erkannt. "
                            "Traceback und Fehlermeldung genau lesen, "
                            "betroffene Funktion/Zeile im Code prüfen."
                        ),
                    }
                    if tb_info:
                        s.update(tb_info)
                    suggestions.append(s)

        return suggestions

    def update(self) -> list:
        suggestions = self._scan_logs()

        data = {
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S"),
            "suggestions": suggestions,
        }

        self._save_suggestions(data)
        return suggestions
