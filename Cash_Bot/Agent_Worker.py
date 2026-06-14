import json
import os
import time
import datetime
import urllib.request
import urllib.parse
import Logik
import threading
import sys

# ============================================================
# AUTO-UPDATER
# ============================================================

UPDATE_CONFIG = "update_config.json"
UPDATE_URL = "https://raw.githubusercontent.com/ricardojung848-design/cash-bot-sites/main/update_server.json"


def load_local_version():
    if not os.path.exists(UPDATE_CONFIG):
        return "0.0.0"
    try:
        with open(UPDATE_CONFIG, "r", encoding="utf-8") as f:
            return json.load(f).get("version", "0.0.0")
    except:
        return "0.0.0"


def save_local_version(version):
    with open(UPDATE_CONFIG, "w", encoding="utf-8") as f:
        json.dump({"version": version}, f)


def check_for_update():
    try:
        with urllib.request.urlopen(UPDATE_URL, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        error(f"[UPDATER] Fehler beim Abrufen: {e}")
        return None


def download_file(url, filename):
    urllib.request.urlretrieve(url, filename)


def auto_update_loop():
    while True:
        info("[UPDATER] Prüfe auf Updates...")
        local = load_local_version()
        data = check_for_update()

        if data:
            latest = data.get("latest_version", local)
            if latest != local:
                info(f"[UPDATER] Update gefunden: {local} → {latest}")

                for file, url in data.get("files", {}).items():
                    try:
                        info(f"[UPDATER] Lade {file}...")
                        download_file(url, file)
                    except Exception as e:
                        error(f"[UPDATER] Fehler bei {file}: {e}")

                save_local_version(latest)
                info("[UPDATER] Update abgeschlossen. Starte Worker neu...")
                time.sleep(2)
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                info("[UPDATER] Keine Updates verfügbar.")
        else:
            warn("[UPDATER] Update-Server nicht erreichbar.")

        time.sleep(600)  # alle 10 Minuten prüfen


# ============================================================
# KONFIGURATION
# ============================================================

AUFGABEN_DATEI = "aufgaben.json"
CHAT_ID_FILE = "last_chat_id.txt"
TOKEN_FILE = "token.txt"

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "worker.log")
MAX_LOG_SIZE = 2 * 1024 * 1024  # 2 MB

os.makedirs(LOG_DIR, exist_ok=True)


# ============================================================
# LOGGING
# ============================================================

def rotate_log():
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_LOG_SIZE:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = f"worker_{timestamp}.log"
        os.rename(LOG_FILE, os.path.join(LOG_DIR, backup))


def log(level, msg):
    rotate_log()
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass


def info(msg): log("INFO", msg)
def warn(msg): log("WARN", msg)
def error(msg): log("ERROR", msg)
def fatal(msg): log("FATAL", msg)


# ============================================================
# TOKEN
# ============================================================

def get_token():
    if not os.path.exists(TOKEN_FILE):
        warn("Kein TOKEN_FILE gefunden.")
        return None
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


BOT_TOKEN = get_token()


# ============================================================
# TELEGRAM SENDEN
# ============================================================

def send_telegram_message(chat_id, text):
    if not chat_id or not BOT_TOKEN:
        warn("Konnte keine Telegram-Nachricht senden (fehlende chat_id oder BOT_TOKEN).")
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode("utf-8")
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10):
            pass
        info(f"Antwort an Telegram gesendet (Chat {chat_id}).")
    except Exception as e:
        error(f"[RÜCKKANAL] Fehler beim Senden: {e}")


# ============================================================
# CHAT-ID
# ============================================================

def speichere_chat_id(chat_id):
    if not chat_id:
        return
    try:
        with open(CHAT_ID_FILE, "w", encoding="utf-8") as f:
            f.write(str(chat_id))
        info(f"CHAT_ID gespeichert: {chat_id}")
    except Exception as e:
        warn(f"Konnte CHAT_ID nicht speichern: {e}")


def lade_chat_id():
    if not os.path.exists(CHAT_ID_FILE):
        return None
    try:
        with open(CHAT_ID_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except:
        return None


# ============================================================
# AUFGABEN VERARBEITEN
# ============================================================

def verarbeite_aufgabe(task: dict):
    befehl = task.get("befehl", "UNBEKANNT")
    text = task.get("text", "")
    chat_id = task.get("chat_id") or lade_chat_id()

    if chat_id:
        speichere_chat_id(chat_id)

    info(f"Neue Aufgabe: {befehl} | Text: {text} | Chat: {chat_id}")

    try:
        if befehl == "CHECK_SYSTEM":
            send_telegram_message(chat_id, "✅ System läuft stabil.")

        elif befehl == "KI_ANFRAGE":
            info("KI-Anfrage wird verarbeitet...")
            antwort = Logik.process_ki_anfrage(text)
            send_telegram_message(chat_id, antwort)

        elif befehl == "FABRIK":
            info("FABRIK-Befehl empfangen.")
            antwort = Logik.handle_fabrik_command(text)
            send_telegram_message(chat_id, antwort)

        else:
            warn(f"Unbekannter Befehl: {befehl}")
            send_telegram_message(chat_id, f"❓ Unbekannter Befehl: {befehl}")

    except Exception as e:
        msg = f"Fehler bei der Aufgabenverarbeitung ({befehl}): {e}"
        error(msg)
        send_telegram_message(chat_id, f"❌ {msg}")


# ============================================================
# HAUPTSCHLEIFE
# ============================================================

def main():
    info("Agent Worker gestartet (NEUE VERSION).")
    info(f"Geladene Logik.py: {Logik.__file__}")

    while True:
        try:
            if os.path.exists(AUFGABEN_DATEI) and os.path.getsize(AUFGABEN_DATEI) > 0:
                with open(AUFGABEN_DATEI, "r", encoding="utf-8") as f:
                    try:
                        tasks = json.load(f)
                    except json.JSONDecodeError as e:
                        error(f"JSON-Fehler in {AUFGABEN_DATEI}: {e}")
                        tasks = []

                if isinstance(tasks, list):
                    for task in tasks:
                        if isinstance(task, dict):
                            verarbeite_aufgabe(task)
                        else:
                            warn(f"Ungültiger Task-Eintrag: {task}")
                else:
                    warn("Aufgaben-Datei enthält kein List-Format.")

                with open(AUFGABEN_DATEI, "w", encoding="utf-8") as f:
                    json.dump([], f)

        except Exception as loop_error:
            fatal(f"Fehler in der Hauptschleife: {loop_error}")

        time.sleep(1)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    threading.Thread(target=auto_update_loop, daemon=True).start()
    main()
