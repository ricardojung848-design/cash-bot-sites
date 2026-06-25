import sys
import shutil
from pathlib import Path
from typing import List

from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager
from core.utils import (
    BASE_DIR,
    CONFIG_DIR,
    LOGS_DIR,
    DATA_DIR,
    OUTPUT_DIR,
    SOCIAL_DIR,
)


class SystemStructureManager:
    """
    PRO-Version des SystemStructureManagers:
    - Überprüft und repariert automatisch die Ordner- und Dateistruktur des Projekts.
    - Vollständig objektorientiert und in das EngineManager-Ökosystem integriert.
    - Nutzt moderne Pathlib-Methoden für sichere und plattformunabhängige Pfadoperationen.
    """

    def __init__(self, engine_manager: EngineManager):
        self.engines = engine_manager
        self.report: List[str] = []

        # Konvertierung der Import-Pfade in Path-Objekte
        self.base_path = Path(BASE_DIR).resolve()
        self.config_path = Path(CONFIG_DIR).resolve()
        self.logs_path = Path(LOGS_DIR).resolve()
        self.data_path = Path(DATA_DIR).resolve()
        self.output_path = Path(OUTPUT_DIR).resolve()
        self.social_path = Path(SOCIAL_DIR).resolve()

        # Erwartete Systemverzeichnisse definieren
        self.REQUIRED_DIRS = {
            "core": self.base_path / "core",
            "modules": self.base_path / "modules",
            "config": self.config_path,
            "logs": self.logs_path,
            "scraped_data": self.data_path,
            "generated_content": self.output_path,
            "social_media": self.social_path,
        }

        # Erwartete Systemdateien definieren
        self.REQUIRED_FILES = {
            "config/token.txt": self.config_path / "token.txt",
            "config/cashbot_config.json": self.config_path / "cashbot_config.json",
            "aufgaben.json": self.base_path / "aufgaben.json",
            "rueckgabe.json": self.base_path / "rueckgabe.json",
        }

    def add_report(self, msg: str) -> None:
        """Fügt dem internen Report eine Nachricht hinzu und loggt sie zentral."""
        self.report.append(msg)
        log_doctor(f"SystemStructureManager: {msg}")

    def ensure_directories(self) -> None:
        """Prüft die Existenz der erforderlichen Ordner und erstellt sie bei Bedarf."""
        for name, path in self.REQUIRED_DIRS.items():
            try:
                if not path.exists():
                    path.mkdir(parents=True, exist_ok=True)
                    self.add_report(f"📁 Ordner erstellt: {path}")
                else:
                    self.add_report(f"✔ Ordner OK: {path}")
            except Exception as e:
                self.add_report(f"❌ Fehler beim Erstellen des Ordners {name} ({path}): {e}")

    def ensure_files(self) -> None:
        """Prüft die Existenz kritischer Dateien und erstellt leere Dummies, falls sie fehlen."""
        for name, path in self.REQUIRED_FILES.items():
            try:
                if not path.exists():
                    # Ordnerstruktur für die Datei sicherstellen
                    path.parent.mkdir(parents=True, exist_ok=True)
                    # Leere Datei initialisieren
                    path.write_text("", encoding="utf-8")
                    self.add_report(f"📄 Datei erstellt: {path}")
                else:
                    self.add_report(f"✔ Datei OK: {path}")
            except Exception as e:
                self.add_report(f"❌ Fehler beim Erstellen der Datei {name} ({path}): {e}")

    def auto_correct_structure(self) -> None:
        """Findet falsch platzierte Systemdateien und verschiebt sie an den korrekten Ort."""
        correct_token_path = self.config_path / "token.txt"
        
        # Liste bekannter falscher Ablageorte für die token.txt
        wrong_locations = [
            self.base_path / "token.txt",
            self.base_path / "core" / "token.txt",
            self.base_path / "modules" / "token.txt",
        ]

        for wrong_path in wrong_locations:
            try:
                if wrong_path.is_file():
                    # Vor dem Verschieben das Zielverzeichnis absichern
                    self.config_path.mkdir(parents=True, exist_ok=True)
                    
                    # Datei verschieben (shutil.move akzeptiert auch Path-Objekte)
                    shutil.move(str(wrong_path), str(correct_token_path))
                    self.add_report(f"🔧 token.txt korrigiert und verschoben nach: {correct_token_path}")
            except Exception as e:
                self.add_report(f"❌ Fehler beim Verschieben der falsch platzierten Datei {wrong_path}: {e}")

    def get_status(self) -> str:
        """Gibt den aggregierten Prüfbericht als formatierten String zurück."""
        return "\n".join(self.report)

    def run_full_check(self) -> str:
        """Führt eine vollständige Systemdiagnose und automatische Strukturreparatur durch."""
        self.report.clear()
        self.add_report("🔍 Starte automatisierte Systemstruktur-Prüfung...")
        self.ensure_directories()
        self.ensure_files()
        self.auto_correct_structure()
        self.add_report("✅ Systemstruktur vollständig geprüft und abgeglichen.")
        return self.get_status()


# Abwärtskompatibler Einstiegspunkt für ältere Programmteile
def run_check_legacy(engine_manager: EngineManager) -> str:
    """Erlaubt Legacy-Modulen den direkten Aufruf der Überprüfung."""
    manager = SystemStructureManager(engine_manager)
    return manager.run_full_check()