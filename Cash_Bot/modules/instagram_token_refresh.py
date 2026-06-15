# modules/instagram_token_refresh.py

import requests
from core.utils import log_worker, error_worker
from core.utils import save_json, load_json
from core.utils import CONFIG_DIR
import os

CONFIG_FILE = os.path.join(CONFIG_DIR, "cashbot_config.json")

class InstagramTokenRefresher:
    def __init__(self, access_token: str) -> None:
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"

    def refresh(self) -> str:
        url = f"{self.base_url}/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": "DEINE_APP_ID",
            "client_secret": "DEIN_APP_SECRET",
            "fb_exchange_token": self.access_token
        }

        try:
            r = requests.get(url, params=params)
            data = r.json()

            if "access_token" not in data:
                error_worker(f"Token Refresh Error: {data}")
                return "❌ Token konnte nicht erneuert werden."

            new_token = data["access_token"]

            cfg = load_json(CONFIG_FILE, {})
            cfg["instagram_api"]["access_token"] = new_token
            save_json(CONFIG_FILE, cfg)

            log_worker("🔄 Instagram Token erfolgreich erneuert.")
            return "🔄 Token erneuert."

        except Exception as e:
            error_worker(f"Token Refresh Exception: {e}")
            return f"❌ Fehler: {e}"
