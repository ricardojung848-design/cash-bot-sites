import json
import urllib.request
import time
import os
import sys

UPDATE_CONFIG = "update_config.json"
UPDATE_URL = "https://raw.githubusercontent.com/ricardojung848-design/cash-bot-sites/main/update_server.json"

def load_local_version():
    if not os.path.exists(UPDATE_CONFIG):
        return "0.0.0"
    with open(UPDATE_CONFIG, "r") as f:
        return json.load(f)["version"]

def save_local_version(version):
    with open(UPDATE_CONFIG, "w") as f:
        json.dump({"version": version}, f)

def check_for_update():
    try:
        with urllib.request.urlopen(UPDATE_URL) as r:
            data = json.loads(r.read().decode())
        return data
    except Exception as e:
        print("[UPDATER] Fehler beim Abrufen:", e)
        return None

def download_file(url, filename):
    urllib.request.urlretrieve(url, filename)

def auto_update_loop():
    while True:
        print("[UPDATER] Prüfe auf Updates...")
        local_version = load_local_version()
        update_data = check_for_update()

        if update_data:
            latest = update_data["latest_version"]
            if latest != local_version:
                print(f"[UPDATER] Update gefunden: {local_version} → {latest}")
                for file, url in update_data["files"].items():
                    print(f"[UPDATER] Lade {file}...")
                    download_file(url, file)

                save_local_version(latest)
                print("[UPDATER] Update abgeschlossen. Starte Worker neu...")
                time.sleep(2)
                os.execv(sys.executable, ["python"] + sys.argv)
            else:
                print("[UPDATER] Keine Updates verfügbar.")
        else:
            print("[UPDATER] Update-Server nicht erreichbar.")

        time.sleep(600)
