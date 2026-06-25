import sys
import json
import datetime
from pathlib import Path
from typing import Any, Optional

# Zentrales Logging-System laden
from doctor_core.logging import log_doctor

# === BASIS-PFADE (Modernisiert via Pathlib) ===
# Ermittelt das Projekt-Hauptverzeichnis (eine Ebene über dem 'core'-Ordner)
BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_DIR = BASE_DIR / "config"
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "scraped_data"
OUTPUT_DIR = BASE_DIR / "generated_content"
SOCIAL_DIR = BASE_DIR / "social_media"

# Automatische Absicherung der Verzeichnisstruktur beim Import des Moduls
for directory in [CONFIG_DIR, LOGS_DIR, DATA_DIR, OUTPUT_DIR, SOCIAL_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


# === LEGACY LOGGING INTERFACES (Kompatibilitäts-Layer an log_doctor) ===
def _log_legacy_bridge(level: str, msg: str, target: str) -> None:
    """Interne Brücke, die alte Log-Aufrufe standardisiert an das neue System übergibt."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{level}] [{target}] {msg}"
    
    # Weiterleitung an den neuen Core-Logger
    log_doctor(formatted_msg)


def log_worker(msg: str) -> None:
    _log_legacy_bridge("INFO", msg, "Worker")

def warn_worker(msg: str) -> None:
    _log_legacy_bridge("WARN", msg, "Worker")

def error_worker(msg: str) -> None:
    _log_legacy_bridge("ERROR", msg, "Worker")

def log_telegram(msg: str) -> None:
    _log_legacy_bridge("INFO", msg, "Telegram")

def warn_telegram(msg: str) -> None:
    _log_legacy_bridge("WARN", msg, "Telegram")

def error_telegram(msg: str) -> None:
    _log_legacy_bridge("ERROR", msg, "Telegram")


# === JSON HELFER (Sicher und Typisiert) ===
def load_json(path: Any, default: Optional[Any] = None) -> Any:
    """Lädt eine JSON-Datei sicher ein. Akzeptiert Strings und Path-Objekte."""
    resolved_path = Path(path).resolve()
    if not resolved_path.is_file():
        return default
    try:
        with resolved_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log_doctor(f"Utils-Fehler: JSON-Ladefehler bei {resolved_path.name}: {e}")
        return default


def save_json(path: Any, data: Any) -> None:
    """Speichert Daten formatiert und atomar in eine JSON-Datei."""
    resolved_path = Path(path).resolve()
    try:
        # Sicherstellen, dass der Zielordner existiert
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        with resolved_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        error_worker(f"Fehler beim Speichern von JSON ({resolved_path.name}): {e}")


# === ZEIT HELFER ===
def timestamp() -> str:
    """Erzeugt einen standardisierten ISO-Zeitstempel."""
    return datetime.datetime.now().isoformat()


# Typ-Konvertierungen für externe Module, die OS-Strings als Pfad-Typen erwarten
# Dies stellt sicher, dass os.path.join() in alten Modulen nicht abstürzt
BASE_DIR = str(BASE_DIR)
CONFIG_DIR = str(CONFIG_DIR)
LOGS_DIR = str(LOGS_DIR)
DATA_DIR = str(DATA_DIR)
OUTPUT_DIR = str(OUTPUT_DIR)
SOCIAL_DIR = str(SOCIAL_DIR)