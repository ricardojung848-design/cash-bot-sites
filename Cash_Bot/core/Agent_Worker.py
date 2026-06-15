import os
import time
import json
import threading
import datetime
import urllib.request
import urllib.parse

from . import Logik
from . import updater
from .utils import (
    BASE_DIR,
    CONFIG_DIR,
    info_worker,
    warn_worker,
    error_worker,
    fatal_worker,
    load_json,
    save_json,
)

# =========================
# Pfade & Dateien
# =========================

AUFGABEN_DATEI = os.path.join(BASE_DIR, "aufgaben.json")
TOKEN_FILE = os.path.join(CONFIG_DIR, "token.txt")
CHAT_ID_FILE = os.path.join(CONFIG_DIR, "telegram_chat_id.json")


# =========================
# Token / Telegram
# =========================

def get_token():
    if not os.path.exists(TOKEN_FILE):
        warn_worker(f"Kein TOKEN_FILE gefunden: {TOKEN_FILE}")
        return None
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        warn_worker(f"Konnte TOKEN_FILE nicht lesen: {e}")
        return None


BOT_TOKEN = get_token()


def send_telegram_message(chat_id, text):
    if not chat_id or not BOT_TOKEN:
        warn_worker("Konnte keine Telegram-Nachricht senden (fehlende chat_id oder BOT_TOKEN).")
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode("utf-8")
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10):
            pass
        info_worker(f"Antwort an Telegram gesendet (Chat {chat_id}).")
    except Exception as e:
        error_worker(f"[RÜCKKANAL] Fehler beim Senden: {e}")


# =========================
# Chat-ID speichern / laden
# =========================

def speichere_chat_id(chat_id):
    if not chat_id:
        return
    try:
        data = {"chat_id": str(chat_id)}
        save_json(CHAT_ID_FILE, data)
        info_worker(f"CHAT_ID gespeichert: {chat_id}")
    except Exception as e:
        warn_worker(f"Konnte CHAT_ID nicht speichern: {e}")


def lade_chat_id():
    data = load_json(CHAT_ID_FILE, default={})
    return data.get("chat_id")


# =========================
# Aufgaben verarbeiten
# =========================

def verarbeite_aufgabe(task: dict):
    befehl = task.get("befehl", "UNBEKANNT")
    text = task.get("text", "")
    chat_id = task.get("chat_id") or lade_chat_id()

    if chat_id:
        speichere_chat_id(chat_id)

    info_worker(f"Neue Aufgabe: {befehl} | Text: {text} | Chat: {chat_id}")

    try:
        if befehl == "CHECK_SYSTEM":
            send_telegram_message(chat_id, "✅ DetoBot-System läuft stabil.")

        elif befehl == "KI_ANFRAGE":
            info_worker("KI-Anfrage wird verarbeitet...")
            antwort = Logik.process_ki_anfrage(text)
            send_telegram_message(chat_id, antwort)

        elif befehl == "FABRIK":
            info_worker("FABRIK-Befehl empfangen.")
            antwort = Logik.handle_fabrik_command(text)
            send_telegram_message(chat_id, antwort)

        else:
            warn_worker(f"Unbekannter Befehl: {befehl}")
            send_telegram_message(chat_id, f"❓ Unbekannter Befehl: {befehl}")

    except Exception as e:
        msg = f"Fehler bei der Aufgabenverarbeitung ({befehl}): {e}"
        error_worker(msg)
        if chat_id:
            send_telegram_message(chat_id, f"❌ {msg}")


# =========================
# Hauptschleife
# =========================

def main():
    info_worker("DetoBot Agent Worker gestartet.")
    info_worker(f"Geladene Logik.py: {Logik.__file__}")

    while True:
        try:
            if os.path.exists(AUFGABEN_DATEI) and os.path.getsize(AUFGABEN_DATEI) > 0:
                with open(AUFGABEN_DATEI, "r", encoding="utf-8") as f:
                    try:
                        tasks = json.load(f)
                    except json.JSONDecodeError as e:
                        error_worker(f"JSON-Fehler in {AUFGABEN_DATEI}: {e}")
                        tasks = []

                if isinstance(tasks, list):
                    for task in tasks:
                        if isinstance(task, dict):
                            verarbeite_aufgabe(task)
                        else:
                            warn_worker(f"Ungültiger Task-Eintrag: {task}")
                else:
                    warn_worker("Aufgaben-Datei enthält kein List-Format.")

                with open(AUFGABEN_DATEI, "w", encoding="utf-8") as f:
                    json.dump([], f)

        except Exception as loop_error:
            fatal_worker(f"Fehler in der Hauptschleife: {loop_error}")

        time.sleep(1)


# =========================
# Start
# =========================

if __name__ == "__main__":
    # Updater im Hintergrund
    threading.Thread(target=updater.auto_update_loop, daemon=True).start()
    main()
