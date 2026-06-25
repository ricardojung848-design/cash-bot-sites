import os
import time
import requests
from pathlib import Path
from urllib.parse import quote
from typing import Optional

from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager


class InstagramEngine:
    """
    PRO-Version der Instagram-Schnittstelle:
    - Wickelt den mehrstufigen Reels-Upload-Prozess über die Meta Graph API ab
    - Vollständig thread-sicher konzipiert für die asynchrone Ausführung in der FabrikEngine
    - Bezieht Umgebungsvariablen und Konfigurationen zentralisiert
    """

    def __init__(self, engine_manager: EngineManager, api_version: str = "v23.0"):
        self.engines = engine_manager
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

        # API-Credentials aus der Umgebung oder dem Config-System laden
        self.access_token = os.environ.get("IG_ACCESS_TOKEN", "").strip()
        self.ig_user_id = os.environ.get("IG_USER_ID", "").strip()

    def _build_public_video_url(self, video_path: str) -> str:
        """Erzeugt aus einem lokalen Dateipfad eine über das CDN öffentlich erreichbare URL."""
        filename = os.path.basename(video_path)
        base_cdn_url = os.environ.get("IG_CDN_BASE_URL", "").strip()

        if not base_cdn_url:
            log_doctor("Instagram-Fehler: 'IG_CDN_BASE_URL' fehlt in den Umgebungsvariablen.")
            return ""

        base_cdn_url = base_cdn_url.rstrip("/")
        return f"{base_cdn_url}/{quote(filename)}"

    def _create_reel_container(self, video_url: str, caption: str) -> str:
        """Initiiert den Upload bei Meta und fordert eine Container-ID (creation_id) an."""
        url = f"{self.base_url}/{self.ig_user_id}/media"
        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "share_to_feed": True,
            "access_token": self.access_token
        }

        log_doctor("Instagram: Erstelle Video-Container auf den Meta-Servern...")
        try:
            resp = requests.post(url, data=payload, timeout=30)
            if resp.status_code != 200:
                log_doctor(f"Instagram-Fehler beim Container-Upload: {resp.status_code} - {resp.text}")
                return ""
            
            creation_id = resp.json().get("id")
            if creation_id:
                log_doctor(f"Instagram: Container erfolgreich reserviert (ID: {creation_id})")
                return str(creation_id)
        except Exception as e:
            log_doctor(f"Instagram-Netzwerkfehler beim Container-Upload: {e}")
        
        return ""

    def _wait_for_container(self, creation_id: str, max_wait_seconds: int = 300, poll_interval: int = 5) -> bool:
        """Pollt den Meta-Verarbeitungsstatus, bis das Video serverseitig encodiert wurde."""
        url = f"{self.base_url}/{creation_id}"
        params = {
            "fields": "status_code,status",
            "access_token": self.access_token
        }

        log_doctor(f"Instagram: Warte auf serverseitige Videoverarbeitung für Container {creation_id}...")
        waited = 0
        
        while waited < max_wait_seconds:
            try:
                resp = requests.get(url, params=params, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    status_code = data.get("status_code")
                    status = data.get("status")

                    log_doctor(f"Instagram-Polling: {status_code} ({status})")

                    if status_code == "FINISHED":
                        log_doctor("Instagram: Videoverarbeitung abgeschlossen.")
                        return True
                    if status_code == "ERROR":
                        log_doctor(f"Instagram-Kritisch: Meta meldet Encodierungsfehler: {data}")
                        return False
            except Exception as e:
                log_doctor(f"Instagram-Polling-Warnung: Netzwerk-Timeout: {e}")

            time.sleep(poll_interval)
            waited += poll_interval

        log_doctor("Instagram-Fehler: Timeout beim Warten auf die Videoverarbeitung erreicht.")
        return False

    def _publish_container(self, creation_id: str) -> bool:
        """Gibt den fertig verarbeiteten Container für den Live-Feed frei."""
        url = f"{self.base_url}/{self.ig_user_id}/media_publish"
        payload = {
            "creation_id": creation_id,
            "access_token": self.access_token
        }

        log_doctor("Instagram: Schalte Reel live...")
        try:
            resp = requests.post(url, data=payload, timeout=30)
            if resp.status_code == 200:
                media_id = resp.json().get("id")
                log_doctor(f"Instagram: 🎉 Reel erfolgreich veröffentlicht! (Media-ID: {media_id})")
                return True
            log_doctor(f"Instagram-Fehler bei Live-Schaltung: {resp.status_code} - {resp.text}")
        except Exception as e:
            log_doctor(f"Instagram-Netzwerkfehler bei Live-Schaltung: {e}")
        
        return False

    def post_reel(self, video_path: str, caption: str) -> bool:
        """
        Hauptmethode zum Veröffentlichen eines Reels.
        Sollte vorzugsweise als Task in die FabrikEngine eingereiht werden.
        """
        if not self.access_token or not self.ig_user_id:
            log_doctor("Instagram-Fehler: 'IG_ACCESS_TOKEN' oder 'IG_USER_ID' nicht konfiguriert.")
            return False

        if not Path(video_path).exists():
            log_doctor(f"Instagram-Fehler: Lokale Videodatei existiert nicht: {video_path}")
            return False

        # 1. Öffentliche CDN-URL generieren
        video_url = self._build_public_video_url(video_path)
        if not video_url:
            return False

        # 2. Container bei Meta anlegen
        creation_id = self._create_reel_container(video_url, caption)
        if not creation_id:
            return False

        # 3. Asynchrones Polling (blockiert dank FabrikEngine nicht das Hauptsystem)
        if not self._wait_for_container(creation_id):
            return False

        # 4. Reel final publizieren
        return self._publish_container(creation_id)