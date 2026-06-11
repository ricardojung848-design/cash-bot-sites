import os, json, asyncio, ollama, importlib.util, glob, sys
import importlib
from telegram import Bot
import Agent_Architekt
import Agent_Wächter
from Agent_Wallet_Auto import init_wallet

# --- KONFIGURATION ---
TELEGRAM_TOKEN = "8982497382:AAEOsRO1HOrbJ2LE3BoD-W8Z1-WNnLZBZpc"
AUFGABEN_DATEI = "aufgaben.json"
bot = Bot(token=TELEGRAM_TOKEN)
init_wallet()

async def verarbeite_aufgabe(aufgabe):
    chat_id, befehl, user_text = aufgabe["chat_id"], aufgabe["befehl"], aufgabe["text"]
    try:
        # Import erzwingen, falls sich die Datei geändert hat
        importlib.reload(Agent_Wächter)
        
        if befehl == "ARCHITEKT":
            print(f"🏗️ [WORKER] Starte Architekt für: {user_text}")
            res = ollama.generate(model="deto_agent", prompt=f"Erstelle Python Modul für: {user_text}. Nur Code.")
            code = res['response'].replace('```python', '').replace('```', '').strip()
            name = f"Modul_{user_text.split()[0]}"
            Agent_Architekt.architekt_erstelle_modul(name, code)
            await bot.send_message(chat_id=chat_id, text=f"✅ {name} erstellt.")

        elif befehl == "RUN":
            print(f"🚀 [WORKER] Führe Modul aus: {user_text}")
            name = user_text.strip()
            pfad = f"Module/{name}.py"
            
            valide, fehler = Agent_Wächter.validate_code_syntax(pfad)
            
            if not valide:
                await bot.send_message(chat_id=chat_id, text=f"⚠️ Modul defekt: {fehler}")
                Agent_Architekt.architekt_repariere_modul(name, fehler)
                await bot.send_message(chat_id=chat_id, text="✅ Reparatur versucht.")
            
            spec = importlib.util.spec_from_file_location(name, pfad)
            modul = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(modul)
            await bot.send_message(chat_id=chat_id, text=str(modul.run_modul()))

        elif befehl == "CHECK_SYSTEM":
            print("🔍 [WORKER] Führe System-Check aus...")
            module = glob.glob("Module/*.py")
            meldungen = []
            for m in module:
                valide, fehler = Agent_Wächter.validate_code_syntax(m)
                name = os.path.basename(m).replace(".py", "")
                meldungen.append(f"✅ {name}: OK" if valide else f"❌ {name}: DEFEKT")
            await bot.send_message(chat_id=chat_id, text="🔍 System-Status:\n" + "\n".join(meldungen))

        # === HIER IST DEIN NEUES SPRACHMODUL ===
        elif befehl == "KI_ANFRAGE":
            print(f"🤖 [WORKER] Sende Chat-Anfrage an deto_agent: '{user_text}'")
            
            # Direktes Streaming oder Generierung über deine lokale Ollama-Instanz
            res = ollama.generate(model="deto_agent", prompt=user_text)
            antwort = res['response'].strip()
            
            if antwort:
                await bot.send_message(chat_id=chat_id, text=antwort)
            else:
                await bot.send_message(chat_id=chat_id, text="🤖 Mein lokales Gehirn hat keine Antwort geliefert.")

    except Exception as e:
        print(f"❌ [WORKER FEHLER] {str(e)}")
        await bot.send_message(chat_id=chat_id, text=f"❌ Fehler: {str(e)}")

async def main_worker():
    print("==============================================")
    print("🚀 WORKER AKTIV - Überwache Aufgaben...")
    print("📡 Warte auf Befehle oder Chat-Eingaben...")
    print("==============================================")
    while True:
        if os.path.exists(AUFGABEN_DATEI):
            with open(AUFGABEN_DATEI, "r", encoding="utf-8") as f: 
                lines = f.readlines()
            if lines:
                try:
                    aufgabe = json.loads(lines[0].strip())
                    await verarbeite_aufgabe(aufgabe)
                    with open(AUFGABEN_DATEI, "w", encoding="utf-8") as f: 
                        f.writelines(lines[1:])
                except Exception as e: 
                    print(f"Queue Fehler: {e}")
        await asyncio.sleep(1)

if __name__ == '__main__':
    try: 
        asyncio.run(main_worker())
    except Exception as e:
        print(f"🚨 KRITISCHER FEHLER: {e}")
        input("Drücke Enter...")