import importlib.util
import os

def run_modul(modul_name):
    """Führt eine einfache Integritätsprüfung durch."""
    pfad = f"Module/{modul_name}.py"
    if not os.path.exists(pfad):
        return "❌ Modul nicht gefunden."

    try:
        # Dynamisch laden
        spec = importlib.util.spec_from_file_location(modul_name, pfad)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        
        # Test: Existiert run_modul?
        if not hasattr(modul, 'run_modul'):
            return "❌ Test fehlgeschlagen: Funktion 'run_modul' fehlt."
        
        return "OK"
    except Exception as e:
        return f"❌ Test fehlgeschlagen mit Fehler: {str(e)}"