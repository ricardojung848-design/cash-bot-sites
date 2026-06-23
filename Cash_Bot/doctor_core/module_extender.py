from pathlib import Path

class ModuleExtender:
    def __init__(self, logger, modules_dir):
        self.log = logger
        self.modules_dir = modules_dir

    def append_to_module(self, name: str, code: str):
        filename = self.modules_dir / f"{name}.py"
        if not filename.exists():
            self.log(f"Modul-Erweiterer: Modul existiert nicht: {filename}")
            return False

        try:
            with open(filename, "a", encoding="utf-8") as f:
                f.write("\n" + code + "\n")
            self.log(f"Modul erweitert: {filename}")
            return True
        except Exception as e:
            self.log(f"Fehler beim Erweitern des Moduls: {e}")
            return False
