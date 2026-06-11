import json
import os

# Pfad zur lokalen Galerie-Datenbank
DB_FILE = os.path.join(os.path.dirname(__file__), "galerie.json")

def load_galerie():
    """Lädt die Galerie aus der JSON-Datei."""
    if not os.path.exists(DB_FILE):
        default_data = {"werke": {}}
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=4, ensure_ascii=False)
        return default_data
    
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_galerie(data):
    """Speichert die Galerie in die JSON-Datei."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def werk_hinzufuegen(titel, serie, masse, medium, preis, standort="Atelier Aachen", status="Verfügbar"):
    """Fügt ein neues Kunstwerk zum Portfolio hinzu."""
    data = load_galerie()
    titel_key = titel.strip().lower()
    
    if titel_key in data["werke"]:
        return f"⚠️ Ein Werk mit dem Titel '{titel}' existiert bereits im Portfolio."
    
    data["werke"][titel_key] = {
        "titel": titel.strip(),
        "serie": serie.strip() if serie else "Einzelwerk",
        "masse": masse.strip(),
        "medium": medium.strip(),
        "preis": float(preis),
        "standort": standort.strip(),
        "status": status.strip(),
        "jahr": 2026
    }
    
    save_galerie(data)
    return f"🎨 **Werk erfolgreich erfasst!**\n\nTitel: {titel}\nSerie: {serie}\nMaße: {masse}\nPreis: {preis} €"

def werk_status_update(titel, neuer_status, neuer_standort=None):
    """Aktualisiert Status und optional den Standort eines Werkes (z.B. bei Verkauf oder Ausstellung)."""
    data = load_galerie()
    titel_key = titel.strip().lower()
    
    if titel_key not in data["werke"]:
        return f"❌ Werk '{titel}' wurde im Portfolio nicht gefunden."
    
    data["werke"][titel_key]["status"] = neuer_status.strip()
    if neuer_standort:
        data["werke"][titel_key]["standort"] = neuer_standort.strip()
        
    save_galerie(data)
    return f"🔄 **Status-Update für '{data['werke'][titel_key]['titel']}'**\nStatus: {neuer_status}" + (f"\nStandort: {neuer_standort}" if neuer_standort else "")

def galerie_liste(filter_serie=None):
    """Gibt eine Übersicht aller Werke aus, optional gefiltert nach Serie."""
    data = load_galerie()
    if not data["werke"]:
        return "🖼️ Das Portfolio ist aktuell noch leer."
        
    ausgabe = "🖼️ **DETO Portfolio-Übersicht:**\n"
    if filter_serie:
        ausgabe = f"🖼️ **Werke der Serie '{filter_serie}':**\n"
        
    zaehler = 0
    for key, werk in data["werke"].items():
        if filter_serie and filter_serie.lower().strip() != werk["serie"].lower().strip():
            continue
            
        status_emoji = "🟢" if werk["status"].lower() == "verfügbar" else "🔴" if werk["status"].lower() == "verkauft" else "🟡"
        ausgabe += f"\n{status_emoji} **{werk['titel']}** ({werk['jahr']})\n"
        ausgabe += f"   Format: {werk['masse']} | Medium: {werk['medium']}\n"
        ausgabe += f"   Serie: {werk['serie']} | Preis: {werk['preis']} €\n"
        ausgabe += f"   Ort: {werk['standort']}\n"
        zaehler += 1
        
    if zaehler == 0:
        return f"ℹ️ Keine Werke in der Serie '{filter_serie}' gefunden."
        
    return ausgabe