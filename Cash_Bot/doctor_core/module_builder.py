from pathlib import Path
from typing import Any
from doctor_core.logging import log_doctor


class ModuleBuilder:
    """
    MEGA-PRO-Version:
    - Generiert autonom neue, standardisierte Python-Module im 'modules'-Ordner
    - Erzeugt automatisch valide Klassen-Strukturen (CamelCase) basierend auf Dateinamen
    - Garantiert die Verzeichnis-Integrität vor dem Schreibprozess
    - Vollständig integriert in das Doctor-Core-Ökosystem
    """

    def __init__(self, engine_manager: Any = None):
        self.engines = engine_manager
        self.base_dir = Path(__file__).resolve().parent.parent
        self.modules_dir = self.base_dir / "modules"

    def create_module(self, name: str) -> bool:
        """
        Erstellt eine neue Python-Datei mit einer standardisierten Boilerplate-Klasse.
        Beispiel: 'social_monitor' -> class SocialMonitor
        """
        if not name:
            log_doctor("ModuleBuilder: Modul-Erstellung abgelehnt. Kein Name angegeben.")
            return False

        # Sicherstellen, dass das Zielverzeichnis existiert
        self.modules_dir.mkdir(parents=True, exist_ok=True)

        filename = self.modules_dir / f"{name}.py"
        if filename.exists():
            log_doctor(f"ModuleBuilder: Datei existiert bereits: {filename}")
            return False

        # Dynamische Konvertierung von snake_case zu CamelCase für den Klassennamen
        class_name = "".join(part.capitalize() for part in name.split("_"))
        
        # Das standardisierte, saubere Enterprise-Template
        template_code = (
            "import time\n"
            "from doctor_core.logging import log_doctor\n\n\n"
            f"class {class_name}:\n"
            "    def __init__(self, engine_manager=None):\n"
            "        self.engines = engine_manager\n"
            "        log_doctor(f'" + class_name + ": Instanziiert.')\n\n"
            "    def run(self) -> bool:\n"
            "        # TODO: Implementiere die autonome Logik dieses Moduls\n"
            "        log_doctor(f'" + class_name + ": Führe Standard-Task aus.')\n"
            "        time.sleep(0.1)\n"
            "        return True\n"
        )

        try:
            filename.write_text(template_code, encoding="utf-8")
            log_doctor(f"ModuleBuilder: Neues Modul erfolgreich generiert -> {filename.name}")
            
            # Registriere die Erstellung direkt in der Roadmap des Planners, falls aktiv
            if self.engines and self.engines.has("state"):
                try:
                    state = self.engines.get("state")
                    planner_data = state.get_state("planner", {"roadmap": []})
                    planner_data["roadmap"].append(f"[System] Neues Modul generiert: {name}.py")
                    state.set_state("planner", planner_data)
                except Exception:
                    pass

            return True
            
        except Exception as e:
            log_doctor(f"ModuleBuilder: Fehler beim Schreiben des Moduls '{name}': {e}")
            return False