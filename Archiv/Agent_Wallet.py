import json
import os

# Pfad zu deiner lokalen Wallet-Datei (dort speichert er Adressen/Guthaben)
WALLET_FILE = "mein_art_wallet.json"

def load_wallet():
    if not os.path.exists(WALLET_FILE):
        return {"adresse": "Keine gesetzt", "balance": "0 ETH", "assets": []}
    with open(WALLET_FILE, "r") as f:
        return json.load(f)

def wallet_manager(befehl, wert):
    wallet = load_wallet()
    
    if befehl == "set_adresse":
        wallet["adresse"] = wert
        with open(WALLET_FILE, "w") as f:
            json.dump(wallet, f)
        return f"Wallet-Adresse wurde auf {wert} aktualisiert."
    
    elif befehl == "status":
        return f"Adresse: {wallet['adresse']} | Guthaben: {wallet['balance']}"
    
    return "Befehl unbekannt."