import os
import json
import datetime
import hashlib

# Basisverzeichnis: .../Deto_Art_Agenten/Cash_Bot
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_DIR = os.path.join(BASE_DIR, "config")
LOG_DIR = os.path.join(BASE_DIR, "logs")
MODULE_DIR = os.path.join(BASE_DIR, "modules")

os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(MODULE_DIR, exist_ok=True)


# =========================
# Logging
# =========================

def _log_path(name: str) -> str:
    return os.path.join(LOG_DIR, name)

def _rotate_log(path: str, max_size: int = 2 * 1024 * 1024):
    if os.path.exists(path) and os.path.getsize(path) > max_size:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = f"{os.path.basename(path)}.{ts}.bak"
        os.rename(path, os.path.join(LOG_DIR, backup))

def log_generic(logfile: str, level: str, msg: str):
    path = _log_path(logfile)
    _rotate_log(path)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def log_worker(level: str, msg: str):
    log_generic("worker.log", level, msg)

def log_telegram(level: str, msg: str):
    log_generic("telegram.log", level, msg)

def log_updater(level: str, msg: str):
    log_generic("updater.log", level, msg)

def log_error(level: str, msg: str):
    log_generic("error.log", level, msg)


# Komfort-Shortcuts für Worker
def info_worker(msg):  log_worker("INFO", msg)
def warn_worker(msg):  log_worker("WARN", msg)
def error_worker(msg): log_worker("ERROR", msg)
def fatal_worker(msg): log_worker("FATAL", msg)

# Für Updater
def info_updater(msg):  log_updater("INFO", msg)
def warn_updater(msg):  log_updater("WARN", msg)
def error_updater(msg): log_updater("ERROR", msg)

# Für Telegram
def info_telegram(msg):  log_telegram("INFO", msg)
def warn_telegram(msg):  log_telegram("WARN", msg)
def error_telegram(msg): log_telegram("ERROR", msg)


# =========================
# JSON / Dateien
# =========================

def load_json(path: str, default=None):
    if default is None:
        default = {}
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def save_json(path: str, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        log_error("ERROR", f"Fehler beim Speichern von JSON ({path}): {e}")

def file_exists(path: str) -> bool:
    return os.path.exists(path)

def file_size(path: str) -> int:
    return os.path.getsize(path) if os.path.exists(path) else 0


# =========================
# Hash / Integrität
# =========================

def sha256_file(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        log_error("ERROR", f"Fehler beim Hashen von {path}: {e}")
        return None
