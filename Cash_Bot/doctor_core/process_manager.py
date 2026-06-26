import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"

class AgentProcessManager:
    def __init__(self, engine_manager):
        self.engines = engine_manager
        self.running_processes = {}  # Struktur: { "Agenten_Name": subprocess.Popen }
        os.makedirs(str(LOG_DIR), exist_ok=True)

    def start_agent(self, agent_name, script_path):
        """Startet einen Agenten parallel und liefert im Crash-Fall eine präzise Diagnose"""
        clean_name = agent_name.replace(" ", "_")

        if clean_name in self.running_processes:
            if self.running_processes[clean_name].poll() is None:
                return f"[INFO] {agent_name} läuft bereits aktiv."

        full_path = (BASE_DIR / script_path).resolve()
        if not full_path.exists():
            return f"[ERROR] Datei existiert nicht: {script_path}"

        log_file_path = LOG_DIR / f"{clean_name}_error.log"

        try:
            # Fehlerstrom (stderr) direkt in Logdatei umleiten
            with open(log_file_path, "w", encoding="utf-8") as log_file:
                proc = subprocess.Popen(
                    ["py", "-3.13-64", str(full_path)],
                    cwd=str(BASE_DIR),
                    stdout=subprocess.DEVNULL,
                    stderr=log_file
                )
            
            # ⏱️ DIAGNOSE-FENSTER: Wir warten kurz, ob das Skript sofort crasht
            try:
                proc.wait(timeout=0.6)
                exit_code = proc.poll()
                if exit_code is not None and exit_code != 0:
                    # Diagnose-Auswertung starten
                    err_msg = "Unbekannter Fehler"
                    if log_file_path.exists():
                        raw_error = log_file_path.read_text(encoding="utf-8").strip()
                        if raw_error:
                            # Filtert die letzte Zeile für eine kompakte Ansage heraus
                            lines = [line.strip() for line in raw_error.split("\n") if line.strip()]
                            err_msg = lines[-1] if lines else raw_error

                    return f"[CRASH] {agent_name} abgebrochen -> {err_msg}"
            except subprocess.TimeoutExpired:
                # Prozess läuft stabil über die kritische Startphase hinaus
                pass

            self.running_processes[clean_name] = proc
            return "SUCCESS"
            
        except Exception as e:
            return f"[ERROR] Windows-Startfehler für {agent_name}: {e}"

    def stop_agent(self, agent_name):
        """Stoppt einen spezifischen Agenten sauber"""
        clean_name = agent_name.replace(" ", "_")
        if clean_name in self.running_processes:
            proc = self.running_processes[clean_name]
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()
            del self.running_processes[clean_name]
            return "SUCCESS"
        return f"[INFO] {agent_name} ist bereits offline."

    def stop_all(self):
        """Zentraler Notschalter (Kill-Switch) für alle Agenten"""
        for name in list(self.running_processes.keys()):
            self.stop_agent(name)
        return "ALL PROCESSES TERMINATED"

    def get_statuses(self):
        """Liefert den Live-Status für die Kacheln"""
        status_dict = {}
        for name, proc in list(self.running_processes.items()):
            exit_code = proc.poll()
            display_name = name.replace("_", " ")
            
            if exit_code is None:
                status_dict[display_name] = "RUNNING"
            else:
                status_dict[display_name] = "CRASHED" if exit_code != 0 else "OFFLINE"
                del self.running_processes[name]
                
                if exit_code != 0:
                    self._alert_doctor(display_name, exit_code)
        return status_dict

    def _alert_doctor(self, agent_name, exit_code):
        state = self.engines.get("state")
        if state:
            state.update_state(f"agent_{agent_name}_crash", f"Code {exit_code}")
        print(f"[DOCTOR INTERVENTION] Agent {agent_name} kollabiert. Code: {exit_code}")