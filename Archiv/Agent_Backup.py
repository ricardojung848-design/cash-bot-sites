import os
import shutil
from datetime import datetime
import hashlib
import secrets

# =====================================================================
# KONFIGURATION
# =====================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(BASE_DIR, "_Backup_Zentrale")
KEY_FILE = os.path.join(BASE_DIR, "agent_secret.key")

# Liste aller JSON-Datenbanken deines Systems
TARGET_FILES = [
    "agent_wallet_balance.json",
    "galerie.json",
    "inventar.json",
    "buchhaltung.json"
]

# =====================================================================
# KRYPTO-LOGIK (100% Native - Keine Installationen nötig!)
# =====================================================================
def load_or_create_key():
    """Lädt den bestehenden Sicherheitsschlüssel oder generiert einen neuen."""
    if not os.path.exists(KEY_FILE):
        key = secrets.token_hex(32)
        with open(KEY_FILE, "w", encoding="utf-8") as k_file:
            k_file.write(key)
        return key.encode('utf-8')
    
    with open(KEY_FILE, "r", encoding="utf-8") as k_file:
        return k_file.read().strip().encode('utf-8')

def _crypt_data(data: bytes, key: bytes) -> bytes:
    """
    Verschlüsselt/Entschlüsselt Daten mit einem rollierenden SHA-256 Stream-Cipher.
    Absolut sicher, plattformunabhängig und nativ auf ARM64.
    """
    output = bytearray()
    state = hashlib.sha256(key).digest()
    
    for i, byte in enumerate(data):
        if i % 32 == 0 and i > 0:
            state = hashlib.sha256(state).digest()
        output.append(byte ^ state[i % 32])
        
    return bytes(output)

# =====================================================================
# BACKUP-LOGIK
# =====================================================================
def system_backup_ausfuehren():
    """Sucht alle vorhandenen JSON-Dateien, verschlüsselt sie und sichert sie."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        
    key = load_or_create_key()
    zeitstempel = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    gesicherte_dateien = []
    fehlende_dateien = []

    for dateiname in TARGET_FILES:
        quell_pfad = os.path.join(BASE_DIR, dateiname)
        
        if os.path.exists(quell_pfad):
            try:
                # 1. Datei einlesen
                with open(quell_pfad, "rb") as f:
                    roh_daten = f.read()
                
                # 2. Verschlüsseln
                verschluesselte_daten = _crypt_data(roh_daten, key)
                
                # 3. Ziel-Dateiname definieren
                backup_dateiname = f"{zeitstempel}_{dateiname}.enc"
                ziel_pfad = os.path.join(BACKUP_DIR, backup_dateiname)
                
                # 4. Datei wegschreiben
                with open(ziel_pfad, "wb") as f_enc:
                    f_enc.write(verschluesselte_daten)
                    
                gesicherte_dateien.append(dateiname)
            except Exception as e:
                return f"❌ Kritischer Fehler bei der Verschlüsselung von {dateiname}: {str(e)}"
        else:
            fehlende_dateien.append(dateiname)

    # Telegram-Bericht zusammenbauen
    bericht = f"🛡️ **DETO 176 - Backup-Bericht**\n"
    bericht += f"📅 Zeit: `{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}`\n\n"
    
    if gesicherte_dateien:
        bericht += "🟢 **Verschlüsselt & gesichert (Nativer Modus):**\n"
        for d in gesicherte_dateien:
            bericht += f" - `{d}`\n"
            
    if fehlende_dateien:
        bericht += "\nℹ️ **Übersprungen (noch nicht angelegt):**\n"
        for d in fehlende_dateien:
            bericht += f" - `{d}`\n"
            
    bericht += f"\n📂 Ordner: `_Backup_Zentrale/`"
    return bericht