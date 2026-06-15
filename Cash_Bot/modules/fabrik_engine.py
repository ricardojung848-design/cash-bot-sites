import threading
import queue
import time
from datetime import datetime

# Anzahl Threads (deine Wahl: 8)
THREAD_COUNT = 8

class FabrikTask:
    def __init__(self, thema, callback):
        self.thema = thema
        self.callback = callback
        self.status = "pending"
        self.created_at = datetime.now().isoformat()
        self.started_at = None
        self.finished_at = None
        self.retries = 0
        self.error = None

class FabrikEngine:
    def __init__(self):
        self.task_queue = queue.Queue()
        self.active = False
        self.threads = []
        self.lock = threading.Lock()
        self.completed_tasks = []
        self.failed_tasks = []
        self.running_tasks = {}

    def add_task(self, thema, callback):
        task = FabrikTask(thema, callback)
        self.task_queue.put(task)
        return f"📥 Task hinzugefügt: {thema}"

    def worker(self):
        while self.active:
            try:
                task = self.task_queue.get(timeout=1)
            except queue.Empty:
                continue

            with self.lock:
                task.status = "running"
                task.started_at = datetime.now().isoformat()
                self.running_tasks[task.thema] = task

            try:
                # Callback = Funktion aus Logik.py (z. B. generate_programmatic_pages)
                result = task.callback(task.thema)

                with self.lock:
                    task.status = "completed"
                    task.finished_at = datetime.now().isoformat()
                    self.completed_tasks.append(task)
                    del self.running_tasks[task.thema]

            except Exception as e:
                task.retries += 1
                task.error = str(e)

                if task.retries < 3:
                    # Retry
                    self.task_queue.put(task)
                else:
                    with self.lock:
                        task.status = "failed"
                        task.finished_at = datetime.now().isoformat()
                        self.failed_tasks.append(task)
                        if task.thema in self.running_tasks:
                            del self.running_tasks[task.thema]

            self.task_queue.task_done()

    def start(self):
        if self.active:
            return "⚠️ Fabrik läuft bereits."

        self.active = True
        self.threads = []

        for _ in range(THREAD_COUNT):
            t = threading.Thread(target=self.worker, daemon=True)
            t.start()
            self.threads.append(t)

        return f"🚀 Fabrik gestartet mit {THREAD_COUNT} Threads."

    def stop(self):
        self.active = False
        return "🛑 Fabrik gestoppt."

    def status(self):
        with self.lock:
            pending = self.task_queue.qsize()
            running = len(self.running_tasks)
            completed = len(self.completed_tasks)
            failed = len(self.failed_tasks)

        return (
            "📊 **Fabrik Status**\n"
            f"- Pending: {pending}\n"
            f"- Running: {running}\n"
            f"- Completed: {completed}\n"
            f"- Failed: {failed}\n"
        )

# Singleton-Instanz
FABRIK = FabrikEngine()
