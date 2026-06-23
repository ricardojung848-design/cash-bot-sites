from pathlib import Path

class SystemChecker:
    def __init__(self, logger, config_dir, logs_dir, modules_dir, engines_dir, files_to_check):
        self.log = logger
        self.config_dir = config_dir
        self.logs_dir = logs_dir
        self.modules_dir = modules_dir
        self.engines_dir = engines_dir
        self.files_to_check = files_to_check

    def run(self):
        self.log("Starte Systemprüfung (PRO‑Version).")

        issues = []

        # Ordner prüfen
        for path in [self.config_dir, self.logs_dir, self.modules_dir, self.engines_dir]:
            if not path.exists():
                issues.append(f"Fehlender Ordner: {path}")

        # Dateien prüfen
        for path in self.files_to_check:
            if not path.exists():
                issues.append(f"Fehlende Datei: {path}")

        if issues:
            for i in issues:
                self.log(f"Systemproblem erkannt: {i}")
            return False

        self.log("Systemstruktur wirkt konsistent (PRO‑Check).")
        return True
