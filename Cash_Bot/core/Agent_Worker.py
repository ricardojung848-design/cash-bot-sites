# === NEU HINZUFÜGEN IN core/Logik.py ===

def process_ki_anfrage(text):
    """
    Verarbeitet KI-Anfragen, die vom Agent_Worker kommen.
    """
    log_worker(f"KI-Anfrage wird bearbeitet: {text}")
    
    # Hier kommt deine eigentliche KI-Logik rein
    # Zum Testen erst einmal eine einfache Antwort:
    antwort = f"System hat deine Anfrage empfangen: '{text}'"
    
    return antwort