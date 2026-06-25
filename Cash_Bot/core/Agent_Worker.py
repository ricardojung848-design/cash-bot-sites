import os
import sys
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

def worker_loop():
    print("[BOOT] Starten der Agent Worker Engine (PRO)...")
    
    # EngineManager instanziieren
    manager = EngineManager()
    
    # State-Manager (Langzeitgedächtnis) nachrüsten und registrieren
    state = DoctorState()
    manager.register("state", state)
    
    # FabrikEngine starten – JETZT mit registriertem State-Manager!
    fabrik = FabrikEngine(manager)
    print("[ONLINE] Worker-Engine läuft stabil.")

if __name__ == "__main__":
    worker_loop()