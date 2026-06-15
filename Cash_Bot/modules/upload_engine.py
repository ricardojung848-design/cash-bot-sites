# modules/upload_engine.py

import os
import requests
from core.utils import log_worker, error_worker

class UploadEngine:
    def __init__(self, upload_url: str, api_key: str = None) -> None:
        self.upload_url = upload_url
        self.api_key = api_key

    def upload(self, file_path: str) -> str:
        """
        Lädt eine Datei hoch und gibt die öffentliche URL zurück.
        """
        try:
            log_worker(f"📤 Lade Datei hoch: {file_path}")

            with open(file_path, "rb") as f:
                files = {"file": f}
                headers = {}

                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"

                r = requests.post(self.upload_url, files=files, headers=headers)
                data = r.json()

                if "url" not in data:
                    error_worker(f"Upload Error: {data}")
                    return None

                return data["url"]

        except Exception as e:
            error_worker(f"Upload Exception: {e}")
            return None
