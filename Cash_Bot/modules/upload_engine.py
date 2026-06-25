import os
import shutil
from pathlib import Path
from urllib.parse import quote
from typing import Optional

from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager


class UploadEngine:
    """
    PRO-Version der UploadEngine:
    - Bereitet Mediendateien für das CDN (z. B. GitHub Pages) vor.
    - Kopiert gerenderte Reels in das öffentliche Verzeichnis und generiert die Ziel-URLs.
    - Arbeitet vollständig thread-sicher mit modernen Pathlib-Operationen.
    """

    def __init__(self, engine_manager: EngineManager):
        self.engines = engine_manager
        # Basis-URL für das CDN aus den Umgebungsvariablen laden
        self.base_cdn_url = os.environ.get("IG_CDN_BASE_URL", "").rstrip("/")

    def upload(self, file_path: str) -> Optional[str]:
        """
        Kopiert das Reel in den Ordner public_reels und gibt die öffentliche URL zurück.
        Gibt None zurück, falls ein Fehler auftritt oder Konfigurationen fehlen.
        """
        if not self.base_cdn_url:
            log_doctor("UploadEngine-Fehler: 'IG_CDN_BASE_URL' fehlt in den Umgebungsvariablen.")
            return None

        source_file = Path(file_path).resolve()
        if not source_file.exists():
            log_doctor(f"UploadEngine-Fehler: Quelldatei nicht gefunden: {source_file}")
            return None

        # Projekt-Basisverzeichnis ermitteln (zwei Ebenen über dieser Datei)
        base_dir = Path(__file__).resolve().parent.parent
        public_dir = base_dir / "public_reels"

        try:
            # Zielverzeichnis erstellen, falls es noch nicht existiert
            public_dir.mkdir(parents=True, exist_ok=True)

            filename = source_file.name
            target_path = public_dir / filename

            # Datei kopieren
            shutil.copy(str(source_file), str(target_path))
            log_doctor(f"UploadEngine: Datei erfolgreich nach public_reels kopiert -> {target_path}")

            # Öffentliche, URL-kodierte CDN-URL erzeugen
            public_url = f"{self.base_cdn_url}/{quote(filename)}"
            log_doctor(f"UploadEngine: 🌐 Bereitgestellte CDN-URL -> {public_url}")
            
            return public_url

        except Exception as e:
            log_doctor(f"UploadEngine-Kritisch: Fehler beim Kopieren der Datei: {e}")
            return None


# Abwärtskompatibler Einstiegspunkt für ältere Programmteile
def upload_legacy(file_path: str, engine_manager: EngineManager) -> Optional[str]:
    """Erlaubt Legacy-Modulen den Aufruf der neuen Upload-Logik."""
    engine = UploadEngine(engine_manager)
    return engine.upload(file_path)