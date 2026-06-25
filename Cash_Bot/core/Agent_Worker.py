import os
import sys
import time  # Für präzise Zeitstempel im Aegis-Dashboard
from pathlib import Path

# Stammverzeichnis korrekt in den Systempfad einhängen
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from doctor_core.engine_manager import EngineManager
from doctor_core.state import DoctorState

# Dynamischer Import-Schutz für die FabrikEngine
try:
    from modules.engines.engine_fabrik import FabrikEngine
except ImportError:
    try:
        from modules.fabrik_engine import FabrikEngine
    except ImportError:
        # Letzter Ausweg: Falls die Engine im Hauptverzeichnis oder modules liegt
        sys.path.append(str(BASE_DIR / "modules"))
        from fabrik_engine import FabrikEngine

# Pfad zur zentralen Aegis-Logdatei
LOG_FILE = BASE_DIR / "logs" / "worker.log"

def log_message(msg: str):
    """Gibt Nachrichten im Terminal aus und schreibt sie parallel in das Aegis-Log"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    full_msg = f"[{timestamp}] {msg}"
    
    print(full_msg)  # Bleibt für dein normales Terminal sichtbar
    
    try:
        os.makedirs(LOG_FILE.parent, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_msg + "\n")
    except Exception as e:
        print(f"[LOG ERROR] Fehler beim Schreiben in {LOG_FILE}: {e}")

def worker_loop():
    log_message("[BOOT] Starten der Agent Worker Engine (PRO)...")
    
    # EngineManager instanziieren
    manager = EngineManager()
    
    # State-Manager (Langzeitgedächtnis) nachrüsten und registrieren
    state = DoctorState()
    manager.register("state", state)
    
    try:
        # FabrikEngine starten – JETZT mit registriertem State-Manager!
        fabrik = FabrikEngine(manager)
        log_message("[ONLINE] Worker-Engine läuft stabil.")
        
        # Hält den Worker aktiv und sendet regelmäßige Lebenszeichen ans Dashboard
        while True:
            log_message("[PROCESS] FabrikEngine operiert im Nominalbereich. Überwachung aktiv.")
            time.sleep(5)
            
    except Exception as err:
        import traceback
        log_message(f"[CRITICAL_ERROR] Ausnahmezustand im Core-Prozess: {err}")
        log_message(traceback.format_exc())

if __name__ == "__main__":
    worker_loop()