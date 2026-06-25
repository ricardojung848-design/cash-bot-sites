# PRO AUTO-FIX: Registriert den State-Manager im EngineManager
from doctor_core.engine_manager import EngineManager
from doctor_core.state import DoctorState
from modules.fabrik_engine import FabrikEngine

def worker_loop():
    print("[BOOT] Starten der Agent Worker Engine (PRO)...")
    manager = EngineManager()
    
    # Automatisch nachgerüstet:
    state = DoctorState()
    manager.register("state", state)
    
    fabrik = FabrikEngine(manager)
    # Restlicher Loop läuft stabil weiter