import os
import shutil

def run_modul():
    deleted_folders = 0
    deleted_files = 0
    
    # Pfade, die durchsucht werden sollen (Hauptverzeichnis und Module)
    pfade_zum_pruefen = [".", "./Module"]
    
    for basis_pfad in pfade_zum_pruefen:
        if not os.path.exists(basis_pfad):
            continue
            
        for root, dirs, files in os.walk(basis_pfad, topdown=False):
            # 1. __pycache__ Ordner löschen
            for name in dirs:
                if name == "__pycache__":
                    vollstaendiger_pfad = os.path.join(root, name)
                    try:
                        shutil.rmtree(vollstaendiger_pfad)
                        deleted_folders += 1
                    except Exception:
                        pass
                        
            # 2. Einzelne .pyc Dateien löschen
            for name in files:
                if name.endswith(".pyc"):
                    vollstaendiger_pfad = os.path.join(root, name)
                    try:
                        os.remove(vollstaendiger_pfad)
                        deleted_files += 1
                    except Exception:
                        pass
                        
    return f"🧹 Bereinigung abgeschlossen!\n• Gelöschte Cache-Ordner: {deleted_folders}\n• Gelöschte .pyc-Dateien: {deleted_files}"