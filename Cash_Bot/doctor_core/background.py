from dataclasses import dataclass, field
import time
import threading
from typing import Callable, List, Dict, Any
from doctor_core.logging import log_doctor


@dataclass
class ScheduledTask:
    """Repräsentiert einen einzelnen zeitgesteuerten Task im System."""
    name: str
    callback: Callable[[], None]
    interval_seconds: int
    last_run: float = 0.0
    is_running: bool = False


class BackgroundMonitor:
    """
    MEGA-PRO-Version:
    - Autonomer Enterprise-Scheduler für zeitgesteuerte Hintergrund-Tasks
    - Dynamische Task-Registrierung mit individuellen Intervallen
    - Integrierter Crash-Schutz (ein fehlerhafter Task killt nicht den Monitor)
    - Thread-sichere Ausführung der Jobs
    """

    def __init__(self, engine_manager: Any = None):
        self.engines = engine_manager
        self._tasks: Dict[str, ScheduledTask] = {}
        self._lock = threading.Lock()
        self._running = False

    def register_task(self, name: str, callback: Callable[[], None], interval_seconds: int) -> None:
        """
        Registriert einen neuen zeitgesteuerten Job.
        Beispiel:
            monitor.register_task("backup", engines.backup.create, 86400)
        """
        with self._lock:
            self._tasks[name] = ScheduledTask(
                name=name,
                callback=callback,
                interval_seconds=interval_seconds
            )
            log_doctor(f"BackgroundMonitor: Task '{name}' registriert (Intervall: {interval_seconds}s).")

    def start(self) -> None:
        """Startet die Hintergrundüberwachung in einem eigenen Thread."""
        with self._lock:
            if not self._running:
                self._running = True
                t = threading.Thread(target=self._loop, daemon=True, name="DoctorSchedulerLoop")
                t.start()
                log_doctor("BackgroundMonitor: Haupt-Scheduler-Loop erfolgreich gestartet.")

    def stop(self) -> None:
        """Stoppt den Scheduler-Loop sauber."""
        with self._lock:
            self._running = False

    def _loop(self) -> None:
        """Der zentrale Taktgeber. Überprüft jede Sekunde, welche Tasks fällig sind."""
        while self._running:
            current_time = time.time()
            
            # Kopie der Tasks erstellen, um Sperrfristen kurz zu halten
            with self._lock:
                tasks_to_check = list(self._tasks.values())

            for task in tasks_to_check:
                # Prüfen, ob das Intervall abgelaufen ist und der Task nicht bereits läuft
                if (current_time - task.last_run) >= task.interval_seconds and not task.is_running:
                    task.is_running = True
                    task.last_run = current_time
                    
                    # Task in einem eigenen Worker-Thread ausführen, damit der Scheduler nicht blockiert
                    worker = threading.Thread(
                        target=self._run_task_safely,
                        args=(task,),
                        daemon=True,
                        name=f"Worker_{task.name}"
                    )
                    worker.start()

            # Präziser 1-Sekunden-Takt für minimale CPU-Last
            time.sleep(1.0)

    def _run_task_safely(self, task: ScheduledTask) -> None:
        """Führt den Task aus und fängt alle Exceptions ab, damit das System stabil bleibt."""
        try:
            log_doctor(f"BackgroundMonitor: Starte Job '{task.name}'...")
            
            # Ausführung des eigentlichen Codes
            task.callback()
            
            log_doctor(f"BackgroundMonitor: Job '{task.name}' erfolgreich beendet.")
            
            # Wenn die Engine-Zentrale geladen ist, feuern wir ein Event ab
            if self.engines:
                self.engines.trigger(f"task_success_{task.name}")

        except Exception as e:
            error_msg = f"CRITICAL Error in Background Job '{task.name}': {str(e)}"
            log_doctor(error_msg)
            
            # Fehler direkt im neuen Langzeitgedächtnis loggen, falls verfügbar
            if self.engines and self.engines.has("state"):
                try:
                    import traceback
                    self.engines.get("state").log_error(
                        module_name=f"background_{task.name}",
                        error_message=str(e),
                        traceback=traceback.format_exc()
                    )
                    # Trigger ein Event, damit die Auto-Fix-Engine sofort Bescheid weiß!
                    self.engines.trigger("new_error", {"module": task.name, "error": str(e)})
                except Exception:
                    pass
        finally:
            task.is_running = False