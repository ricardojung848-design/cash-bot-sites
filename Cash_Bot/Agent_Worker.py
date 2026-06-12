import json
import os
import time
import datetime
import urllib.request
import urllib.parse
import Logik
import gspread
from oauth2client.service_account import ServiceAccountCredentials

AUFGABEN_DATEI = "aufgaben.json"
CHAT_ID_FILE = "last_chat_id.txt"
TOKEN_FILE = "token.txt"
CREDENTIALS_FILE = "credentials.json"
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


def log(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(os.path.join(LOG_DIR, "worker.log"), "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass


def get_token():
    if not os.path.exists(TOKEN_FILE):
        log("⚠️ Kein TOKEN_FILE gefunden.")
        return None
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


BOT_TOKEN = get_token()


def send_telegram_message(chat_id, text):
    if not chat_id or not BOT_TOKEN:
        log("⚠️ Konnte keine Telegram-Nachricht senden (fehlende chat_id oder BOT_TOKEN).")
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = urllib.parse.urlencode(
            {"chat_id": chat_id, "text": text}
        ).encode("utf-8")
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10):
            pass
    except Exception as e:
        log(f"❌ [RÜCKKANAL] Fehler beim Senden: {e}")


def speichere_chat_id(chat_id):
    if not chat_id:
        return
    try:
        with open(CHAT_ID_FILE, "w", encoding="utf-8") as f:
            f.write(str(chat_id))
    except Exception as e:
        log(f"⚠️ Konnte CHAT_ID nicht speichern: {e}")


def lade_chat_id():
    if not os.path.exists(CHAT_ID_FILE):
        return None
    try:
        with open(CHAT_ID_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except:
        return None


def verarbeite_fabrik_sheet(chat_id):
    """
    Liest das Google Sheet 'CashBot_Trends',
    sucht Zeilen mit Status 'Offen' und verarbeitet jede Zeile einzeln.
    Erwartet in Logik.py: fabrik_prozess_einzeltask(thema)
    """
    send_telegram_message(chat_id, "🏭 Fabrik gestartet... lese Google Sheet...")

    try:
        scope = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE, scope
        )
        gc = gspread.authorize(creds)
        sheet = gc.open("CashBot_Trends").sheet1
        records = sheet.get_all_records()

        offene_indices = [
            i for i, r in enumerate(records, start=2) if r.get("Status") == "Offen"
        ]

        if not offene_indices:
            send_telegram_message(chat_id, "ℹ️ Keine offenen Themen im Sheet.")
            return

        for row_index in offene_indices:
            row = records[row_index - 2]
            thema = row.get("Thema", "").strip()
            if not thema:
                log(f"⚠️ Zeile {row_index} hat kein 'Thema'. Übersprungen.")
                continue

            send_telegram_message(chat_id, f"📝 Generiere Artikel für: {thema}")
            log(f"Starte Fabrik-Einzelprozess für Thema: {thema}")

            try:
                ergebnis = Logik.fabrik_prozess_einzeltask(thema)
            except AttributeError:
                ergebnis = "❌ Logik.fabrik_prozess_einzeltask() existiert nicht."
            except Exception as e:
                ergebnis = f"❌ Fehler im Fabrik-Einzelprozess: {e}"

            send_telegram_message(chat_id, ergebnis)

            if "❌" not in ergebnis:
                try:
                    sheet.update_cell(row_index, 2, "Live")  # Spalte B = Status
                    log(f"✅ Thema '{thema}' auf 'Live' gesetzt (Zeile {row_index}).")
                except Exception as e:
                    log(f"⚠️ Konnte Status im Sheet nicht aktualisieren: {e}")

        send_telegram_message(chat_id, "🚀 Fabrik-Durchlauf abgeschlossen.")

    except Exception as e:
        msg = f"❌ Fabrik-Fehler (Sheet): {e}"
        log(msg)
        send_telegram_message(chat_id, msg)


def verarbeite_aufgabe(task: dict):
    befehl = task.get("befehl", "UNBEKANNT")
    text = task.get("text", "")
    chat_id = task.get("chat_id") or lade_chat_id()

    if chat_id:
        speichere_chat_id(chat_id)

    log(f"📥 Neue Aufgabe: {befehl} | Text: {text} | Chat: {chat_id}")

    try:
        if befehl == "CHECK_SYSTEM":
            antwort = Logik.check_system() if hasattr(Logik, "check_system") else "✅ System läuft."
            send_telegram_message(chat_id, antwort)

        elif befehl == "KI_ANFRAGE":
            antwort = Logik.ki_anfrage_verarbeiten(text)
            send_telegram_message(chat_id, antwort)

        elif befehl == "FABRIK":
            verarbeite_fabrik_sheet(chat_id)

        else:
            send_telegram_message(chat_id, f"❓ Unbekannter Befehl: {befehl}")
            log(f"Unbekannter Befehl empfangen: {befehl}")

    except Exception as e:
        msg = f"❌ Fehler bei der Aufgabenverarbeitung ({befehl}): {e}"
        log(msg)
        send_telegram_message(chat_id, msg)


def main():
    log("🤖 Agent Worker gestartet (optimierte Version).")
    while True:
        try:
            if os.path.exists(AUFGABEN_DATEI) and os.path.getsize(AUFGABEN_DATEI) > 0:
                with open(AUFGABEN_DATEI, "r", encoding="utf-8") as f:
                    try:
                        tasks = json.load(f)
                    except json.JSONDecodeError as e:
                        log(f"❌ JSON-Fehler in {AUFGABEN_DATEI}: {e}")
                        tasks = []

                if isinstance(tasks, list):
                    for task in tasks:
                        if isinstance(task, dict):
                            verarbeite_aufgabe(task)
                        else:
                            log(f"⚠️ Ungültiger Task-Eintrag: {task}")
                else:
                    log("⚠️ Aufgaben-Datei enthält kein List-Format.")

                with open(AUFGABEN_DATEI, "w", encoding="utf-8") as f:
                    json.dump([], f)

        except Exception as loop_error:
            log(f"❌ Fehler in der Hauptschleife: {loop_error}")

        time.sleep(2)


if __name__ == "__main__":
    main()
