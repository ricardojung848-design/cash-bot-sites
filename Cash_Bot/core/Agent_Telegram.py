import os
import json
import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# === interne Utils laden ===
from core.utils import (
    BASE_DIR,
    CONFIG_DIR,
    LOGS_DIR,
    info_telegram,
    warn_telegram,
    error_telegram,
)

# === Pfade ===
TOKEN_FILE = os.path.join(CONFIG_DIR, "token.txt")
AUFGABEN_DATEI = os.path.join(BASE_DIR, "aufgaben.json")
TELEGRAM_LOG = os.path.join(LOGS_DIR, "telegram.log")


# === TOKEN LADEN ===
def get_token():
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            token = f.read().strip()
            if not token:
                error_telegram("token.txt ist leer!")
                exit()
            return token
    except FileNotFoundError:
        error_telegram(f"token.txt wurde nicht gefunden! Gesucht unter: {TOKEN_FILE}")
        exit()


TELEGRAM_TOKEN = get_token()


# === AUFGABEN IN QUEUE SCHREIBEN ===
def aufgabe_einreihen(chat_id, befehl, text):
    aufgabe = {"chat_id": chat_id, "befehl": befehl, "text": text}
    tasks = []

    if os.path.exists(AUFGABEN_DATEI) and os.path.getsize(AUFGABEN_DATEI) > 0:
        try:
            with open(AUFGABEN_DATEI, "r", encoding="utf-8") as f:
                tasks = json.load(f)
        except json.JSONDecodeError:
            warn_telegram("Konnte Aufgaben-Datei nicht lesen – JSON fehlerhaft.")
            tasks = []

    tasks.append(aufgabe)

    with open(AUFGABEN_DATEI, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)

    info_telegram(f"Aufgabe eingereiht: {befehl} | Chat {chat_id}")


# === NACHRICHTEN VERARBEITEN ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or