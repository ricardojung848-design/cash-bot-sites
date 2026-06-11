import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "logbuch.json")

def _load_log():
    if not os.path.exists(LOG_FILE):
        default_data = {"historie": []}
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=4, ensure_ascii=False)
        return default_data
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_log(data):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def log_aktion(typ, beschreibung, rollback_daten=None):
    data = _load_log()
    eintrag = {
        "id": len(data["historie"]) + 1,
        "typ": typ,
        "beschreibung": beschreibung,
        "rollback_daten": rollback_daten or {}
    }
    data["historie"].insert(0, eintrag)
    data["historie"] = data["historie"][:50]
    _save_log(data)

def undo_letzte_aktion():
    data = _load_log()
    if not data["historie"]:
        return "⚪ Keine Aktionen in der Historie vorhanden, die rückgängig gemacht werden könnten."

    letzte = data["historie"].pop(0)
    typ = letzte["typ"]
    rollback = letzte["rollback_daten"]
    beschreibung = letzte["beschreibung"]

    try:
        if typ == "galerie_add":
            galerie_pfad = os.path.join(BASE_DIR, "galerie.json")
            if os.path.exists(galerie_pfad):
                with open(galerie_pfad, "r", encoding="utf-8") as f:
                    galerie = json.load(f)
                
                titel_key = rollback.get("titel_key")
                if titel_key in galerie.get("werke", {}):
                    del galerie["werke"][titel_key]
                    with open(galerie_pfad, "w", encoding="utf-8") as f:
                        json.dump(galerie, f, indent=4, ensure_ascii=False)
                    _save_log(data)
                    return f"↩️ **Undo erfolgreich!**\n\nAuswirkung: {beschreibung} wurde vollständig rückgängig gemacht."
            
        elif typ == "wallet_tx":
            wallet_pfad = os.path.join(BASE_DIR, "agent_wallet_balance.json")
            if os.path.exists(wallet_pfad):
                with open(wallet_pfad, "r", encoding="utf-8") as f:
                    wallet = json.load(f)
                
                aktueller_stand = wallet.get("balance", 0.0)
                guthaben_aenderung = rollback.get("betrag", 0.0)
                wallet["balance"] = round(aktueller_stand - guthaben_aenderung, 2)
                
                with open(wallet_pfad, "w", encoding="utf-8") as f:
                    json.dump(wallet, f, indent=4, ensure_ascii=False)
                _save_log(data)
                return f"↩️ **Undo erfolgreich!**\n\nAuswirkung: Finanztransaktion zurückgebucht."

        elif typ == "steuer_add":
            steuer_pfad = os.path.join(BASE_DIR, "buchhaltung.json")
            if os.path.exists(steuer_pfad):
                with open(steuer_pfad, "r", encoding="utf-8") as f:
                    buchungen = json.load(f)
                
                buchung_id = rollback.get("id")
                if "eintraege" in buchungen:
                    buchungen["eintraege"] = [b for b in buchungen["eintraege"] if b.get("id") != buchung_id]
                    with open(steuer_pfad, "w", encoding="utf-8") as f:
                        json.dump(buchungen, f, indent=4, ensure_ascii=False)
                    _save_log(data)
                    return f"↩️ **Undo erfolgreich!**\n\nAuswirkung: Steuer-Buchung ID {buchung_id} gelöscht."

        return f"⚠️ Für den Aktionstyp '{typ}' wurde kein automatischer Rollback-Pfad gefunden."

    except Exception as e:
        return f"❌ Fehler beim Ausführen des Undo-Befehls: {str(e)}"