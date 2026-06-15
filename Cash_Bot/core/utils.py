import os
import json
import datetime

# === BASIS-PFADE ===
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "scraped_data")
OUTPUT_DIR = os.path.join(BASE_DIR, "generated_content")
SOCIAL_DIR = os.path.join(BASE_DIR, "social_media")

# Ordner sicherstellen
for d in [CONFIG_DIR, LOGS_DIR, DATA_DIR, OUTPUT_DIR, SOCIAL_DIR]:
    os.makedirs(d, exist_ok=True)

# === LOGGING ===
def _log(level, msg, logfile):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)

    try:
        with open(logfile, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def log_worker(msg):
    _log("INFO", msg, os.path.join(LOGS_DIR, "worker.log"))

def warn_worker(msg):
    _log("WARN", msg, os.path.join(LOGS_DIR, "worker.log"))

def error_worker(msg):
    _log("ERROR", msg, os.path.join(LOGS_DIR, "worker.log"))

def log_telegram(msg):
    _log("INFO", msg, os.path.join(LOGS_DIR, "telegram.log"))

def warn_telegram(msg):
    _log("WARN", msg, os.path.join(LOGS_DIR, "telegram.log"))

def error_telegram(msg):
    _log("ERROR", msg, os.path.join(LOGS_DIR, "telegram.log"))

# === JSON HELFER ===
def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        error_worker(f"Fehler beim Speichern von JSON: {e}")

# === ZEIT HELFER ===
def timestamp():
    return datetime.datetime.now().isoformat()
