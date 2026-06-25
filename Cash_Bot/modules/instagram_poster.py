from typing import Dict, Any, Optional
from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager


class InstagramPoster:
    """
    PRO-Version des InstagramPosters:
    - Fungiert als High-Level-Interface für die Content-Veröffentlichung
    - Nutzt die asynchrone, modularisierte InstagramEngine über den EngineManager
    - Gibt strukturierte Status-Dictionaries zurück, die perfekt von der DialogEngine verarbeitet werden können
    """

    def __init__(self, engine_manager: EngineManager):
        self.engines = engine_manager
        
        # Holt die zugrundeliegende InstagramEngine aus dem globalen Manager
        if not self.engines.has("instagram"):
            raise RuntimeError("InstagramPoster benötigt eine registrierte InstagramEngine im EngineManager!")
        self.instagram_engine = self.engines.get("instagram")

    def post_reel(self, video_path: str, caption: str) -> Dict[str, Any]:
        """
        Initiiert den Veröffentlichungsprozess für ein Reel.
        Kombiniert die Engine-Logik mit einer strukturierten API-Rückgabe für das System.
        """
        log_doctor(f"InstagramPoster: Starte automatisierten Reel-Upload für '{video_path}'...")

        # Ausführen des gekapselten Upload-, Polling- und Publish-Prozesses
        success = self.instagram_engine.post_reel(video_path, caption)

        if not success:
            log_doctor("InstagramPoster-Fehler: Die Veröffentlichung des Reels ist fehlgeschlagen.")
            return {
                "status": "error",
                "message": "Upload oder Validierung auf den Meta-Servern fehlgeschlagen. Siehe Log-Datei."
            }

        log_doctor("InstagramPoster: 🎉 Pipeline erfolgreich durchlaufen. Reel ist live.")
        return {
            "status": "success",
            "video_path": video_path,
            "caption": caption,
            "message": "Reel wurde erfolgreich auf Instagram veröffentlicht."
        }


# Abwärtskompatibler Wrapper für ältere Skripte, die noch die alte Signatur erwarten
def instagram_poster_legacy(video_url: str, caption: str, engine_manager: EngineManager) -> Dict[str, Any]:
    """Erlaubt Legacy-Modulen den Aufruf der neuen Poster-Logik über den EngineManager."""
    poster = InstagramPoster(engine_manager)
    return poster.post_reel(video_url, caption)