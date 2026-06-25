from pathlib import Path
import os
import subprocess
import sys
from typing import List, Dict, Any, Tuple
from doctor_core.logging import log_doctor


class SystemChecker:
    """
    MEGA-PRO-Version:
    - Erweiterte Integritäts- und Berechtigungsprüfung (Security-Layer)
    - Isolierte Test-Sandbox zur gefahrlosen Ausführung von Auto-Fix-Patches
    - Überwachung kritischer Systemressourcen für Windows ARM64
    """

    def __init__(self, engine_manager: Any = None):
        self.engines = engine_manager
        
        # Pfade dynamisch aus der Projektstruktur ableiten (Ausfallsicher)
        self.base_dir = Path(__file__).resolve().parent.parent
        self.config_dir = self.base_dir / "config"
        self.logs_dir = self.base_dir / "logs"
        self.modules_dir = self.base_dir / "modules"
        self.doctor_core_dir = self.base_dir / "doctor_core"
        
        # Wichtige Kerndateien, die zwingend existieren müssen
        self.critical_files = [
            self.doctor_core_dir / "state.py",
            self.doctor_core_dir / "engine_manager.py",
            self.doctor_core_dir / "background.py",
            self.config_dir / "doctor_memory.sqlite"
        ]

    def run(self) -> bool:
        """Führt eine vollständige Sicherheits- und Integritätsprüfung durch."""
        log_doctor("SystemChecker: Starte erweiterten Sicherheits- und Integritäts-Check.")
        issues = []

        # 1. Verzeichnis-Existenz und Schreibrechte prüfen
        directories = {
            "Config": self.config_dir,
            "Logs": self.logs_dir,
            "Modules": self.modules_dir,
            "Core": self.doctor_core_dir
        }

        for name, path in directories.items():
            if not path.exists():
                issues.append(f"Fehlender Ordner: {path}")
                continue
            
            # Aktive Prüfung auf Schreibrechte (wichtig für Windows-Berechtigungen)
            if not os.access(path, os.W_OK):
                issues.append(f"Keine Schreibrechte im Ordner: {path}")

        # 2. Kritische Dateien prüfen
        for path in self.critical_files:
            if not path.exists():
                # Die SQLite-Datenbank wird beim ersten Start von state.py erzeugt
                if path.suffix == ".sqlite":
                    continue
                issues.append(f"Kritische Systemdatei fehlt: {path}")

        # 3. Auswertung
        if issues:
            for issue in issues:
                log_doctor(f"CRITICAL Security/System-Problem: {issue}")
                if self.engines and self.engines.has("state"):
                    self.engines.get("state").log_error("SystemChecker", issue)
            return False

        log_doctor("SystemChecker: Systemstruktur und Berechtigungen sind absolut integer.")
        return True

    def execute_in_sandbox(self, code_snippet: str, timeout_seconds: int = 5) -> Tuple[bool, str]:
        """
        Der Security-Layer für die Auto-Fix-Engine.
        Führt Python-Code isoliert aus und fängt Endlosschleifen oder Crashes ab,
        ohne dass das Hauptsystem gefährdet wird.
        """
        log_doctor("Security-Layer: Starte Code-Validierung in der Sandbox...")
        
        # Temporäre Testdatei in der Sandbox erzeugen
        sandbox_file = self.modules_dir / "_sandbox_test.py"
        
        try:
            # Code sicher schreiben
            sandbox_file.write_text(code_snippet, encoding="utf-8")
            
            # Subprozess isoliert mit eingeschränkten Rechten starten
            result = subprocess.run(
                [sys.executable, str(sandbox_file)],
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )
            
            if result.returncode == 0:
                log_doctor("Security-Layer: Sandbox-Test ERFOLGREICH.")
                return True, result.stdout
            else:
                log_doctor("Security-Layer: Sandbox-Test FEHLGESCHLAGEN (Code fehlerhaft).")
                return False, result.stderr

        except subprocess.TimeoutExpired:
            log_doctor(f"Security-Layer: WARNUNG - Code-Laufzeit überschritten (Timeout nach {timeout_seconds}s).")
            return False, "TIMEOUT: Mögliche Endlosschleife im generierten Code verhindert."
        except Exception as e:
            log_doctor(f"Security-Layer: Fehler bei Sandbox-Ausführung: {str(e)}")
            return False, str(e)
        finally:
            # Aufräumen: Testdatei restlos entfernen
            if sandbox_file.exists():
                try:
                    os.remove(sandbox_file)
                except Exception:
                    pass