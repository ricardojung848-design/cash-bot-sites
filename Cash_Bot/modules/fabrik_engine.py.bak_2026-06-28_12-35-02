import threading
import queue
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager

# Globale Thread-Anzahl für rechenintensive oder blockierende Operationen
THREAD_COUNT = 8


class FabrikTask:
    """Repräsentiert eine einzelne atomare Aufgabe innerhalb der FabrikEngine."""
    def __init__(self, thema: str, callback: Callable[[str], Any]):
        self.thema = thema
        self.callback = callback
        self.status = "pending"
        self.created_at = datetime.now().isoformat()
        self.started_at: Optional[str] = None
        self.finished_at: Optional[str] = None
        self.retries = 0
        self.error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert den Task-Status für die SQLite-Persistenz."""
        return {
            "thema": self.thema,
            "status": self.status,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "retries": self.retries,
            "error": self.error
        }


class FabrikEngine:
    """
    PRO-Version der FabrikEngine:
    - Verwaltet einen asynchronen Worker-Pool mit 8 Threads für asynchrone Logiken
    - Integriert ein automatisches Retry-Verfahren (max. 3 Versuche) bei Callback-Fehlern
    - Synchronisiert Task-Statistiken transaktionssicher mit dem SQLite-Zustand
    """

    def __init__(self, engine_manager: EngineManager):
        self.engines = engine_manager
        if not self.engines.has("state"):
            raise RuntimeError("FabrikEngine benötigt einen registrierten State-Manager im EngineManager!")
        self.state = self.engines.get("state")

        self.task_queue: queue.Queue = queue.Queue()
        self.active = False
        self.threads: List[threading.Thread] = []
        self.lock = threading.Lock()
        
        # Laufende Operationen verbleiben zur Performance-Optimierung im RAM
        self.running_tasks: Dict[str, FabrikTask] = {}

    def add_task(self, thema: str, callback: Callable[[str], Any]) -> str:
        """Reiht eine neue Aufgabe in die asynchrone Multi-Thread-Warteschlange ein."""
        task = FabrikTask(thema, callback)
        self.task_queue.put(task)
        log_doctor(f"Fabrik: Task registriert -> {thema}")
        return f"📥 Task hinzugefügt: {thema}"

    def _persist_task_history(self, task: FabrikTask) -> None:
        """Sichert abgeschlossen oder fehlgeschlagen Tasks persistent in der DB."""
        try:
            history = self.state.get_state("fabrik_history", {"tasks": []})
            history["tasks"].append(task.to_dict())
            
            # Speicherbegrenzung auf die letzten 200 Tasks, um DB-Blähung zu verhindern
            if len(history["tasks"]) > 200:
                history["tasks"] = history["tasks"][-200:]
                
            self.state.set_state("fabrik_history", history)
        except Exception as e:
            log_doctor(f"Fabrik-Fehler beim Sichern der Historie: {e}")

    def worker(self) -> None:
        """Interne Endlosschleife eines Worker-Threads."""
        while self.active:
            try:
                # Timeout verhindert Deadlocks beim Stoppen der Engine
                task: FabrikTask = self.task_queue.get(timeout=1)
            except queue.Empty:
                continue

            with self.lock:
                task.status = "running"
                task.started_at = datetime.now().isoformat()
                self.running_tasks[task.thema] = task

            try:
                # Dynamische Ausführung der Logik (z.B. generate_programmatic_pages)
                task.callback(task.thema)

                with self.lock:
                    task.status = "completed"
                    task.finished_at = datetime.now().isoformat()
                    if task.thema in self.running_tasks:
                        del self.running_tasks[task.thema]
                
                self._persist_task_history(task)
                log_doctor(f"Fabrik: Task erfolgreich beendet -> {task.thema}")

            except Exception as e:
                task.retries += 1
                task.error = str(e)
                log_doctor(f"Fabrik-Warnung: Fehler in Task '{task.thema}' (Versuch {task.retries}/3): {e}")

                if task.retries < 3:
                    # Erneutes Einreihen bei Fehlschlag
                    self.task_queue.put(task)
                else:
                    with self.lock:
                        task.status = "failed"
                        task.finished_at = datetime.now().isoformat()
                        if task.thema in self.running_tasks:
                            del self.running_tasks[task.thema]
                    
                    self._persist_task_history(task)
                    log_doctor(f"Fabrik: Task endgültig fehlgeschlagen -> {task.thema}")

            finally:
                self.task_queue.task_done()

    def start(self) -> str:
        """Aktiviert den Thread-Pool und startet alle Worker."""
        if self.active:
            return "⚠️ Fabrik läuft bereits."

        self.active = True
        self.threads = []

        for i in range(THREAD_COUNT):
            t = threading.Thread(target=self.worker, daemon=True, name=f"FabrikWorker-{i}")
            t.start()
            self.threads.append(t)

        log_doctor(f"Fabrik: Core-Zentrale hochgefahren mit {THREAD_COUNT} Threads.")
        return f"🚀 Fabrik gestartet mit {THREAD_COUNT} Threads."

    def stop(self) -> str:
        """Deaktiviert die Schleifen-Flags der Worker für einen sanften Shutdown."""
        self.active = False
        log_doctor("Fabrik: Shutdown-Signal an Worker-Threads gesendet.")
        return "🛑 Fabrik gestoppt."

    def get_status_summary(self) -> str:
        """Errechnet Echtzeitmetriken der Warteschlange für das Kontrollzentrum."""
        with self.lock:
            pending = self.task_queue.qsize()
            running = len(self.running_tasks)
            
            # Historische Werte aus DB laden
            history = self.state.get_state("fabrik_history", {"tasks": []})
            completed = sum(1 for t in history["tasks"] if t["status"] == "completed")
            failed = sum(1 for t in history["tasks"] if t["status"] == "failed")

        return (
            "📊 **Fabrik Status**\n"
            f"- Ausstehend (Pending): {pending}\n"
            f"- Aktiv (Running): {running}\n"
            f"- Abgeschlossen (Historie): {completed}\n"
            f"- Fehlgeschlagen (Historie): {failed}\n"
        )