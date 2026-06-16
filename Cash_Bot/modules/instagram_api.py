# modules/instagram_api.py

import requests
from typing import Dict, Any
from core.utils import log_worker, error_worker

class InstagramAPI:
    def __init__(self, access_token: str, ig_user_id: str) -> None:
        self.access_token = access_token
        self.ig_user_id = ig_user_id
        self.base_url = "https://graph.facebook.com/v18.0"

    def _post(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        params["access_token"] = self.access_token

        try:
            r = requests.post(url, params=params)
            data = r.json()
            if "error" in data:
                error_worker(f"Instagram API Error: {data['error']}")
            return data
        except Exception as e:
            error_worker(f"Instagram API Request Failed: {e}")
            return {"error": str(e)}

    def upload_reel(self, video_url: str, caption: str) -> Dict[str, Any]:
        log_worker("📤 Sende Reel an Instagram...")
        params = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "share_to_feed": "true",
        }
        return self._post(f"{self.ig_user_id}/media", params)

    def publish_media(self, creation_id: str) -> Dict[str, Any]:
        log_worker("🚀 Veröffentliche Reel...")
        params = {"creation_id": creation_id}
        return self._post(f"{self.ig_user_id}/media_publish", params)
