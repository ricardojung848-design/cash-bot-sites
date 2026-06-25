import re
from datetime import datetime
from typing import Any, Dict, List

from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager


class KeywordEngine:
    """
    PRO-Version der KeywordEngine:
    - Generiert SEO-Longtails und SERP-Varianten basierend auf einem Hauptthema.
    - Berechnet dynamische Cluster-Größen mit optionalem Trend-Boost.
    - Speichert generierte Keyword-Cluster persistent in der SQLite-Datenbank ab.
    """

    def __init__(self, engine_manager: EngineManager):
        self.engines = engine_manager
        if not self.engines.has("state"):
            raise RuntimeError("KeywordEngine benötigt einen registrierten State-Manager im EngineManager!")
        self.state = self.engines.get("state")

    def normalize(self, text: str) -> str:
        """Bereinigt den Text von Sonderzeichen für saubere Suchphrasen."""
        return re.sub(r"[^a-zA-Z0-9äöüÄÖÜß ]", "", text).strip()

    def is_trend_topic(self, thema: str) -> bool:
        """Prüft, ob das Thema aktuelle Trend-Keywords oder das aktuelle Jahr beinhaltet."""
        thema_low = thema.lower()
        trend_keywords = ["2026", "trend", "neu", "ai", "ki", "automation", "tiktok", "instagram", "viral"]
        return any(tk in thema_low for tk in trend_keywords)

    def generate_longtails(self, base: str) -> List[str]:
        """Erstellt klassische informationelle Longtail-Keywords."""
        return [
            f"{base} erklärung",
            f"{base} beispiele",
            f"{base} workflow",
            f"{base} fehler vermeiden",
            f"{base} best practices",
            f"{base} tools",
            f"{base} für anfänger",
            f"{base} für profis",
            f"{base} anleitung",
            f"{base} tipps",
        ]

    def generate_serp_variants(self, base: str) -> List[str]:
        """Erstellt gezielte Suchanfragen-Varianten für Suchergebnisseiten (SERPs)."""
        return [
            f"was ist {base}",
            f"wie funktioniert {base}",
            f"{base} vorteile",
            f"{base} nachteile",
            f"{base} kosten",
            f"{base} nutzen",
            f"{base} guide",
            f"{base} tutorial",
        ]

    def dynamic_cluster_size(self, thema: str) -> int:
        """Bestimmt die Zielgröße des Clusters basierend auf der Komplexität des Suchbegriffs."""
        thema_low = thema.lower()
        if len(thema_low) < 10:
            return 8   # Enges Nischenthema
        if len(thema_low) < 20:
            return 15  # Mittleres Thema
        return 25      # Breites Themenfeld

    def generate_keyword_cluster(self, thema: str) -> Dict[str, Any]:
        """
        Generiert ein vollständiges, aggressiv optimiertes Keyword-Cluster.
        Sichert das Ergebnis automatisch in der relationalen Datenbank.
        """
        thema_clean = self.normalize(thema)
        base = thema_clean.lower()

        if not base:
            log_doctor("KeywordEngine-Warnung: Leeres Thema übergeben.")
            return {"thema": "", "count": 0, "keywords": [], "trend_boost": False}

        cluster: List[str] = [base]

        # Ergänzen der Listen-Varianten
        cluster.extend(self.generate_longtails(base))
        cluster.extend(self.generate_serp_variants(base))

        # Dynamische Größenberechnung inklusive Trend-Prüfung
        size = self.dynamic_cluster_size(thema_clean)
        is_trend = self.is_trend_topic(thema_clean)

        if is_trend:
            size = int(size * 1.5)
            log_doctor(f"KeywordEngine: Trend-Boost aktiv für '{thema_clean}' (+50% Volumen).")

        # Aggressiver Deckel bei maximal 40 Keywords
        size = min(size, 40)
        cluster = cluster[:size]

        result = {
            "thema": thema_clean,
            "count": len(cluster),
            "keywords": cluster,
            "trend_boost": is_trend,
            "timestamp": datetime.now().isoformat()
        }

        # Daten-Persistenz im SQLite-Zustand verankern
        try:
            seo_history = self.state.get_state("seo_keyword_history", {"clusters": {}})
            seo_history["clusters"][base] = result
            self.state.set_state("seo_keyword_history", seo_history)
            log_doctor(f"KeywordEngine: 🎉 Cluster für '{thema_clean}' ({len(cluster)} Keywords) in DB gesichert.")
        except Exception as e:
            log_doctor(f"KeywordEngine-Fehler beim Sichern in der DB: {e}")

        return result


# Abwärtskompatibler Einstiegspunkt für ältere Programmteile
def generate_keyword_cluster_legacy(thema: str, engine_manager: EngineManager) -> Dict[str, Any]:
    """Erlaubt Legacy-Modulen den Aufruf der neuen Cluster-Logik."""
    engine = KeywordEngine(engine_manager)
    return engine.generate_keyword_cluster(thema)