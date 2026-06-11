import os, json, asyncio, ollama, importlib.util, glob, sys
import importlib
import shutil
from datetime import datetime
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
            # Bestimme das erste Wort (z.B. "Agent_Worker" oder "OrdnerCleaner")
            target_name = user_text.split()[0].strip()
            
            # PRÜFUNG: Handelt es sich um ein Core-Update?
            if target_name.startswith("Agent_") and os.path.exists(f"{target_name}.py"):
                print(f"🔄 [CORE UPDATE] Starte Selbsterneuerung für {target_name}.py...")
                await bot.send_message(chat_id=chat_id, text=f"🔄 Core-Update für `{target_name}.py` erkannt. Starte automatische Sicherung...")
                
                # 1. Automatisches Sicherheits-Backup vor dem Eingriff
                backup_dir = "./Backups"
                zeitstempel = datetime.now().strftime("%Y%m%d_%H%M%S")
                aktueller_backup_pfad = os.path.join(backup_dir, zeitstempel)
                os.makedirs(aktueller_backup_pfad, exist_ok=True)
                shutil.copy(f"{target_name}.py", os.path.join(aktueller_backup_pfad, f"{target_name}.py"))
                
                # 2. Bestehenden Code einlesen, damit die KI weiß, was sie modifiziert
                with open(f"{target_name}.py", "r", encoding="utf-8") as f:
                    aktueller_code = f.read()
                
                await bot.send_message(chat_id=chat_id, text=f"🧠 Übermittle aktuellen Code an deto_agent für die Modifikation...")
                
                # 3. Präzisen Prompt an Ollama senden
                prompt = (
                    f"Du bist das Gehirn dieses Agentensystems. Du sollst dich selbst updaten.\n"
                    f"Hier ist der aktuelle Code von {target_name}.py:\n\n"
                    f"{aktueller_code}\n\n"
                    f"Anweisung des Users für das Update: {user_text}\n\n"
                    f"Gib den VOLLSTÄNDIGEN, modifizierten Code zurück. "
                    f"NUR Code, kein Markdown, kein Erklärtext, kein ```python."
                )
                
                res = ollama.generate(model="deto_agent", prompt=prompt)
                neu_code = res['response'].replace('```python', '').replace('```', '').strip()
                
                # 4. Sicherheits-Check: Syntax prüfen, bevor wir überschreiben!
                temp_pfad = f"{target_name}_temp.py"
                with open(temp_pfad, "w", encoding="utf-8") as f:
                    f.write(neu_code)
                    
                valide, fehler = Agent_Wächter.validate_code_syntax(temp_pfad)
                if not valide:
                    os.remove(temp_pfad)
                    print(f"❌ [CORE UPDATE ABGEBROCHEN] Syntax-Fehler generiert!")
                    await bot.send_message(chat_id=chat_id, text=f"❌ Core-Update abgebrochen! Der generierte Code hat einen Syntax-Fehler:\n`{fehler}`")
                    return
                
                # 5. Überschreiben der echten Datei, da Code valide ist
                os.remove(temp_pfad)
                with open(f"{target_name}.py", "w", encoding="utf-8") as f:
                    f.write(neu_code)
                
                await bot.send_message(chat_id=chat_id, text=f"✅ {target_name}.py erfolgreich mutiert! Führe Live-System-Neustart aus...")
                print(f"♻️ [LIVE RELOAD] Starte Worker-Prozess neu, um Änderungen anzuwenden...")
                
                # 6. Der Zaubertrick: Prozess im CMD-Fenster live austauschen und neu laden
                os.execv(sys.executable, [sys.executable] + sys.argv)
                
            else:
                # Normaler Modul-Architekt (für neue Skripte im Module-Ordner)
                print(f"🏗️ [WORKER] Starte Architekt für normales Modul: {user_text}")
                res = ollama.generate(model="deto_agent", prompt=f"Erstelle Python Modul für: {user_text}. Nur Code.")
                code = res['response'].replace('```python', '').replace('```', '').strip()
                name = f"Modul_{target_name}"
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

        elif befehl == "KI_ANFRAGE":
            print(f"🤖 [WORKER] Sende Chat-Anfrage an deto_agent: '{user_text}'")
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
    print("🚀 MUTATIONS-WORKER AKTIV - Überwache Aufgaben...")
    print("📡 Bereit für Module und Core-Updates...")
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