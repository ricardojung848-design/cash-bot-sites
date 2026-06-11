import json
import os

WALLET_DB = "agent_wallet_balance.json"

def init_wallet():
    if not os.path.exists(WALLET_DB):
        with open(WALLET_DB, "w") as f:
            json.dump({"guthaben": 0.0, "transaktionen": []}, f)

def agent_add_funds(amount):
    with open(WALLET_DB, "r+") as f:
        data = json.load(f)
        data["guthaben"] += amount
        data["transaktionen"].append(f"Eingang: {amount} ETH")
        f.seek(0)
        json.dump(data, f)
    return f"Guthaben aktualisiert: {data['guthaben']} ETH"

def agent_status():
    with open(WALLET_DB, "r") as f:
        data = json.load(f)
    return f"Status: {data['guthaben']} ETH | Letzte Aktion: {data['transaktionen'][-1] if data['transaktionen'] else 'Keine'}"