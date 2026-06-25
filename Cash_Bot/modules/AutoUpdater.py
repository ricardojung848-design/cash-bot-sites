import json
import urllib.request
import sys
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager

UPDATE_SERVER_URL = "https://raw.githubusercontent.com/ricardojung848-design/cash-bot-sites/main/update_server.json"


class UpdateEngine:
    """
    PRO-Version des Auto-Updaters:
    - Überprüft remote GitHub-Repositories nach neuen Code-Releases
    - Verwaltet die lokale Software-Version direkt im SQLite-Zustand (entfernt 'update_config.json')
    - Lädt Patches herunter und initiiert einen hot reload des Prozesses bei Updates
    """

    def __init__(self, engine_manager: EngineManager, base_dir: Optional[Path] = None):
        self.engines = engine_manager
        if not self.engines.has("state"):
            raise RuntimeError("UpdateEngine benötigt einen registrierten State-Manager im EngineManager!")
        self.state = self.engines.get("state")
        
        # Basis-Verzeichnis für Dateitransfers bestimmen
        self.base_dir = base_dir or Path(__file__).resolve().parent.parent

    def _get_local_version(self) -> str:
        """Liest die aktuell installierte Version aus der SQLite-Datenbank aus."""
        update_data = self.state.get_state("updater", {"version": "0.0.0"})
        return update_data.get("version", "0.0.0")

    def _set_local_version(self, version_str: str) -> None:
        """Sichert die neue Versionsnummer transaktionssicher in der DB."""
        update_data = self.state.get_state("updater", {"version": "0.0.0"})
        update_data["version"] = version_str
        self.state.set_state("updater", update_data)

    def fetch_remote_manifest(self) -> Optional[Dict[str, Any]]:
        """Fragt das Update-Manifest sicher vom Remote-Server ab."""
        try:
            req = urllib.request.Request(
                UPDATE_SERVER_URL,
                headers={'User-Agent': 'Agent_Doctor-UpdateEngine/2.0'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            log_doctor(f"UpdateEngine: Fehler beim Abruf des Remote-Manifests: {e}")
            return None

    def execute_check_and_update(self) -> bool:
        """
        Führt einen einzelnen, isolierten Update-Check durch.
        Gibt True zurück, wenn ein Update durchgeführt wurde und ein Neustart ansteht.
        """
        local_version = self._get_local_version()
        log_doctor(f"UpdateEngine: Starte Versionsprüfung... (Lokal: v{local_version})")
        
        manifest = self.fetch_remote_manifest()
        if not manifest:
            log_doctor("UpdateEngine: Update-Server temporär nicht erreichbar oder Manifest korrupt.")
            return False

        latest_version = manifest.get("latest_version", "0.0.0")
        if latest_version == local_version:
            log_doctor("UpdateEngine: System auf dem neuesten Stand. Keine Updates notwendig.")
            return False

        log_doctor(f"UpdateEngine: 🚀 Update gefunden! Modifikationen erkannt: v{local_version} → v{latest_version}")
        files_to_download = manifest.get("files", {})

        # Alle veränderten Dateien sequentiell herunterladen
        for rel_filepath, download_url in files_to_download.items():
            target_path = (self.base_dir / rel_filepath).resolve()
            log_doctor(f"UpdateEngine: Downloade Patch für '{rel_filepath}'...")
            
            try:
                # Sicherstellen, dass Unterordner existieren (z.B. modules/ oder config/)
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                urllib.request.urlretrieve(download_url, str(target_path))
            except Exception as e:
                log_doctor(f"UpdateEngine: Kritischer Fehler beim Schreiben von {rel_filepath}: {e}")
                return False

        # Version in DB hochstufen
        self._set_local_version(latest_version)
        log_doctor(f"UpdateEngine: Update auf v{latest_version} erfolgreich abgeschlossen. Hot-Reload wird eingeleitet...")
        
        # 2 Sekunden Cooldown für offene DB-Transaktionen, dann sauberer Neustart
        time.sleep(2)
        self._trigger_hot_reload()
        return True

    def _trigger_hot_reload(self) -> None:
        """Ersetzt den aktuellen Python-Prozess im RAM nahtlos durch die upgedatete Version."""
        os.execv(sys.executable, ["python"] + sys.argv)