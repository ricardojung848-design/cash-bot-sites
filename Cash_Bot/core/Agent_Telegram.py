# core/Agent_Telegram.py
# Diese Datei startet NUR den echten Telegram-Bot
# Kein Auto-Restart, keine Schleifen, keine Token-Probleme

from telegram_bot import main

if __name__ == "__main__":
    main()
