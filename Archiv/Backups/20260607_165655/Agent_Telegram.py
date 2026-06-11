import json
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = "8982497382:AAEOsRO1HOrbJ2LE3BoD-W8Z1-WNnLZBZpc"
AUFGABEN_DATEI = "aufgaben.json"

def aufgabe_einreihen(chat_id, befehl, text):
    aufgabe = {"chat_id": chat_id, "befehl": befehl, "text": text}
    with open(AUFGABEN_DATEI, "a", encoding="utf-8") as f:
        f.write(json.dumps(aufgabe, ensure_ascii=False) + "\n")
    print(f"📥 [SPEICHER] Aufgabe '{befehl}' erfolgreich in aufgaben.json geschrieben.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text.strip()
    chat_id = update.effective_chat.id
    
    print(f"\n📩 [TELEGRAM] Neue Nachricht empfangen: '{user_text}'")

    # Text für den Abgleich vereinheitlichen (Großbuchstaben)
    user_text_upper = user_text.upper()

    # 1. System-Check direkt abfangen (mit oder ohne Slash)
    if user_text_upper == "CHECK_SYSTEM" or user_text_upper == "/CHECK_SYSTEM":
        print("🔍 [MATCH] System-Check erkannt!")
        await update.message.reply_text("🔍 System-Prüfung wird an den Worker übergeben...")
        aufgabe_einreihen(chat_id, "CHECK_SYSTEM", "CHECK_SYSTEM")
        return

    # 2. Architekt-Auftrag (/code, /architekt oder ARCHITEKT)
    elif user_text_upper.startswith("/CODE") or user_text_upper.startswith("ARCHITEKT"):
        print("🏗️ [MATCH] Architekt-Befehl erkannt!")
        if user_text_upper.startswith("/CODE"):
            anforderung = user_text[5:].strip()
        else:
            anforderung = user_text[9:].strip()
            
        await update.message.reply_text(f"🏗️ Architekt baut: {anforderung}")
        aufgabe_einreihen(chat_id, "ARCHITEKT", anforderung)
        return

    # 3. Ausführ-Auftrag (/run oder RUN)
    elif user_text_upper.startswith("/RUN") or user_text_upper.startswith("RUN"):
        print("🚀 [MATCH] Run-Befehl erkannt!")
        if user_text_upper.startswith("/RUN"):
            modul = user_text[4:].strip()
        else:
            modul = user_text[3:].strip()
            
        await update.message.reply_text(f"🚀 Starte Modul: {modul}")
        aufgabe_einreihen(chat_id, "RUN", modul)
        return

    # 4. Andere Standard-Befehle (Fallbacks)
    if user_text_upper.startswith("/RECHNUNG"): befehl = "RECHNUNG"
    elif user_text_upper.startswith("/MEIN_WALLET"): befehl = "WALLET_STATUS"
    elif user_text_upper.startswith("/EINZAHLUNG"): befehl = "EINZAHLUNG"
    elif user_text_upper.startswith("/LOG"): befehl = "LOGBUCH"
    elif user_text_upper.startswith("/EXPORT"): befehl = "EXPORT"
    else: 
        befehl = "KI_ANFRAGE"
        print(f"🤖 [FALLBACK] Keine direkte Zuweisung. Verarbeite als standard {befehl}")
        
    aufgabe_einreihen(chat_id, befehl, user_text)

def main():
    print("==============================================")
    print("🤖 TELEGRAM-BOT WIRD GESTARTET...")
    print("📡 Lausche auf Telegram-Nachrichten...")
    print("==============================================")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()