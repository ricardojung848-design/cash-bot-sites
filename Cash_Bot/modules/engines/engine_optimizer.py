import time
from pathlib import Path
from typing import Any, List, Dict
from doctor_core.logging import log_doctor


class OptimizerEngine:
    """
    MEGA-PRO-Version:
    - Analysiert die Struktur des 'modules'-Ordners zur Laufzeit
    - Berechnet die Zeilenanzahl und bestimmt dynamisch die Komplexitätsstufe
    - Migriert die flache JSON-Logik direkt in den zentralen SQLite-State
    - Sortiert Kandidaten absteigend nach Optimierungspotenzial (Größe)
    """

    def __init__(self, engine_manager: Any = None):
        self.engines = engine_manager
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.modules_dir = self.base_dir / "modules"

    def analyze_modules(self) -> List[Dict[str, Any]]:
        """Scannt das Verzeichnis und sammelt Metriken über die Skriptgrößen."""
        modules_info = []
        if not self.modules_dir.exists():
            log_doctor(f"OptimizerEngine: Verzeichnis nicht gefunden: {self.modules_dir}")
            return modules_info

        for f in self.modules_dir.iterdir():
            if f.is_file() and f.suffix == ".py" and not f.name.startswith("_"):
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    lines = len(content.splitlines())
                except Exception as e:
                    log_doctor(f"OptimizerEngine: Fehler beim Lesen von {f.name}: {e}")
                    lines = 0

                # Dynamische Bestimmung der Komplexitätsklasse
                if lines > 400:
                    complexity = "hoch"
                elif lines > 150:
                    complexity = "mittel"
                else:
                    complexity = "niedrig"

                modules_info.append({
                    "name": f.name,
                    "lines": lines,
                    "complexity": complexity,
                })

        # Größte Dateien nach oben priorisieren
        modules_info.sort(key=lambda m: m["lines"], reverse=True)
        return modules_info

    def update(self) -> List[Dict[str, Any]]:
        """Führt die Analyse aus und synchronisiert das Ergebnis mit dem SQLite-State."""
        log_doctor("OptimizerEngine: Starte statische Codeanalyse der Erweiterungs-Module.")
        modules_info = self.analyze_modules()
        
        data = {
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S"),
            "modules": modules_info,
        }

        if self.engines and self.engines.has("state"):
            try:
                state = self.engines.get("state")
                # Bindung an den Schlüssel 'optimizer', den deine Phase6Simulation erwartet
                state.set_state("optimizer", data)
                log_doctor(f"OptimizerEngine: {len(modules_info)} Module erfolgreich analysiert und im State persistiert.")
            except Exception as e:
                log_doctor(f"OptimizerEngine: Fehler beim Schreiben in die Datenbank: {e}")
        else:
            log_doctor(f"OptimizerEngine: State-Manager fehlt. {len(modules_info)} Ergebnisse nur im RAM vorhanden.")

        return modules_info