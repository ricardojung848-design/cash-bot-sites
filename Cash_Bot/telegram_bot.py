import os
import time
from typing import Dict, Any, List

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from core.utils import (
    BASE_DIR,
    load_json,
    save_json,
    log_worker,
    error_worker,
)

AUFGABEN_DATEI = os.path.join(BASE_DIR, "aufgaben.json")
RUECKGABE_DATEI = os.path.join(BASE_DIR, "rueckgabe.json")

with open(os.path.join(BASE_DIR, "config", "token.txt"), "r") as f:
    TELEGRAM_BOT_TOKEN = f.read().strip()



def load_tasks() -> List[Dict[str, Any]]:
    tasks = load_json(AUFGABEN_DATEI, [])
    if not isinstance(tasks, list):
        tasks = []
        save_json(AUFGABEN_DATEI, tasks)
    return tasks


def save_tasks(tasks: List[Dict[str, Any]]) -> None:
    save_json(AUFGABEN_DATEI, tasks)


def add_task(chat_id: int, befehl: str, text: str) -> None:
    tasks = load_tasks()
    tasks.append({
        "chat_id": chat_id,
        "befehl": befehl,
        "text": text,
    })
    save_tasks(tasks)
    log_worker(f"Neue Aufgabe gespeichert: {befehl} | Chat {chat_id}")


def load_reply() -> Dict[str, Any]:
    data = load_json(RUECKGABE_DATEI, {})
    if not isinstance(data, dict):
        data = {}
    return data


def clear_reply() -> None:
    save_json(RUECKGABE_DATEI, {})


def wait_for_worker_answer(chat_id: int, timeout: float = 10.0, interval: float = 0.2) -> str:
    start = time.time()
    while time.time() - start < timeout:
        data = load_reply()
        if data.get("chat_id") == chat_id and "antwort" in data:
            antwort = data["antwort"]
            clear_reply()
            return antwort
        time.sleep(interval)
    return "Keine Antwort vom Worker erhalten."


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("DETO Cash Manager ist aktiv. Schreib mir einfach etwas.")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = "/help"

    await update.message.reply_text("'KI_ANFRAGE' empfangen. Worker verarbeitet...")

    add_task(chat_id, "KI_ANFRAGE", text)
    antwort = wait_for_worker_answer(chat_id)
    await update.message.reply_text(antwort)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    await update.message.reply_text("'KI_ANFRAGE' empfangen. Worker verarbeitet...")

    add_task(chat_id, "KI_ANFRAGE", text)
    antwort = wait_for_worker_answer(chat_id)
    await update.message.reply_text(antwort)


def main():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN fehlt in den Umgebungsvariablen.")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    log_worker("Telegram-Bot gestartet...")
    app.run_polling()
