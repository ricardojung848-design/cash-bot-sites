import os
import shutil
from datetime import datetime

def run_modul():
    backup_dir = "./Backups"
    core_files = ["Agent_Worker.py", "Agent_Telegram.py", "Agent_Wächter.py", "Agent_Architekt.py"]
    
    try:
        # Zeitstempel für den Backup-Unterordner erstellen
        zeitstempel = datetime.now().strftime("%Y%m%d_%H%M%S")
        aktueller_backup_pfad = os.path.join(backup_dir, zeitstempel)
        
        if not os.path.exists(aktueller_backup_pfad):
            os.makedirs(aktueller_backup_pfad)
            
        erfolgreich = []
        for datei in core_files:
            if os.path.exists(datei):
                shutil.copy(datei, os.path.join(aktueller_backup_pfad, datei))
                erfolgreich.append(datei)
                
        return (f"🤖 🔄 **Self-Update-System initialisiert!**\n\n"
                f"✅ Backup erfolgreich erstellt unter:\n`{aktueller_backup_pfad}`\n\n"
                f"📦 Gesicherte Core-Dateien:\n" + "\n".join([f"• {f}" for f in erfolgreich]) + 
                f"\n\nDas System ist nun bereit für tiefere Core-Updates.")
                
    except Exception as e:
        return f"❌ Fehler beim Erstellen des System-Backups: {str(e)}"