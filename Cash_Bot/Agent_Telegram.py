import json
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import datetime

# === LOGGING ===
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "telegram.log")
MAX_LOG_SIZE = 2 * 1024 * 1024  # 2 MB

os.makedirs(LOG_DIR, exist_ok=True)

def rotate_log():
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_LOG_SIZE:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = f"telegram_{ts}.log"
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


# === TOKEN LADEN ===
def get_token():
    try:
        with open("token.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        error("token.txt wurde nicht gefunden!")
        exit()

TELEGRAM_TOKEN = get_token()
AUFGABEN_DATEI = "aufgaben.json"


# === AUFGABEN IN QUEUE SCHREIBEN ===
def aufgabe_einreihen(chat_id, befehl, text):
    aufgabe = {"chat_id": chat_id, "befehl": befehl, "text": text}
    tasks = []

    if os.path.exists(AUFGABEN_DATEI) and os.path.getsize(AUFGABEN_DATEI) > 0:
        try:
            with open(AUFGABEN_DATEI, "r", encoding="utf-8") as f:
                tasks = json.load(f)
        except json.JSONDecodeError:
            warn("Konnte Aufgaben-Datei nicht lesen – JSON fehlerhaft.")
            tasks = []

    tasks.append(aufgabe)

    with open(AUFGABEN_DATEI, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)

    info(f"Aufgabe eingereiht: {befehl} | Chat {chat_id}")


# === NACHRICHTEN VERARBEITEN ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text.strip()
    chat_id = update.effective_chat.id

    info(f"Nachricht empfangen: '{user_text}' von Chat {chat_id}")

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

    await update.message.reply_text(f"✅ Befehl '{b}' empfangen und in Bearbeitung.")
    info(f"Antwort an Chat {chat_id} gesendet.")


# === MAIN LOOP ===
def main():
    info("Telegram Listener wird gestartet...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    info("Telegram Listener läuft und hört zu...")
    app.run_polling()


if __name__ == "__main__":
    main()
