import time
import re
import tkinter as tk
from pathlib import Path
from typing import Any, List, Dict
from doctor_core.logging import log_doctor

# Traceback-Pattern: File "...", line X, in function
TRACEBACK_FILE_RE = re.compile(r'File "(.+?)", line (\d+), in (.+)')


class FixSuggestionEngine:
    """
    PRO-Version mit Auto-Fill Integration:
    - Analysiert Logs nach Systemfehlern
    - Extrahiert Fehlerquellen und generiert Patches
    - Befüllt die Benutzeroberfläche direkt ohne manuelle Eingaben
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
        print("[ENGINE] FixSuggestionEngine mit Auto-Fill bereit.")

    def analyze_and_autofill(self, ui_instance: Any, traceback_text: str, error_message: str):
        """
        Analysiert den Fehler der Engine und füllt die Eingabefelder
        der Benutzeroberfläche autonom aus.
        """
        print("[PRO-HEALING] Analysiere Log-Daten für UI-Auto-Fill...")
        
        # 1. Quellcodedatei ermitteln
        tb_info = self._extract_traceback_info(traceback_text)
        if tb_info and "source_file" in tb_info:
            target_file = tb_info["source_file"]
        else:
            file_match = re.findall(r'File "([^"]+)"', traceback_text)
            target_file = file_match[-1] if file_match else "core/Agent_Worker.py"

        # Relativen Pfad bereinigen
        if "Cash_Bot" in target_file:
            target_file = target_file.split("Cash_Bot")[-1].strip("\\/").replace("\\", "/")

        # 2. Spezifischen Reparatur-Code generieren
        if "State-Manager" in error_message or "FabrikEngine" in error_message or "RuntimeError" in error_message:
            suggested_code = """# PRO AUTO-FIX: Registriert den State-Manager im EngineManager
from doctor_core.engine_manager import EngineManager
from doctor_core.state import DoctorState
from modules.fabrik_engine import FabrikEngine

def worker_loop():
    print("[BOOT] Starten der Agent Worker Engine (PRO)...")
    manager = EngineManager()
    
    # Automatisch nachgerüstet:
    state = DoctorState()
    manager.register("state", state)
    
    fabrik = FabrikEngine(manager)
    # Restlicher Loop läuft stabil weiter
"""
        else:
            suggested_code = f"# Automatischer Code-Vorschlag für:\n# {error_message}"

        # 3. Widgets in der Benutzeroberfläche ermitteln und befüllen
        try:
            for widget in ui_instance.winfo_children():
                if isinstance(widget, tk.Frame):
                    for sub_w in widget.winfo_children():
                        if isinstance(sub_w, tk.Entry):
                            sub_w.delete(0, "end")
                            sub_w.insert(0, target_file)
                        elif isinstance(sub_w, tk.Text):
                            sub_w.delete("1.0", "end")
                            sub_w.insert("1.0", suggested_code)
            print(f"[PRO-HEALING] UI-Felder erfolgreich ausgefüllt für: {target_file}")
        except Exception as e:
            print(f"[ERROR] Fehler beim UI-Befüllen: {e}")

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
            seen_keywords = set()

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

        data = {
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S"),
            "suggestions": suggestions,
        }

        if self.engines and self.engines.has("state"):
            try:
                state = self.engines.get("state")
                state.set_state("fixes", data)
                log_doctor(f"FixSuggestionEngine: {len(suggestions)} Fehler-Muster im Langzeit-State aktualisiert.")
            except Exception as e:
                log_doctor(f"FixSuggestionEngine: Fehler beim Speichern im System-State: {e}")
        else:
            log_doctor(f"FixSuggestionEngine: State-Manager nicht registriert.")

        return suggestions