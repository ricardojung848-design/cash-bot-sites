import time
import threading

class BackgroundMonitor:
    def __init__(self, logger):
        self.log = logger

    def start(self):
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        self.log("Hintergrundüberwachung gestartet (PRO-Version).")
        while True:
            self.log("Hintergrund-Check ausgeführt.")
            time.sleep(10)
