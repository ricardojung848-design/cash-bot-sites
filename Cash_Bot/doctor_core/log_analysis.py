class LogAnalyzer:
    def __init__(self, logger, logs_dir):
        self.log = logger
        self.logs_dir = logs_dir

    def run(self):
        self.log("Starte Loganalyse (PRO‑Version).")

        log_files = []
        if self.logs_dir.exists():
            for f in self.logs_dir.iterdir():
                if f.is_file() and f.suffix in [".log", ".txt"]:
                    log_files.append(f)

        if not log_files:
            self.log("Keine Log‑Dateien gefunden.")
            return False

        self.log(f"{len(log_files)} Log‑Datei(en) gefunden.")
        return True
