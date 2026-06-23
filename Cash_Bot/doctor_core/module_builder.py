from pathlib import Path

class ModuleBuilder:
    def __init__(self, logger, modules_dir):
        self.log = logger
        self.modules_dir = modules_dir

    def create_module(self, name: str):
        if not name:
            self.log("Modul-Builder: Kein Name angegeben.")
            return False

        filename = self.modules_dir / f"{name}.py"
        if filename.exists():
            self.log(f"Modul-Builder: Datei existiert bereits: {filename}")
            return False

        class_name = "".join(part.capitalize() for part in name.split("_"))
        template_code = (
            "import time\n\n"
            f"class {class_name}:\n"
            "    def __init__(self):\n"
            "        pass\n\n"
            "    def run(self):\n"
            "        # TODO: Implementiere die Logik dieses Moduls\n"
            "        time.sleep(0.1)\n"
        )

        try:
            filename.write_text(template_code, encoding="utf-8")
            self.log(f"Neues Modul erstellt: {filename}")
            return True
        except Exception as e:
            self.log(f"Fehler beim Erstellen des Moduls: {e}")
            return False
