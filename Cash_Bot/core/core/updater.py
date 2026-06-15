import os
import time
import json
import urllib.request
import sys
import shutil

from .utils import (
    BASE_DIR,
    CONFIG_DIR,
    info_updater,
    warn_updater,
    error_updater,
    load_json,
    save_json,
)

UPDATE_CONFIG_PATH = os.path.join(CONFIG_DIR, "update_config.json")
UPDATE_SERVER_URL = "https://raw.githubusercontent.com/ricardojung848-design/cash-bot-sites/main/update_server.json"


def load_local_version() -> str:
    data = load_json(UPDATE_CONFIG_PATH, default={"version": "0.0.0"})
    return data.get("version", "0.0.0")


def save_local_version(version: str):
    save_json(UPDATE_CONFIG_PATH, {"version": version})


def fetch_update_info() -> dict | None:
    try:
        with urllib.request.urlopen(UPDATE_SERVER_URL, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        error_updater(f"[UPDATER] Fehler beim Abrufen der Update-Info: {e}")
        return None


def backup_file(path: str):
    if not os.path.exists(path):
        return
    backup_path = path + ".bak"
    try:
        shutil.copy2(path, backup_path)
        info_updater(f"[UPDATER] Backup erstellt: {backup_path}")
    except Exception as e:
        warn_updater(f"[UPDATER] Konnte Backup nicht erstellen ({path}): {e}")


def download_file(url: str, target_path: str):
    try:
        info_updater(f"[UPDATER] Lade {os.path.basename(target_path)}...")
        with urllib.request.urlopen(url, timeout=20) as r:
            data = r.read()
        with open(target_path, "wb") as f:
            f.write(data)
        info_updater(f"[UPDATER] Datei aktualisiert: {target_path}")
    except Exception as e:
        error_updater(f"[UPDATER] Fehler beim Download von {url}: {e}")
        raise


def apply_update(files_map: dict):
    for filename, url in files_map.items():
        local_path = os.path.join(BASE_DIR, filename)
        backup_file(local_path)
        download_file(url, local_path)


def check_and_update_once() -> bool:
    """
    Prüft einmal auf Updates.
    Gibt True zurück, wenn ein Update durchgeführt wurde.
    """
    info_updater("[UPDATER] Prüfe auf Updates...")
    local_version = load_local_version()
    data = fetch_update_info()

    if not data:
        warn_updater("[UPDATER] Keine gültige Update-Info erhalten.")
        return False

    latest = data.get("latest_version", local_version)
    files = data.get("files", {})

    if latest != local_version:
        info_updater(f"[UPDATER] Update gefunden: {local_version} → {latest}")
        try:
            apply_update(files)
            save_local_version(latest)
            info_updater("[UPDATER] Update abgeschlossen.")
            return True
        except Exception as e:
            error_updater(f"[UPDATER] Update fehlgeschlagen: {e}")
            return False
    else:
        info_updater("[UPDATER] Keine Updates verfügbar.")
        return False


def auto_update_loop(interval_seconds: int = 600):
    """
    Endlosschleife: regelmäßig auf Updates prüfen.
    Bei erfolgreichem Update → Prozess neu starten.
    """
    while True:
        updated = check_and_update_once()
        if updated:
            info_updater("[UPDATER] Starte Prozess neu...")
            time.sleep(2)
            os.execv(sys.executable, [sys.executable] + sys.argv)
        time.sleep(interval_seconds)
