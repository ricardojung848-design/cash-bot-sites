import threading
import time
from typing import Dict, Any, Optional
from doctor_core.logging import log_doctor
from doctor_core.event_system import EventSystem

class SubAgent:
    """Repräsentiert die Struktur eines spezialisierten Sub-Agenten im Ökosystem."""
    def __init__(self, name: str, agent_type: str):
        self.name = name
        self.agent_type = agent_type  # z.B. 'render', 'social', 'optimizer', 'worker'
        self.status = "stopped"       # stopped, running, error, idle
        self.last_seen = time.time()
        self.current_task = None

class MultiAgentController:
    """
    Phase 11 Multi-Agent-Support:
    Die Schaltzentrale des Doctors, um mehrere autonome Sub-Agenten 
    zu registrieren, zu steuern, zu überwachen und zu koordinieren.
    """
    def __init__(self):
        self._agents: Dict[str, SubAgent] = {}
        self._lock = threading.Lock()
        self.events = EventSystem()
        
        # Hooks an das Event-System aus Phase 9 binden
        self.events.subscribe("agent_status_update", self._handle_agent_status)
        self.events.subscribe("delegate_task", self._handle_task_delegation)
        
        log_doctor("Multi-Agent-Support: Agenten-Controller initialisiert.")

    def register_agent(self, name: str, agent_type: str) -> None:
        """Registriert einen neuen Sub-Agenten im System."""
        with self._lock:
            if name in self._agents:
                log_doctor(f"Multi-Agent-Support: Agent '{name}' ist bereits registriert.")
                return
            self._agents[name] = SubAgent(name, agent_type)
            log_doctor(f"Multi-Agent-Support: 🤖 Agent '{name}' ({agent_type}) erfolgreich registriert.")

    def get_agent_status(self, name: str) -> Optional[dict]:
        """Gibt den aktuellen Zustand eines spezifischen Agenten zurück."""
        with self._lock:
            agent = self._agents.get(name)
            if agent:
                return {
                    "name": agent.name,
                    "type": agent.agent_type,
                    "status": agent.status,
                    "current_task": agent.current_task,
                    "active": (time.time() - agent.last_seen) < 15  # Heartbeat-Check (15s)
                }
            return None

    def list_all_agents(self) -> list:
        """Gibt eine Liste aller registrierten Agenten und deren Zustände zurück."""
        with self._lock:
            return [
                {
                    "name": a.name,
                    "type": a.agent_type,
                    "status": a.status,
                    "task": a.current_task,
                    "alive": (time.time() - a.last_seen) < 15
                }
                for a in self._agents.values()
            ]

    # --- EVENT HOOKS (PHASE 9 INTEGRATION) ---

    def _handle_agent_status(self, data: Any) -> None:
        """Hook: Verarbeitet eingehende Lebenszeichen (Heartbeats) und Statusänderungen von Agenten."""
        if not isinstance(data, dict) or "name" not in data:
            return
            
        name = data["name"]
        status = data.get("status", "running")
        current_task = data.get("task", None)
        
        with self._lock:
            if name in self._agents:
                agent = self._agents[name]
                agent.status = status
                agent.current_task = current_task
                agent.last_seen = time.time()
            else:
                # Agent schickt Lebenszeichen, war aber noch nicht registriert -> Auto-Registrierung
                log_doctor(f"Multi-Agent-Support: Unbekannter Agent '{name}' erkannt. Starte Auto-Registrierung.")
                self._agents[name] = SubAgent(name, data.get("type", "generic"))
                self._agents[name].status = status
                self._agents[name].last_seen = time.time()

    def _handle_task_delegation(self, data: Any) -> None:
        """Hook: Nimmt globale Aufgaben entgegen und sucht den passendsten, freien Agenten."""
        if not isinstance(data, dict) or "target_type" not in data or "task_data" not in data:
            return
            
        target_type = data["target_type"]
        task_data = data["task_data"]
        
        allocated_agent = None
        with self._lock:
            for agent in self._agents.values():
                # Finde einen Agenten des gesuchten Typs, der bereit ('idle' oder 'running') und online ist
                if agent.agent_type == target_type and (time.time() - agent.last_seen) < 15:
                    allocated_agent = agent.name
                    break
                    
        if allocated_agent:
            log_doctor(f"Multi-Agent-Support: Aufgabe an Agent '{allocated_agent}' ({target_type}) zugewiesen.")
            # Event direkt an den spezifischen Agenten feuern
            self.events.trigger(f"task_{allocated_agent}", task_data)
        else:
            log_doctor(f"Multi-Agent-Support: ⚠️ Keine aktiven Agenten für Typ '{target_type}' verfügbar. Aufgabe geparkt.")
            self.events.trigger("task_pipeline_stalled", {"target_type": target_type, "task_data": task_data})