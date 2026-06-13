import os

def run_modul():
    try:
        # Versuch, eine Datei zu öffnen
        with open('nicht_existent.txt', 'r') as file:
            pass  # Leere Operation, um Fehler zu simulieren
    except FileNotFoundError:
        print("Datei existiert nicht.")
    else:
        print("Datei gefunden.")

if __name__ == "__main__":
    run_modul()