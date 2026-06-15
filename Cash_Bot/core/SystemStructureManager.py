import os
import shutil
from core.utils import (
    BASE_DIR,
    CONFIG_DIR,
    LOGS_DIR,
    DATA_DIR,
    OUTPUT_DIR,
    SOCIAL_DIR,
    log_worker,
    warn_worker,
    error_worker,
)

class SystemStructureManager:

    REQUIRED_DIRS = {
        "core": os.path.join(BASE_DIR, "core"),
        "modules": os.path.join(BASE_DIR, "modules"),
        "config": CONFIG_DIR,
        "logs": LOGS_DIR,
        "scraped_data": DATA_DIR,
        "generated_content": OUTPUT_DIR,
        "social_media": SOCIAL_DIR,
    }

    REQUIRED_FILES = {
        "config/token.txt": os.path.join(CONFIG_DIR, "token.txt"),
        "config/cashbot_config.json": os.path.join(CONFIG_DIR, "cashbot_config.json"),
        "aufgaben.json": os.path.join(BASE_DIR, "aufgaben.json"),
        "rueckgabe.json": os.path.join(BASE_DIR, "rueckgabe.json"),
    }

    def __init__(self):
        self.report = []

    def add_report(self, msg):
        self.report.append(msg)
        log_worker(msg)

    # === Ordner prüfen ===
    def ensure_directories(self):
        for name, path in self.REQUIRED_DIRS.items():
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                self.add_report(f"📁 Ordner erstellt: {path}")
            else:
                self.add_report(f"✔ Ordner OK: {path}")

    # === Dateien prüfen ===
    def ensure_files(self):
        for name, path in self.REQUIRED_FILES.items():
            if not os.path.exists(path):
                # leere Datei erstellen
                with open(path, "w", encoding="utf-8") as f:
                    f.write("")
                self.add_report(f"📄 Datei erstellt: {path}")
            else:
                self.add_report(f"✔ Datei OK: {path}")

    # === Falsch platzierte Dateien korrigieren ===
    def auto_correct_structure(self):
        # Beispiel: token.txt falsch abgelegt?
        wrong_locations = [
            os.path.join(BASE_DIR, "token.txt"),
            os.path.join(BASE_DIR, "core", "token.txt"),
            os.path.join(BASE_DIR, "modules", "token.txt"),
        ]

        for wrong in wrong_locations:
            if os.path.exists(wrong):
                correct = os.path.join(CONFIG_DIR, "token.txt")
                shutil.move(wrong, correct)
                self.add_report(f"🔧 token.txt verschoben nach: {correct}")

    # === Systemstatus zurückgeben ===
    def get_status(self):
        return "\n".join(self.report)

    # === Hauptfunktion ===
    def run_full_check(self):
        self.add_report("🔍 Starte Systemstruktur-Prüfung...")
        self.ensure_directories()
        self.ensure_files()
        self.auto_correct_structure()
        self.add_report("✅ Systemstruktur vollständig geprüft.")
        return self.get_status()
