import os
import requests
from typing import Dict, Any

from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager


class InstagramTokenRefresher:
    """
    PRO-Version des InstagramTokenRefreshers:
    - Erneuert kurzlebige Meta-Tokens in langlebige Access Tokens (60 Tage)
    - Entfernt die 'cashbot_config.json' und speichert den Token direkt im SQLite-State
    - Bezieht sensible App-Credentials sicher über Umgebungsvariablen
    """

    def __init__(self, engine_manager: EngineManager):
        self.engines = engine_manager
        if not self.engines.has("state"):
            raise RuntimeError("InstagramTokenRefresher benötigt einen registrierten State-Manager im EngineManager!")
        self.state = self.engines.get("state")
        
        # Basis-URL für Meta Graph API (zukunftssicher auf v23.0 angehoben wie die InstagramEngine)
        self.base_url = "https://graph.facebook.com/v23.0"

    def refresh(self) -> str:
        """
        Führt den Token-Refresh-Call gegen die Meta API aus und sichert 
        den neuen Token transaktionssicher in der relationalen Datenbank.
        """
        # Aktuellen Token aus der SQLite-Datenbank laden
        instagram_data = self.state.get_state("instagram_config", {"access_token": ""})
        current_token = instagram_data.get("access_token", os.environ.get("IG_ACCESS_TOKEN", "")).strip()

        if not current_token:
            log_doctor("InstagramTokenRefresher-Fehler: Kein Ausgangs-Token im State oder in der Umgebung gefunden.")
            return "❌ Kein aktiver Token zum Erneuern vorhanden."

        # App Credentials aus der Umgebung laden
        client_id = os.environ.get("IG_CLIENT_ID", "DEINE_APP_ID").strip()
        client_secret = os.environ.get("IG_CLIENT_SECRET", "DEIN_APP_SECRET").strip()

        url = f"{self.base_url}/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "fb_exchange_token": current_token
        }

        log_doctor("InstagramTokenRefresher: Sende Refresh-Anforderung an Meta...")

        try:
            response = requests.get(url, params=params, timeout=15)
            data = response.json()

            if "access_token" not in data:
                log_doctor(f"InstagramTokenRefresher-Fehler: API verweigert Refresh: {data}")
                return "❌ Token konnte nicht erneuert werden."

            new_token = data["access_token"]

            # Token im SQLite DB-State aktualisieren
            instagram_data["access_token"] = new_token
            instagram_data["last_refresh"] = os.environ.get("CURRENT_TIMESTAMP", "")
            self.state.set_state("instagram_config", instagram_data)

            log_doctor("InstagramTokenRefresher: 🔄 Instagram Access Token erfolgreich in SQLite erneuert.")
            return "🔄 Token erneuert."

        except Exception as e:
            log_doctor(f"InstagramTokenRefresher-Kritisch: Verbindung fehlgeschlagen: {e}")
            return f"❌ Fehler: {e}"


# Abwärtskompatibler Wrapper für Altsysteme
def refresh_instagram_token_legacy(engine_manager: EngineManager) -> str:
    """Erlaubt Legacy-Modulen den Trigger des neuen Refreshers."""
    refresher = InstagramTokenRefresher(engine_manager)
    return refresher.refresh()