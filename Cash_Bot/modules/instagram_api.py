import os
import time
import requests
from urllib.parse import quote

from core.utils import log_worker, warn_worker, error_worker


class InstagramPoster:
    def __init__(self, access_token: str, ig_user_id: str, api_version: str = "v23.0") -> None:
        self.access_token = access_token
        self.ig_user_id = ig_user_id
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    # ---------------------------------------------------------
    # Hilfsfunktion: öffentliche Video-URL bauen
    # ---------------------------------------------------------
    def _build_public_video_url(self, video_path: str) -> str:
        """
        WICHTIG:
        Instagram Graph API braucht eine öffentlich erreichbare URL.
        Hier musst du deine eigene Logik einbauen, z.B.:

        - Upload zu S3 / Cloud Storage
        - Bereitstellung über eigenen CDN
        - Statisches Hosting (NGINX, Apache, etc.)

        Fürs erste kannst du hier eine feste Basis-URL annehmen und
        die Datei manuell dorthin legen.

        Beispiel:
            BASE_CDN_URL = "https://dein-cdn.de/instagram"
            video_path = "/app/social/reel_auto.mp4"
            -> https://dein-cdn.de/instagram/reel_auto.mp4
        """
        # PLACEHOLDER-IMPLEMENTIERUNG:
        # Passe das an deine Infrastruktur an.
        filename = os.path.basename(video_path)
        base_cdn_url = os.environ.get("IG_CDN_BASE_URL", "").rstrip("/")

        if not base_cdn_url:
            error_worker("❌ IG_CDN_BASE_URL ist nicht gesetzt – öffentliche Video-URL kann nicht gebaut werden.")
            return ""

        return f"{base_cdn_url}/{quote(filename)}"

    # ---------------------------------------------------------
    # Container für Reel erstellen
    # ---------------------------------------------------------
    def _create_reel_container(self, video_url: str, caption: str) -> str:
        url = f"{self.base_url}/{self.ig_user_id}/media"

        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "share_to_feed": True,
            "access_token": self.access_token,
        }

        log_worker(f"📦 Erstelle IG-Container für Reel...")

        try:
            resp = requests.post(url, data=payload, timeout=30)
        except Exception as e:
            error_worker(f"❌ Netzwerkfehler beim Erstellen des Containers: {e}")
            return ""

        if resp.status_code != 200:
            error_worker(f"❌ Fehler beim Erstellen des Containers: {resp.status_code} – {resp.text}")
            return ""

        data = resp.json()
        creation_id = data.get("id")
        if not creation_id:
            error_worker(f"❌ Keine creation_id im Container-Response: {data}")
            return ""

        log_worker(f"✅ Container erstellt: creation_id={creation_id}")
        return creation_id

    # ---------------------------------------------------------
    # Container-Status pollen, bis FINISHED oder ERROR
    # ---------------------------------------------------------
    def _wait_for_container(self, creation_id: str, max_wait_seconds: int = 300, poll_interval: int = 5) -> bool:
        url = f"{self.base_url}/{creation_id}"
        params = {
            "fields": "status_code,status",
            "access_token": self.access_token,
        }

        log_worker("⏳ Warte auf IG-Container-Verarbeitung...")

        waited = 0
        while waited < max_wait_seconds:
            try:
                resp = requests.get(url, params=params, timeout=15)
            except Exception as e:
                error_worker(f"❌ Netzwerkfehler beim Polling des Containers: {e}")
                return False

            if resp.status_code != 200:
                error_worker(f"❌ Fehler beim Polling des Containers: {resp.status_code} – {resp.text}")
                return False

            data = resp.json()
            status_code = data.get("status_code")
            status = data.get("status")

            log_worker(f"📡 Container-Status: status_code={status_code}, status={status}")

            if status_code == "FINISHED":
                log_worker("✅ Container-Verarbeitung abgeschlossen.")
                return True
            if status_code == "ERROR":
                error_worker(f"❌ Container-Verarbeitung fehlgeschlagen: {data}")
                return False

            time.sleep(poll_interval)
            waited += poll_interval

        error_worker("❌ Timeout: Container-Verarbeitung nicht rechtzeitig abgeschlossen.")
        return False

    # ---------------------------------------------------------
    # Container veröffentlichen
    # ---------------------------------------------------------
    def _publish_container(self, creation_id: str) -> bool:
        url = f"{self.base_url}/{self.ig_user_id}/media_publish"
        payload = {
            "creation_id": creation_id,
            "access_token": self.access_token,
        }

        log_worker("🚀 Veröffentliche Reel über media_publish...")

        try:
            resp = requests.post(url, data=payload, timeout=30)
        except Exception as e:
            error_worker(f"❌ Netzwerkfehler beim Veröffentlichen des Reels: {e}")
            return False

        if resp.status_code != 200:
            error_worker(f"❌ Fehler beim Veröffentlichen des Reels: {resp.status_code} – {resp.text}")
            return False

        data = resp.json()
        media_id = data.get("id")
        if not media_id:
            warn_worker(f"⚠️ Kein media_id im Publish-Response: {data}")
        else:
            log_worker(f"✅ Reel veröffentlicht: media_id={media_id}")

        return True

    # ---------------------------------------------------------
    # Öffentliche Methode: Reel posten
    # ---------------------------------------------------------
    def post_reel(self, video_path: str, caption: str) -> bool:
        if not self.access_token or not self.ig_user_id:
            error_worker("❌ Instagram Access Token oder ig_user_id fehlen.")
            return False

        if not os.path.exists(video_path):
            error_worker(f"❌ Videodatei nicht gefunden: {video_path}")
            return False

        # 1) Öffentliche URL bauen
        video_url = self._build_public_video_url(video_path)
        if not video_url:
            error_worker("❌ Konnte keine öffentliche Video-URL erzeugen.")
            return False

        log_worker(f"🌐 Verwende Video-URL für IG: {video_url}")

        # 2) Container erstellen
        creation_id = self._create_reel_container(video_url, caption)
        if not creation_id:
            return False

        # 3) Auf Verarbeitung warten
        if not self._wait_for_container(creation_id):
            return False

        # 4) Container veröffentlichen
        return self._publish_container(creation_id)
