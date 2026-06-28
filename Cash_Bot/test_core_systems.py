import os
import sys
import time
from pathlib import Path

# Stammverzeichnis absichern
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from doctor_core.engine_manager import EngineManager
from doctor_core.state import DoctorState
from doctor_core.process_manager import AgentProcessManager
from doctor_core.aegis_storage import AegisStorage

def run_integration_test():
    print("==================================================")
    print("🧪 STARTING AEGIS CORE SYSTEM INTEGRATION TEST")
    print("==================================================")
    
    # 1. TEST: Speicher-Infrastruktur (Datenbank)
    print("\n[STEP 1] Initialisiere Aegis-Datenbank...")
    try:
        db = AegisStorage()
        print("[OK] Datenbank erfolgreich initialisiert.")
        
        print("[DB] Schreibe Test-Aufgabe und Kalendereintrag...")
        db.add_task("Aegis OS Dashboard aufbauen")
        db.add_event("Core-Review mit KI", "2026-06-26", "14:00")
        
        tasks = db.get_all_tasks()
        print(f"[OK] Datenbank-Lesezugriff erfolgreich. Aktuelle Aufgaben im Speicher: {len(tasks)}")
    except Exception as e:
        print(f"[💥 ERROR] Fehler bei der Datenbank-Prüfung: {e}")
        return

    # 2. TEST: Multitasking & Prozess-Manager
    print("\n[STEP 2] Initialisiere EngineManager & ProcessManager...")
    try:
        state = DoctorState()
        manager = EngineManager()
        manager.register("state", state)
        
        pm = AgentProcessManager(manager)
        print("[OK] Prozess-Manager einsatzbereit.")
        
        # Wir versuchen den bestehenden Worker parallel zu zünden
        print("\n[PM] Starte 'Agent_Worker' im Hintergrund-Thread...")
        # Nutze den Pfad relativ zur Root, den wir in der registry festgelegt haben
        result = pm.start_agent("Agent_Worker", "core/Agent_Worker.py")
        print(f"[PM] Start-Rückmeldung: {result}")
        
        if result == "SUCCESS":
            print("[PM] Warte 3 Sekunden, damit der Prozess anlaufen kann...")
            time.sleep(3)
            
            # Status abfragen (Erwartet: 'RUNNING')
            statuses = pm.get_statuses()
            print(f"[LIVE STATUS] Erkannte Prozesse: {statuses}")
            
            worker_status = statuses.get("Agent_Worker", statuses.get("Agent Worker"))

            if worker_status == "RUNNING":
                print("\n[🎉 SUCCESS] MULTITASKING & DATA-CORE STEHEN BOMBENFEST!")
            else:
                print("\n[⚠️ WARNING] Prozess wurde gestartet, aber der Status ist ungewöhnlich.")
                
            # Sauber aufräumen und den Hintergrundprozess wieder killen
            print("\n[PM] Fahre Test-Prozesse wieder herunter...")
            pm.stop_agent("Agent_Worker")
            print("[OK] Hintergrundprozesse sauber beendet.")
            
    except Exception as e:
        print(f"[💥 ERROR] Fehler beim Multitasking-Test: {e}")

if __name__ == "__main__":
    run_integration_test()