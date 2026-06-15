from typing import Dict, Any
from core.utils import log_worker, error_worker
from modules.instagram_api import InstagramAPI

class InstagramPoster:
    def __init__(self, access_token: str, ig_user_id: str) -> None:
        self.api = InstagramAPI(access_token, ig_user_id)

    def post_reel(self, video_url: str, caption: str) -> Dict[str, Any]:
        """
        Upload + Publish eines Reels.
        """
        log_worker("📤 Starte Instagram Reel Upload...")

        creation = self.api.upload_reel(video_url, caption)
        if "id" not in creation:
            error_worker("❌ Upload fehlgeschlagen.")
            return creation

        creation_id = creation["id"]

        publish = self.api.publish_media(creation_id)
        if "id" not in publish:
            error_worker("❌ Publish fehlgeschlagen.")
            return publish

        log_worker(f"🎉 Reel veröffentlicht! ID: {publish['id']}")
        return publish
