# modules/upload_engine.py

import os
import shutil
from urllib.parse import quote
from core.utils import log_worker, error_worker


class UploadEngine:
    def __init__(self) -> None:
        # Basis-URL für GitHub Pages
        self.base_cdn_url = os.environ.get("IG_CDN_BASE_URL", "").rstrip("/")

    # ---------------------------------------------------------
    # Lokaler Upload: Datei in public_reels kopieren
    # ---------------------------------------------------------
    def upload(self, file_path: str) -> str:
        """
        Kopiert das Reel in den Ordner public_reels und gibt die öffentliche URL zurück.
        """

        if not self.base_cdn_url:
            error_worker("❌ IG_CDN_BASE_URL fehlt – kann keine öffentliche URL erzeugen.")
            return None

        if not os.path.exists(file_path):
            error_worker(f"❌ Datei nicht gefunden: {file_path}")
            return None

        # Projektbasis ermitteln
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        public_dir = os.path.join(base_dir, "public_reels")

        os.makedirs(public_dir, exist_ok=True)

        filename = os.path.basename(file_path)
        target_path = os.path.join(public_dir, filename)

        try:
            shutil.copy(file_path, target_path)
            log_worker(f"📤 Datei kopiert nach public_reels: {target_path}")
        except Exception as e:
            error_worker(f"❌ Fehler beim Kopieren: {e}")
            return None

        # Öffentliche URL erzeugen
        public_url = f"{self.base_cdn_url}/{quote(filename)}"
        log_worker(f"🌐 Öffentliche URL: {public_url}")

        return public_url
