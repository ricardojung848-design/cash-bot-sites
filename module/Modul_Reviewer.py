import ollama
import os

def run_modul(modul_name):
    """
    Scannt ein Modul, sucht nach Fehlern und gibt eine Empfehlung ab.
    """
    pfad = f"Module/{modul_name}.py"
    if not os.path.exists(pfad):
        return "❌ Review fehlgeschlagen: Datei nicht gefunden."

    with open(pfad, "r", encoding="utf-8") as f:
        code = f.read()

    prompt = (
        f"Analysiere diesen Python-Code als Senior-Entwickler auf:\n"
        f"1. Syntax-Fehler\n"
        f"2. Sicherheitslücken (z.B. unsichere Importe)\n"
        f"3. Effizienz und Lesbarkeit.\n"
        f"Wenn der Code okay ist, antworte nur mit 'OK'. "
        f"Wenn er Fehler hat, erkläre kurz den Fehler und schlage den korrigierten Code vor.\n\n"
        f"CODE:\n{code}"
    )

    res = ollama.generate(model="deto_agent", prompt=prompt)
    analyse = res['response'].strip()
    
    return analyse