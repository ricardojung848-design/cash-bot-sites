import time
import json
import traceback
import requests
import Logik
import os
from datetime import datetime

# === TELEGRAM BOT TOKEN LADEN ===
with open("telegram_config.json", "r", encoding="utf-8") as f:
    TELEGRAM = json.load(f)

BOT_TOKEN = TELEGRAM["bot_token"]
CHAT_ID = TELEGRAM["chat_id"]
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# === LOGGING ===
def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} {msg}")

# === DEBUG: PFAD + VERSION AUSGEBEN ===
def debug_startup_info():
    log("=== DEBUG STARTUP INFO ===")
    log(f"Arbeitsverzeichnis: {os.getcwd()}")
    log(f"Geladene Logik.py: {Logik.__file__}")
    if hasattr(Logik, "LOGIK_VERSION"):
        log(f"Logik-Version: {Logik.LOGIK_VERSION}")
    else:
        log("⚠️ Logik-Version NICHT gefunden (LOGIK_VERSION fehlt)")
    log("==========================")

# === TELEGRAM SENDEN ===
def send_message(text):
    try:
        requests.post(API_URL, json={"chat_id": CHAT_ID, "text": text})
    except Exception as e:
        log(f"❌ Fehler beim Senden an Telegram: {e}")

# === HAUPTVERARBEITUNG ===
def verarbeite_ki_anfrage(text, chat_id):
    try:
        antwort = Logik.process_ki_anfrage(text)
        send_message(antwort)
    except Exception as e:
        fehler = traceback.format_exc()
        log(f"❌ Fehler bei der Aufgabenverarbeitung (KI_ANFRAGE): {e}")
        send_message(f"❌ Fehler in KI-Anfrage:\n{e}\n\n{fehler}")

# === TELEGRAM LISTENER ===
def telegram_listener():
    last_update_id = None
    log("Telegram-Listener läuft und hört zu...")

    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            if last_update_id:
                url += f"?offset={last_update_id + 1}"

            res = requests.get(url).json()

            if "result" in res:
                for update in res["result"]:
                    last_update_id = update["update_id"]

                    if "message" in update:
                        msg = update["message"]
                        chat_id = msg["chat"]["id"]

                        if "text" in msg:
                            text = msg["text"]
                            log(f"Neue Aufgabe: KI_ANFRAGE | Text: {text} | Chat: {chat_id}")
                            verarbeite_ki_anfrage(text, chat_id)

        except Exception as e:
            log(f"❌ Listener-Fehler: {e}")
            time.sleep(2)

        time.sleep(0.5)

# === START ===
if __name__ == "__main__":
    log("Agent Worker gestartet (optimierte Version).")
    debug_startup_info()
    telegram_listener()
