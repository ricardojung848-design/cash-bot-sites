from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Callable, List
import threading
import queue
from doctor_core.logging import log_doctor


@dataclass
class EngineManager:
    """
    MEGA-PRO-Version:
    - Zentraler Container für alle Engines (Service Locator)
    - Dynamische Registrierung mit Thread-Safety
    - Integrierter Event-Bus (Pub/Sub) für Trigger & Hooks
    - Ermöglicht asynchrone, entkoppelte Multi-Agenten-Kommunikation
    """

    _engines: Dict[str, Any] = field(default_factory=dict)
    _listeners: Dict[str, List[Callable]] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _event_queue: queue.Queue = field(default_factory=queue.Queue)
    _loop_running: bool = field(default=False)

    def __post_init__(self):
        # Startet den asynchronen Event-Dispatcher-Thread
        self._start_event_loop()

    # --- ENGINE MANAGEMENT ---

    def register(self, name: str, engine: Any) -> None:
        """
        Engine unter einem Namen registrieren. Thread-sicher.
        Beispiel:
            engines.register("fix", FixSuggestionEngine(...))
        """
        if not name:
            raise ValueError("Engine-Name darf nicht leer sein.")
        
        with self._lock:
            self._engines[name] = engine
            setattr(self, name, engine)
            log_doctor(f"EngineManager: Engine '{name}' registriert: {engine.__class__.__name__}")

    def get(self, name: str) -> Optional[Any]:
        """Engine per Namen abrufen."""
        with self._lock:
            return self._engines.get(name)

    def has(self, name: str) -> bool:
        """Prüfen, ob eine Engine registriert ist."""
        with self._lock:
            return name in self._engines

    def ensure(self, name: str) -> Any:
        """Engine holen oder Fehler loggen, wenn sie fehlt."""
        engine = self.get(name)
        if engine is None:
            log_doctor(f"EngineManager: Engine '{name}' ist nicht registriert.")
        return engine

    def list_engines(self) -> Dict[str, str]:
        """Übersicht aller registrierten Engines (Name -> Klassennamen)."""
        with self._lock:
            return {name: engine.__class__.__name__ for name, engine in self._engines.items()}

    # --- EVENT-SYSTEM (TRIGGER & HOOKS) ---

    def subscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """
        Registriert einen Hook / Listener für ein bestimmtes Event.
        Beispiel:
            engines.subscribe("new_error", self.auto_fix_engine.handle_error)
        """
        with self._lock:
            if event_type not in self._listeners:
                self._listeners[event_type] = []
            self._listeners[event_type].append(callback)
            log_doctor(f"EngineManager: Hook für Event '{event_type}' registriert.")

    def trigger(self, event_type: str, data: Any = None) -> None:
        """
        Feuert ein Event ab. Das Event wird in eine Queue gelegt,
        damit der aufrufende Thread nicht blockiert wird (Asynchron).
        """
        self._event_queue.put((event_type, data))

    def _start_event_loop(self):
        """Startet den Hintergrund-Thread zur Event-Verarbeitung."""
        with self._lock:
            if not self._loop_running:
                self._loop_running = True
                t = threading.Thread(target=self._event_dispatcher_worker, daemon=True, name="DoctorEventLoop")
                t.start()

    def _event_dispatcher_worker(self):
        """Verarbeitet Events sequentiell im Hintergrund, um Race Conditions zu vermeiden."""
        while self._loop_running:
            try:
                # Wartet blockierend auf das nächste Event (Timeout für sauberes Beenden)
                event_type, data = self._event_queue.get(timeout=1.0)
                
                with self._lock:
                    listeners = self._listeners.get(event_type, []).copy()

                for callback in listeners:
                    try:
                        # Ruft den registrierten Hook auf
                        callback(data)
                    except Exception as e:
                        log_doctor(f"CRITICAL Event Error in Hook für '{event_type}': {str(e)}")
                
                self._event_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                log_doctor(f"CRITICAL Event Loop Failure: {str(e)}")