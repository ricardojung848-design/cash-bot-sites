import time
from pathlib import Path

# Basis-Pfad für die Log-Dateien definieren
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "doctor.log"

def log_doctor(message: str) -> None:
    """
    Zentrale Logging-Funktion für das gesamte Agent-Doctor Ökosystem.
    Schreibt konsolidierte Logs in die Konsole und in doctor.log.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] [DOCTOR] {message}"
    
    # 1. In die Konsole drucken
    print(formatted_msg, flush=True)
    
    # 2. In die Log-Datei schreiben
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted_msg + "\n")
    except Exception as e:
        print(f"[{timestamp}] [CRITICAL] Log-Schreibfehler: {e}", flush=True)