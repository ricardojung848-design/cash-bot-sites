# modules/hook_generator.py

from typing import List
from modules.hook_analyzer import get_top_hooks

def generate_hook(thema: str) -> str:
    """
    Baut neue Hooks basierend auf den erfolgreichsten Mustern.
    Wenn keine Daten vorhanden sind → fallback Hooks.
    """

    top = get_top_hooks()

    if not top:
        return f"🔥 {thema} meistern – ohne Zeit zu verschwenden."

    # Nimm das beste Muster und ersetze das Thema
    best = top[0]

    # Einfacher Pattern-Replacer
    if "{thema}" in best:
        return best.replace("{thema}", thema)

    # Wenn kein Platzhalter existiert → Thema intelligent einfügen
    return f"{best} ({thema})"
