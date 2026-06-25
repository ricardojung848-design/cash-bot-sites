import queue
import threading
import time
from typing import Callable, Dict, List, Any
from doctor_core.logging import log_doctor

class EventSystem:
    """
    Phase 9 Event-System (Trigger & Hooks):
    Ermöglicht eine entkoppelte, ereignisgesteuerte Kommunikation im gesamten Ökosystem.
    Module können auf Events lauschen (Hooks) oder selbst Events abfeuern (Trigger).
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        # Singleton-Pattern, damit alle Module dasselbe Event-System nutzen
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EventSystem, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._listeners: Dict[str, List[Callable[[Any], None]]] = {}
        self._event_queue: queue.Queue = queue.Queue()
        self._is_running = False
        self._worker_thread: threading.Thread = None
        self._initialized = True
        self.start()

    def start(self) -> None:
        """Startet die asynchrone Event-Verarbeitungsschleife."""
        if self._is_running:
            return
        self._is_running = True
        self._worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self._worker_thread.start()
        log_doctor("Event-System: Asynchroner Event-Loop erfolgreich hochgefahren.")

    def stop(self) -> None:
        """Stoppt die Event-Verarbeitung."""
        self._is_running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=2.0)
        log_doctor("Event-System: Event-Loop sauber heruntergefahren.")

    def subscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """Registriert einen Hook (Callback) für einen bestimmten Event-Typ."""
        with self._lock:
            if event_type not in self._listeners:
                self._listeners[event_type] = []
            if callback not in self._listeners[event_type]:
                self._listeners[event_type].append(callback)
                log_doctor(f"Event-System: Hook registriert für Typ '{event_type}'.")

    def unsubscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """Entfernt einen Hook wieder."""
        with self._lock:
            if event_type in self._listeners and callback in self._listeners[event_type]:
                self._listeners[event_type].remove(callback)

    def trigger(self, event_type: str, data: Any = None) -> None:
        """Feuert ein Event ab und legt es in die asynchrone Warteschlange (Queue)."""
        event = {"type": event_type, "data": data, "timestamp": time.time()}
        self._event_queue.put(event)

    def _process_queue(self) -> None:
        """Arbeitet die Queue im Hintergrund ab und verteilt Events an die Hooks."""
        while self._is_running:
            try:
                # Wartet maximal 0.5 Sekunden auf ein Event, um die Schleife lebendig zu halten
                event = self._event_queue.get(timeout=0.5)
                event_type = event["type"]
                data = event["data"]

                # Hooks abrufen und ausführen
                listeners_to_notify = []
                with self._lock:
                    if event_type in self._listeners:
                        listeners_to_notify = list(self._listeners[event_type])

                for callback in listeners_to_notify:
                    try:
                        callback(data)
                    except Exception as e:
                        log_doctor(f"Event-System-Fehler beim Ausführen eines Hooks für '{event_type}': {e}")
                
                self._event_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                log_doctor(f"Event-System-Kritischer Loop-Fehler: {e}")