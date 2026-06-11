import os
import requests
from dotenv import load_dotenv

# Konfiguration laden
load_dotenv()
PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_API_SECRET = os.getenv("PINATA_API_SECRET")

def mint_art_to_ipfs(file_path):
    """Lädt das Bild hoch und gibt den IPFS-Link zurück"""
    print(f"🚀 Starte NFT-Prozess für: {file_path}")
    
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_API_SECRET
    }
    
    try:
        with open(file_path, 'rb') as file:
            response = requests.post(url, files={'file': file}, headers=headers)
            
        if response.status_code == 200:
            ipfs_hash = response.json()['IpfsHash']
            link = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
            print(f"✅ Hochgeladen! IPFS Hash: {ipfs_hash}")
            return link
        else:
            print(f"❌ Upload fehlgeschlagen: {response.text}")
            return None
    except Exception as e:
        print(f"Fehler: {e}")
        return None

# Test-Ausführung
if __name__ == "__main__":
    # Stelle sicher, dass ein Bild namens 'test_kunst.jpg' im Ordner liegt
    bild_pfad = "test_kunst.jpg" 
    ergebnis_link = mint_art_to_ipfs(bild_pfad)
    
    if ergebnis_link:
        print(f"🎨 Dein NFT ist bereit! Hier ist die öffentliche URL: {ergebnis_link}")