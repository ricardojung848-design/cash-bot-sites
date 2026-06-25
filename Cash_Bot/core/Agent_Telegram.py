import sys
from pathlib import Path

# Sicherstellen, dass das Projekt-Hauptverzeichnis im Systempfad liegt.
# Dies verhindert Import-Fehler, wenn der Bot aus dem 'core'-Ordner heraus gestartet wird.
base_dir = Path(__file__).resolve().parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

# Einbindung des zentralen Loggers für den Start-Prozess
from doctor_core.logging import log_doctor

# Importiert die Hauptfunktion des eigentlichen Telegram-Bots
try:
    from telegram_bot import main
except ImportError as e:
    log_doctor(f"Agent_Telegram-Kritisch: Konnte 'telegram_bot.py' im Hauptverzeichnis nicht finden: {e}")
    sys.exit(1)


if __name__ == "__main__":
    log_doctor("Agent_Telegram: Starte Telegram-Bot-Schnittstelle...")
    try:
        main()
    except KeyboardInterrupt:
        log_doctor("Agent_Telegram: Telegram-Bot wurde manuell beendet.")
    except Exception as e:
        log_doctor(f"Agent_Telegram-Kritisch: Unerwarteter Absturz des Telegram-Bots: {e}")