import json
import os
import time
import datetime
import urllib.request
import urllib.parse
import Logik
import gspread
from oauth2client.service_account import ServiceAccountCredentials

AUFGABEN_DATEI = 'aufgaben.json'
CHAT_ID_FILE = "last_chat_id.txt"
TOKEN_FILE = "token.txt"
CREDENTIALS_FILE = "credentials.json"

def get_token():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r") as f:
        return f.read().strip()

BOT_TOKEN = get_token()

def send_telegram_message(chat_id, text):
    if not chat_id: return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': chat_id, 'text': text}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req) as response:
            pass
    except Exception as e:
        print(f"❌ [RÜCKKANAL] Fehler: {e}")

def verarbeite_fabrik(chat_id):
    """Die neue Logik: Holt Daten aus Sheets und baut Content."""
    send_telegram_message(chat_id, "🏭 Fabrik gestartet... Analysiere Google Sheet...")
    
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        gc = gspread.authorize(creds)
        sheet = gc.open("CashBot_Trends").sheet1
        records = sheet.get_all_records()
        
        offene_themen = [i for i, r in enumerate(records, start=2) if r.get("Status") == "Offen"]
        
        if not offene_themen:
            send_telegram_message(chat_id, "ℹ️ Keine neuen Änderungen (nichts 'Offen' im Sheet).")
            return

        for index in offene_themen:
            thema = records[index-2].get("Thema")
            send_telegram_message(chat_id, f"📝 Generiere Artikel: {thema}...")
            
            # Hier greifen wir auf deine Logik zu
            # Wir nehmen an, Logik.generate_article existiert oder wir nutzen den Flow:
            ergebnis = Logik.fabrik_prozess_einzeltask(thema) 
            
            sheet.update_cell(index, 2, "Live")
            send_telegram_message(chat_id, f"✅ Fertig: {thema} ist jetzt live!")
            
        send_telegram_message(chat_id, "🚀 Alle Aufgaben abgeschlossen!")
        
    except Exception as e:
        send_telegram_message(chat_id, f"❌ Fabrik-Fehler: {str(e)}")

def verarbeite_aufgabe(task):
    befehl = task.get('befehl', 'UNBEKANNT')
    text = task.get('text', '')
    chat_id = task.get('chat_id')
    
    if chat_id:
        with open(CHAT_ID_FILE, "w", encoding="utf-8") as f:
            f.write(str(chat_id))

    if befehl == "CHECK_SYSTEM":
        send_telegram_message(chat_id, Logik.check_system())
    elif befehl == "KI_ANFRAGE":
        send_telegram_message(chat_id, Logik.ki_anfrage_verarbeiten(text))
    elif befehl == "FABRIK":
        verarbeite_fabrik(chat_id)
    else:
        send_telegram_message(chat_id, f"❓ Unbekannter Befehl: {befehl}")

def main():
    print("🤖 Agent Worker läuft (mit Fabrik-Modus)...")
    while True:
        if os.path.exists(AUFGABEN_DATEI) and os.path.getsize(AUFGABEN_DATEI) > 0:
            try:
                with open(AUFGABEN_DATEI, 'r', encoding='utf-8') as f:
                    tasks = json.load(f)
                if isinstance(tasks, list):
                    for task in tasks:
                        verarbeite_aufgabe(task)
                with open(AUFGABEN_DATEI, 'w', encoding='utf-8') as f:
                    json.dump([], f)
            except Exception as e:
                print(f"❌ Fehler: {e}")
        time.sleep(2)

if __name__ == "__main__":
    main()