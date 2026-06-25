import sys
import urllib.request
import json
from pathlib import Path
from doctor_core.logging import log_doctor
from doctor_core.state import DoctorState
from doctor_core.security_layer import SecurityLayer
from doctor_core.event_system import EventSystem

BASE_DIR = Path(__file__).resolve().parent.parent
MODULES_DIR = BASE_DIR / "modules"


class SelfImprovementEngine:
    """
    Phase 12 — Self-Improvement Engine:
    Ermöglicht dem Doctor autonome Webrecherche, Wissensextraktion,
    Sicherheitsprüfung und das Einspielen von eigenständigen Code-Upgrades.
    """

    def __init__(self, state: DoctorState):
        self.state = state
        self.security = SecurityLayer()
        self.events = EventSystem()
        log_doctor("Self-Improvement Engine: Kognitives Upgrade-System aktiv.")

    def run_autonomous_research(self, topic: str = "python ai agent optimization tips") -> bool:
        """
        ✔ Web-Research-Engine
        Recherchiert im Netz (simuliert/Scraping via URL-Request) nach neuen Methoden.
        """
        log_doctor(f"Self-Improvement: Starte Web-Research zu Thema: '{topic}'...")
        
        try:
            # Hier simulieren wir den Abruf topaktueller KI-Architekturen.
            # Im echten Betrieb kannst du hier eine Such-API wie Perplexity oder DuckDuckGo anbinden.
            query = urllib.parse.quote(topic)
            url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc"
            
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Agent_Doctor_PRO)'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode())
                items = res_data.get("items", [])
                
                if items:
                    top_repo = items[0]
                    repo_info = f"Repo: {top_repo['full_name']} - {top_repo['description']}"
                    
                    # ✔ Knowledge-Updater: Wissen persistent in Phase 8 absichern
                    self.state.store_knowledge("web_research", f"latest_{topic.replace(' ', '_')}", repo_info)
                    log_doctor(f"Self-Improvement ✅: Neues Wissen extrahiert und gelernt: {top_repo['full_name']}")
                    return True
                    
        except Exception as e:
            log_doctor(f"Self-Improvement ⚠️ Webrecherche-API eingeschränkt (Fallback-Wissen aktiv): {e}")
            # Lokales Fallback-Wissen generieren, falls Netzwerk offline ist
            self.state.store_knowledge("web_research", "latest_optimization", "Verwende asynchrone Queues für KI-Pipelines.")
        
        return False

    def execute_self_upgrade(self, target_module_name: str, new_code_content: str) -> bool:
        """
        ✔ Self-Upgrade-Engine
        Verbessert bestehende Module autonom, sofern sie die Sandbox-Sicherheitsprüfung bestehen.
        """
        target_file = MODULES_DIR / f"{target_module_name}.py"
        
        if not target_file.exists():
            log_doctor(f"Self-Improvement ❌: Upgrade abgebrochen. Zielmodul {target_module_name}.py existiert nicht.")
            return False

        # Temporäre Datei für die Sicherheitsprüfung in der Sandbox (Phase 10) erstellen
        temp_sandbox_file = MODULES_DIR / f"temp_upgrade_{target_module_name}.py"
        
        try:
            temp_sandbox_file.write_text(new_code_content, encoding="utf-8")
            
            # Security-Layer Validierung
            is_safe = self.security.verify_code_safety(temp_sandbox_file)
            
            if not is_safe:
                log_doctor(f"Self-Improvement 🛑 CRITICAL: Autonomes Upgrade für '{target_module_name}' durch Security-Layer blockiert!")
                return False
            
            # Backup des alten Moduls erstellen (Phase 7 Integration)
            backup_file = target_file.with_suffix(".py.bak")
            target_file.rename(backup_file)
            
            # Upgrade live schalten
            temp_sandbox_file.rename(target_file)
            log_doctor(f"Self-Improvement 🚀 SUCCESS: Modul '{target_module_name}' wurde autonom upgegradet!")
            
            # Event feuern (Phase 9 Integration)
            self.events.trigger("module_upgraded", {"module": target_module_name, "timestamp": target_file.stat().st_mtime})
            return True
            
        except Exception as e:
            log_doctor(f"Self-Improvement ❌ Fehler beim Upgrade-Prozess: {e}")
            # Rollback falls die temporäre Datei noch existiert
            if temp_sandbox_file.exists():
                temp_sandbox_file.unlink()
            return False
        finally:
            if temp_sandbox_file.exists():
                temp_sandbox_file.unlink()