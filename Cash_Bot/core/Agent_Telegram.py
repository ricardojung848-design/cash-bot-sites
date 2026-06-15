import os
import json
import time
import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# === interne Utils ===
from core.utils import (
    BASE_DIR,
    CONFIG_DIR,
    LOGS_DIR,
    load_json,
    save_json,
    log_telegram,
    warn_telegram,
    error_telegram,
)

# === PFAD ZU TOKEN & RÜCKGABE ===
TOKEN_FILE = os.path.join(CONFIG_DIR, "token.txt")
AUFGABEN_DATEI = os.path.join(BASE_DIR, "aufgaben.json")
RUECKGABE_DATEI = os.path.join(BASE_DIR, "rueckgabe.json")


# === TOKEN LADEN ===
def get_token():
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        error_telegram(f"token.txt wurde nicht gefunden! Gesucht unter: {TOKEN_FILE}")
        exit()


TELEGRAM_TOKEN = get_token()


# === AUFGABEN EINREIHEN ===
def aufgabe_einreihen(chat_id, befehl, text):
    tasks = load_json(AUFGABEN_DATEI, [])
    tasks.append({"chat_id": chat_id, "befehl": befehl, "text": text})
    save_json(AUFGABEN_DATEI, tasks)
    log_telegram(f"Aufgabe eingereiht: {befehl} | Chat {chat_id}")


# === NACHRICHTEN VERARBEITEN ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text.strip()
    chat_id = update.effective_chat.id

    log_telegram(f"Nachricht empfangen: '{user_text}' von Chat {chat_id}")

    u = user_text.upper()

    if u == "/CHECK_SYSTEM":
        b = "CHECK_SYSTEM"
    elif u.startswith(("/CODE", "ARCHITEKT")):
        b = "ARCHITEKT"
    elif u.startswith(("/RUN", "RUN")):
        b = "RUN"
    elif u.startswith("/LOG"):
        b = "LOGBUCH"
    else:
        b = "KI_ANFRAGE"

    aufgabe_einreihen(chat_id, b, user_text)

    await update.message.reply_text(f"⏳ Befehl '{b}' empfangen. Worker verarbeitet...")
    log_telegram(f"Antwort an Chat {chat_id} gesendet.")


# === RÜCKKANAL: ANTWORTEN AUTOMATISCH SENDEN ===
async def rueckkanal_loop(app: Application):
    last_response = None

    while True:
        data = load_json(RUECKGABE_DATEI, {})

        if data and data != last_response:
            chat_id = data.get("chat_id")
            antwort = data.get("antwort")

            if chat_id and antwort:
                try:
                    await app.bot.send_message(chat_id=chat_id, text=antwort)
                    log_telegram(f"Antwort an Chat {chat_id} gesendet: {antwort}")

                    # Datei leeren
                    save_json(RUECKGABE_DATEI, {})
                except Exception as e:
                    error_telegram(f"Fehler beim Senden der Antwort: {e}")

            last_response = data

        await asyncio.sleep(0.3)


# === MAIN LOOP ===
import asyncio

def main():
    log_telegram("Telegram Listener wird gestartet...")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Listener für eingehende Nachrichten
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Rückkanal starten
    app.job_queue.run_repeating(lambda ctx: asyncio.create_task(rueckkanal_loop(app)), interval=0.3)

    log_telegram("Telegram Listener läuft und hört zu...")

    app.run_polling()


if __name__ == "__main__":
    main()
