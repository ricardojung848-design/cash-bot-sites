import json, os, ollama

REGISTRY_DATEI = "registry.json"
MODUL_ORDNER = "Module"

def architekt_erstelle_modul(name, code):
    if not os.path.exists(MODUL_ORDNER): os.makedirs(MODUL_ORDNER)
    pfad = f"{MODUL_ORDNER}/{name}.py"
    with open(pfad, "w", encoding="utf-8") as f: f.write(code)
    
    registry = {}
    if os.path.exists(REGISTRY_DATEI):
        with open(REGISTRY_DATEI, "r", encoding="utf-8") as f: registry = json.load(f)
    
    registry[name] = {"beschreibung": f"Modul für {name}", "pfad": pfad}
    with open(REGISTRY_DATEI, "w", encoding="utf-8") as f: json.dump(registry, f, indent=4)
    return True

def architekt_repariere_modul(name, fehler_meldung):
    pfad = f"{MODUL_ORDNER}/{name}.py"
    with open(pfad, "r", encoding="utf-8") as f: code = f.read()
    prompt = f'Der Code hat diesen Fehler: {fehler_meldung}. Repariere ihn. Gib NUR den Code aus:\n{code}'
    res = ollama.generate(model="deto_agent", prompt=prompt)
    neuer_code = res['response'].replace('```python', '').replace('```', '').strip()
    with open(pfad, "w", encoding="utf-8") as f: f.write(neuer_code)
    return True