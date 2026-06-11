import json
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- 1. Konfiguration & Token-Management ---
def get_token():
    try:
        # Sucht im aktuellen Ordner nach der token.txt
        with open("token.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("❌ FEHLER: token.txt wurde im Ordner nicht gefunden!")
        exit()

TELEGRAM_TOKEN = get_token()
AUFGABEN_DATEI = "aufgaben.json"

# --- 2. Warteschlange (Queueing) ---
def aufgabe_einreihen(chat_id, befehl, text):
    """Liest die Datei, fügt die neue Aufgabe hinzu und speichert sie."""
    aufgabe = {"chat_id": chat_id, "befehl": befehl, "text": text}
    tasks = []
    
    # Bestehende Aufgaben sicher laden
    if os.path.exists(AUFGABEN_DATEI) and os.path.getsize(AUFGABEN_DATEI) > 0:
        try:
            with open(AUFGABEN_DATEI, "r", encoding="utf-8") as f:
                tasks = json.load(f)
        except json.JSONDecodeError:
            tasks = []

    # Neue Aufgabe anhängen
    tasks.append(aufgabe)
    
    # Datei überschreiben
    with open(AUFGABEN_DATEI, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)
    
    print(f"📥 [SPEICHER] Aufgabe '{befehl}' erfolgreich für Chat {chat_id} eingereiht.")

# --- 3. Nachrichten-Verarbeitung ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: 
        return
    
    user_text = update.message.text.strip()
    chat_id = update.effective_chat.id
    
    # Befehls-Erkennung (Routing)
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
        
    # Aufgabe in die JSON-Datei schreiben
    aufgabe_einreihen(chat_id, b, user_text)
    
    # Feedback an Telegram
    await update.message.reply_text(f"✅ Befehl '{b}' empfangen und in Bearbeitung.")

# --- 4. Main Loop ---
def main():
    print("🤖 Telegram Bot wird gestartet...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # FILTER: Wir nutzen nur noch 'filters.TEXT' ohne Command-Einschränkung,
    # damit /check_system und alle anderen Befehle sicher ankommen.
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    print("👂 Telegram-Listener läuft und hört zu...")
    app.run_polling()

if __name__ == '__main__':
    main()