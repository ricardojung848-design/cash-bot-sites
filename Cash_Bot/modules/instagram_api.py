import os
import time
import requests
from urllib.parse import quote

from core.utils import log_worker, warn_worker, error_worker


class InstagramAPI:
    def __init__(self, access_token: str, ig_user_id: str, api_version: str = "v23.0") -> None:
        self.access_token = access_token
        self.ig_user_id = ig_user_id
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    # ---------------------------------------------------------
    # Öffentliche Video-URL bauen
    # ---------------------------------------------------------
    def _build_public_video_url(self, video_path: str) -> str:
        filename = os.path.basename(video_path)
        base_cdn_url = os.environ.get("IG_CDN_BASE_URL", "").strip()

        if not base_cdn_url:
            error_worker("❌ IG_CDN_BASE_URL fehlt – kann keine öffentliche Video-URL erzeugen.")
            return ""

        base_cdn_url = base_cdn_url.rstrip("/")
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
            "access_token": self.access_token
        }

        log_worker("📦 Erstelle IG-Container für Reel...")

        try:
            resp = requests.post(url, data=payload, timeout=30)
        except Exception as e:
            error_worker(f"❌ Netzwerkfehler beim Erstellen des Containers: {e}")
            return ""

        if resp.status_code != 200:
