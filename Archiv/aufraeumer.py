import os
import ast

MODUL_ORDNER = "Module"

def ist_datei_valide(dateipfad):
    """Prüft, ob die Datei echten, parsbaren Python-Code enthält."""
    try:
        with open(dateipfad, "r", encoding="utf-8") as f:
            inhalt = f.read().strip()
            
        if not inhalt: 
            return False # Datei ist leer
            
        # Prüfe, ob der Code überhaupt syntaktisch korrekt ist
        ast.parse(inhalt)
        return True
    except Exception as e:
        print(f"DEBUG: Datei {dateipfad} ist ungültig: {e}")
        return False

def ordner_bereinigen():
    if not os.path.exists(MODUL_ORDNER):
        print(f"Ordner {MODUL_ORDNER} existiert nicht.")
        return

    geloeschte_dateien = 0
    gepruefte_dateien = 0

    for datei in os.listdir(MODUL_ORDNER):
        if datei.endswith(".py"):
            gepruefte_dateien += 1
            pfad = os.path.join(MODUL_ORDNER, datei)
            
            if not ist_datei_valide(pfad):
                print(f"⚠️ Lösche defekte Datei: {datei}")
                try:
                    os.remove(pfad)
                    geloeschte_dateien += 1
                except Exception as e:
                    print(f"❌ Fehler beim Löschen von {datei}: {e}")
            else:
                print(f"✅ Datei {datei} ist okay.")

    print(f"\nZusammenfassung: {gepruefte_dateien} Dateien geprüft, {geloeschte_dateien} gelöscht.")

if __name__ == "__main__":
    ordner_bereinigen()
    print("Fertig! Der Module-Ordner ist nun sauber.")