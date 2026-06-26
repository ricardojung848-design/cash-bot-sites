import os
import sys
import subprocess
from pathlib import Path

# BASE_DIR zeigt fest auf das Hauptverzeichnis (Cash_Bot)
BASE_DIR = Path(__file__).resolve().parent.parent

class AgentProcessManager:
    def __init__(self, engine_manager):
        self.engines = engine_manager
        self.running_processes = {}  # Struktur: { "Agenten_Name": subprocess.Popen }

    def start_agent(self, agent_name, script_path):
        """Startet einen Agenten parallel über einen absolut abgesicherten Windows-Pfad"""
        clean_name = agent_name.replace(" ", "_")

        if clean_name in self.running_processes:
            if self.running_processes[clean_name].poll() is None:
                return f"[INFO] {agent_name} läuft bereits aktiv."

        # ABSICHERUNG: Macht aus 'core/Agent_Worker.py' einen absoluten Windows-Pfad
        full_path = (BASE_DIR / script_path).resolve()
        
        if not full_path.exists():
            return f"[ERROR] Datei existiert nicht unter: {full_path}"

        try:
            # Aufruf mit deiner exakten Python-Version und absolutem Pfad
            proc = subprocess.Popen(
                ["py", "-3.13-64", str(full_path)],
                cwd=str(BASE_DIR),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Kurzer Verifizierungs-Check
            try:
                proc.wait(timeout=0.4)
                exit_code = proc.poll()
                if exit_code is not None and exit_code != 0:
                    return f"[CRASH] Agent startete, brach aber sofort ab (Code {exit_code})."
            except subprocess.TimeoutExpired:
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
        """Zentraler Notschalter für alle Agenten"""
        for name in list(self.running_processes.keys()):
            self.stop_agent(name)
        return "ALL PROCESSES TERMINATED"

    def get_statuses(self):
        """Liefert den Live-Status für die iPhone-App-Kacheln"""
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