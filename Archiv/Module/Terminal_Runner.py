import sys
import io
import contextlib

def run_modul():
    return "Terminal-Runner bereit. Nutze '/exec [dein code]' im Chat."

def run_code(code):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        try:
            exec(code)
            ergebnis = buffer.getvalue()
            if ergebnis.strip():
                return ergebnis.strip()
            else:
                return "✅ Code erfolgreich ausgeführt (kein Output)."
        except Exception as e:
            return f"❌ FEHLER IM CODE:\n{str(e)}"