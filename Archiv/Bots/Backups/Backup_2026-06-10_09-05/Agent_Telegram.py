import json
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- HIER DEINEN ECHTEN TOKEN EINFÜGEN ---
TELEGRAM_TOKEN = "8982497382:AAHwEjHiw4J78rxYzApGfptINWEZemd6J3Y"
AUFGABEN_DATEI = "aufgaben.json"

def aufgabe_einreihen(chat_id, befehl, text):
    """Liest die Datei, fügt die neue Aufgabe zur Liste hinzu und überschreibt die Datei."""
    aufgabe = {"chat_id": chat_id, "befehl": befehl, "text": text}
    tasks = []
    
    # 1. Bestehende Aufgaben sicher laden
    if os.path.exists(AUFGABEN_DATEI) and os.path.getsize(AUFGABEN_DATEI) > 0:
        try:
            with open(AUFGABEN_DATEI, "r", encoding="utf-8") as f:
                tasks = json.load(f)
        except json.JSONDecodeError:
            tasks = []

    # 2. Neue Aufgabe anhängen
    tasks.append(aufgabe)
    
    # 3. Datei überschreiben
    with open(AUFGABEN_DATEI, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)
    print(f"📥 [SPEICHER] Aufgabe '{befehl}' erfolgreich eingereiht.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_text = update.message.text.strip()
    chat_id = update.effective_chat.id
    
    # Befehls-Logik
    u = user_text.upper()
    if u == "/CHECK_SYSTEM": b = "CHECK_SYSTEM"
    elif u.startswith(("/CODE", "ARCHITEKT")): b = "ARCHITEKT"
    elif u.startswith(("/RUN", "RUN")): b = "RUN"
    elif u.startswith("/LOG"): b = "LOGBUCH"
    else: b = "KI_ANFRAGE"
        
    aufgabe_einreihen(chat_id, b, user_text)
    await update.message.reply_text(f"✅ Befehl '{b}' empfangen.")

def main():
    print("🤖 Telegram Bot wird gestartet...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()