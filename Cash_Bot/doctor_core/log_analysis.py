from pathlib import Path
import os
from typing import List, Dict, Any
from doctor_core.logging import log_doctor
from doctor_core.event_system import EventSystem  # Import für Phase 9 Integration


class LogAnalyzer:
    """
    MEGA-PRO-Version:
    - Autonomer Log-Parser für Fehlererkennung in Echtzeit
    - Extrahiert Fehler-Patterns, Stacktraces und kritische Meldungen
    - Triggert vollautomatisch das Event-System bei Systemfehlern
    - Merkt sich die letzte gelesene Dateigröße, um Overhead zu vermeiden
    """

    def __init__(self, engine_manager: Any = None):
        self.engines = engine_manager
        self.events = EventSystem()  # Direktzugriff auf die Event-Zentrale (Phase 9)
        self.base_dir = Path(__file__).resolve().parent.parent
        self.logs_dir = self.base_dir / "logs"
        
        # Speichert die Dateigröße beim letzten Check, um nur neue Zeilen zu lesen (Delta-Parsing)
        self._file_positions: Dict[str, int] = {}
        
        # Kritische Suchbegriffe für das Gehirn des Agenten
        self.error_keywords = ["ERROR", "CRITICAL", "EXCEPTION", "TRACEBACK", "FAILED"]

    def run(self) -> bool:
        """Sucht nach Logdateien und analysiert deren Inhalt auf Fehler."""
        log_doctor("LogAnalyzer: Starte tiefenstrukturelle Loganalyse.")

        if not self.logs_dir.exists():
            self.logs_dir.mkdir(parents=True, exist_ok=True)
            log_doctor("LogAnalyzer: Log-Verzeichnis existierte nicht, wurde erstellt.")
            return False

        log_files = [
            f for f in self.logs_dir.iterdir() 
            if f.is_file() and f.suffix in [".log", ".txt"] and not f.name.startswith("_")
        ]

        if not log_files:
            log_doctor("LogAnalyzer: Keine Log-Dateien zur Analyse gefunden.")
            return True

        found_issues = 0

        for file_path in log_files:
            issues = self._parse_file(file_path)
            found_issues += len(issues)
            
            # Jeden gefundenen Fehler ins System speisen
            for issue in issues:
                log_doctor(f"LogAnalyzer: Kritischer Eintrag in '{file_path.name}' isoliert: {issue['message']}")
                
                # 1. In der Memory-Engine (Phase 8) archivieren
                if self.engines and self.engines.has("state"):
                    self.engines.get("state").log_error(
                        module_name=file_path.stem,
                        error_message=issue["message"]
                    )
                
                # 2. Event über das echte EventSystem abfeuern (Phase 9)
                # Verwende das Event-Label "new_error", worauf deine AutoFixEngine lauscht
                self.events.trigger("new_error", {
                    "module": file_path.stem,
                    "error": issue["message"]
                })

        log_doctor(f"LogAnalyzer: Analyse beendet. {found_issues} neue Probleme isoliert.")
        return True

    def _parse_file(self, file_path: Path) -> List[Dict[str, str]]:
        """Liest hocheffizient nur die seit dem letzten Check hinzugefügten Log-Zeilen."""
        detected_issues = []
        file_key = str(file_path.resolve())
        
        try:
            current_size = file_path.stat().st_size
            last_position = self._file_positions.get(file_key, 0)

            # Wenn die Datei kleiner wurde (z.B. Log-Rotation), fangen wir von vorne an
            if current_size < last_position:
                last_position = 0

            if current_size == last_position:
                return [] # Keine neuen Einträge

            with file_path.open("r", encoding="utf-8", errors="ignore") as f:
                f.seek(last_position)
                new_lines = f.readlines()
                
                # Aktualisiere den Pointer für den nächsten Durchlauf
                self._file_positions[file_key] = f.tell()

            # Analyse der neuen Zeilen
            for line in new_lines:
                cleaned_line = line.strip()
                if not cleaned_line:
                    continue
                
                # Prüfen, ob eines der Keywords anschlägt
                if any(keyword in cleaned_line.upper() for keyword in self.error_keywords):
                    detected_issues.append({
                        "file": file_path.name,
                        "message": cleaned_line
                    })

        except Exception as e:
            log_doctor(f"LogAnalyzer: Fehler beim Parsen von {file_path.name}: {str(e)}")
            
        return detected_issues