import subprocess
import sys

def run_code(code: str) -> str:
    """Führt übergebenen Python-Code sicher in einem Subprozess aus."""
    if not code.strip():
        return "Fehler: Kein Code zum Ausführen übergeben."
        
    try:
        # Führt den Code aus und fängt die Rückgabe ab
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=15,
            encoding='utf-8'
        )
        
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        if error:
            return f"❌ FEHLER IM CODE:\n{error}"
        return output if output else "✅ Code erfolgreich ausgeführt (keine Bildschirmausgabe)."
        
    except subprocess.TimeoutExpired:
        return "❌ Fehler: Die Code-Ausführung hat zu lange gedauert (Timeout)."
    except Exception as e:
        return f"❌ Unerwarteter Fehler: {str(e)}"