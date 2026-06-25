import time
import re
from pathlib import Path
from typing import Any, List, Dict
from doctor_core.logging import log_doctor

# Traceback-Pattern: File "...", line X, in function
TRACEBACK_FILE_RE = re.compile(r'File "(.+?)", line (\d+), in (.+)')


class FixSuggestionEngine:
    """
    MEGA-PRO-Version:
    - Analysiert Log-Dateien auf spezifische und generische Fehlermuster
    - Extrahiert präzise Quellcodedatei, Zeilennummer und Funktion aus Tracebacks
    - Migriert von flachen JSON-Dateien direkt in das SQLite-Langzeitgedächtnis
    - Liefert saubere Datensätze für die autonome Behebungs-Schleife
    """

    KEYWORDS = {
        "SyntaxError": "Syntax prüfen (Klammern, Anführungszeichen, Einrückung).",
        "ConnectionError": "Netzwerkverbindung, API-URL und Zeitüberschreitungen prüfen.",
        "Timeout": "Timeout erhöhen oder Last reduzieren.",
        "KeyError": "Dictionary-Zugriffe prüfen, .get() mit Default verwenden.",
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

    def __init__(self, engine_manager: Any = None):
        self.engines = engine_manager
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.logs_dir = self.base_dir / "logs"

    def _extract_traceback_info(self, content: str) -> Dict[str, Any] | None:
        """Extrahiert den letzten 'File "...", line X, in ...'-Block aus einem Traceback."""
        matches = list(TRACEBACK_FILE_RE.finditer(content))
        if not matches:
            return None
        m = matches[-1]
        return {
            "source_file": m.group(1),
            "line": int(m.group(2)),
            "function": m.group(3),
        }

    def _scan_logs(self) -> List[Dict[str, Any]]:
        """Durchsucht das Logverzeichnis nach vordefinierten Fehlermustern."""
        suggestions = []

        if not self.logs_dir.exists():
            log_doctor(f"FixSuggestionEngine: logs_dir existiert nicht: {self.logs_dir}")
            return suggestions

        for f in self.logs_dir.iterdir():
            if not f.is_file() or f.suffix not in [".log", ".txt"] or f.name.startswith("_"):
                continue

            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except Exception as e:
                log_doctor(f"FixSuggestionEngine: Fehler beim Lesen von {f.name}: {e}")
                continue

            tb_info = self._extract_traceback_info(content)

            # Eindeutige Treffer sammeln, um Duplikate innerhalb derselben Datei zu vermeiden
            seen_keywords = set()

            # 1. Spezifische Fehler prüfen
            for kw, hint in self.KEYWORDS.items():
                if kw in content and kw not in seen_keywords:
                    seen_keywords.add(kw)
                    s = {
                        "log_file": f.name,
                        "keyword": kw,
                        "hint": hint,
                    }
                    if tb_info:
                        s.update(tb_info)
                    suggestions.append(s)

            # 2. Generische Fehler prüfen
            for pattern in self.GENERIC_PATTERNS:
                if pattern not in seen_keywords and re.search(pattern, content):
                    seen_keywords.add(pattern)
                    s = {
                        "log_file": f.name,
                        "keyword": pattern,
                        "hint": "Allgemeiner Fehler erkannt. Traceback und Fehlermeldung prüfen.",
                    }
                    if tb_info:
                        s.update(tb_info)
                    suggestions.append(s)

        return suggestions

    def update(self) -> List[Dict[str, Any]]:
        """Führt den Scan aus und persistiert die Vorschläge im relationalen State."""
        suggestions = self._scan_logs()

        # Zustand für Phase-6-Simulation und Phase-7-Autofix bereitstellen
        data = {
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S"),
            "suggestions": suggestions,
        }

        if self.engines and self.engines.has("state"):
            try:
                state = self.engines.get("state")
                # Nutzt die abwärtskompatible JSON-Struktur des neuen State-Managers
                state.set_state("fixes", data)
                log_doctor(f"FixSuggestionEngine: {len(suggestions)} Fehler-Muster im Langzeit-State aktualisiert.")
            except Exception as e:
                log_doctor(f"FixSuggestionEngine: Fehler beim Speichern im System-State: {e}")
        else:
            log_doctor(f"FixSuggestionEngine: State-Manager nicht registriert. {len(suggestions)} Vorschläge im RAM.")

        return suggestions