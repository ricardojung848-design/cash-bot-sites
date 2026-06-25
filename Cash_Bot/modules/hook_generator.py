from typing import List, Optional
from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager
from modules.hook_analyzer import HookAnalyzer


class HookGenerator:
    """
    PRO-Version des HookGenerators:
    - Nutzt die datenbasierten Erkenntnisse des HookAnalyzers über den EngineManager
    - Generiert dynamisch optimierte Hooks für neue Content-Themen
    - Fällt intelligent auf performante Standard-Muster zurück, wenn die Datenbasis leer ist
    """

    def __init__(self, engine_manager: EngineManager):
        self.engines = engine_manager
        
        # Sicherstellen, dass der HookAnalyzer bereitsteht
        if not self.engines.has("hook_analyzer"):
            self.analyzer = HookAnalyzer(self.engines)
        else:
            self.analyzer = self.engines.get("hook_analyzer")

    def generate_hook(self, thema: str) -> str:
        """
        Baut einen neuen Hook basierend auf den erfolgreichsten historischen Mustern.
        Fällt bei leerer Datenbank auf vordefinierte, psychologisch optimierte Hooks zurück.
        """
        try:
            top_hooks = self.analyzer.get_top_hooks(n=3)
        except Exception as e:
            log_doctor(f"HookGenerator-Warnung: Konnte Top-Hooks nicht laden: {e}")
            top_hooks = []

        # Fallback-Muster, falls noch keine oder zu wenige Analytics-Events existieren
        if not top_hooks:
            log_doctor(f"HookGenerator: Keine historischen Daten gefunden. Nutze Fallback für Thema '{thema}'.")
            return f"🔥 Wie du {thema} meisterst – ohne Zeit zu verschwenden."

        # Nimm das aktuell erfolgreichste Muster aus der DB
        best_pattern = top_hooks[0]

        # Flexibler Pattern-Replacer für dynamische Hooks
        # Erwartet im Muster Platzhalter wie {thema}, {Thema} oder [thema]
        lowercase_pattern = best_pattern.lower()
        
        if "{thema}" in lowercase_pattern:
            # Ersetzt den Platzhalter case-insensitive
            hook = best_pattern.replace("{thema}", thema).replace("{Thema}", thema)
            log_doctor(f"HookGenerator: Erfolgreiches Muster adaptiert -> {hook}")
            return hook

        # Wenn kein expliziter Platzhalter existiert -> Thema intelligent als Kontext anfügen
        hook = f"{best_pattern} — Fokus: {thema}"
        log_doctor(f"HookGenerator: Muster ohne Platzhalter kombiniert -> {hook}")
        return hook


# Abwärtskompatibler Einstiegspunkt (falls alte Skripte die Funktion direkt importieren)
def generate_hook_legacy(thema: str, engine_manager: EngineManager) -> str:
    """Erlaubt Legacy-Modulen den Aufruf der neuen Generator-Logik."""
    generator = HookGenerator(engine_manager)
    return generator.generate_hook(thema)