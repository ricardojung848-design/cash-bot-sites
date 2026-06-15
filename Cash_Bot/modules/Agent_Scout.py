import json
import os
import urllib.request
import urllib.parse
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCOUT_LOG = os.path.join(BASE_DIR, "scout_funde.json")

# =====================================================================
# KI-KONFIGURATION (HYBRID, DYNAMISCH & INTERAKTIV)
# =====================================================================
# 1. LM Studio Einstellungen (Exzellent für komplexe Analysen)
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
LM_STUDIO_MODEL = "mistralai/mistral-7b-instruct-v0.3"

# 2. Ollama Einstellungen
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_DEFAULT = "llama3"       # Das absolute Sicherheitsnetz (Plan B, falls du 'n' drückst)
OLLAMA_FAST = "gemma2:2b"       # IDEE 3: Schnelles, kleines Modell für Kurztexte (z.B. gemma2:2b oder qwen2.5:1.5b)
OLLAMA_DEEP = "llama3"         # Starkes Modell für lange Textwüsten

# Hauptstrategie: "fallback" (Erst LM Studio versuchen, sonst Ollama-Backup)
KI_STRATEGIE = "fallback"
# =====================================================================

# Hier trägst du Feeds oder öffentliche Kultur-/Jobseiten ein, die du überwachst
ZIEL_QUELLEN = [
    "https://www.bundesweit-kreativ.de/feeder/rss/rss.xml", # Beispiel für Kreativ-Ausschreibungen
    # Füge hier weitere regionale RSS-Feeds oder Kultur-Portale hinzu
]

def _load_scout_log():
    if not os.path.exists(SCOUT_LOG):
        default_data = {"bekannte_links": [], "treffer": []}
        with open(SCOUT_LOG, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=4, ensure_ascii=False)
        return default_data
    with open(SCOUT_LOG, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if "treffer" not in data:
                data["treffer"] = []
            return data
        except Exception:
            return {"bekannte_links": [], "treffer": []}

def _save_scout_log(data):
    with open(SCOUT_LOG, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def _html_bereinigen(html_text):
    """Entfernt HTML-Tags und Skripte, um reinen Text zu isolieren."""
    clean = re.compile('<.*?>|&([a-z0-9]+|#[0-9]+|#x[0-9a-f]+);')
    text = re.sub(clean, ' ', html_text)
    return " ".join(text.split())

def _seite_abrufen(url):
    """Lädt den Inhalt einer Webseite ohne externe Abhängigkeiten."""
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) DETO-Art-Scout/1.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"[Scout-Fehler] Konnte {url} nicht abrufen: {str(e)}")
        return None

# ---------------------------------------------------------------------
# AUTOMATISCHER DOWNLOAD & PLAN B (IDEE 1)
# ---------------------------------------------------------------------
def _hole_installierte_ollama_modelle():
    """Gibt eine Liste aller lokal installierten Ollama-Modelle zurück."""
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3) as response:
            lokale_modelle = json.loads(response.read().decode("utf-8"))
            return [m["name"] for m in lokale_modelle.get("models", [])]
    except Exception:
        return []

def _ollama_modell_mit_erlaubnis_laden(model_name):
    """
    Prüft das Modell. Wenn es fehlt, wird aktiv nachgefragt.
    IDEE 1: Bei Ablehnung ('n') greift automatisch der Plan-B-Fallback (OLLAMA_DEFAULT).
    """
    installierte = _hole_installierte_ollama_modelle()
    if not installierte:
        return None # Ollama läuft wohl gerade nicht

    if model_name in installierte or f"{model_name}:latest" in installierte:
        return model_name

    print("\n" + "="*60)
    print(f"🤖 AGENT-HINWEIS: Ich würde für die Analyse gerne '{model_name}' laden.")
    print("   Dieses Modell fehlt aktuell noch auf deiner Festplatte.")
    print("="*60)
    
    entscheidung = input(f"❓ Darf ich '{model_name}' jetzt via Ollama herunterladen? (j/n): ").strip().lower()
    
    if entscheidung == 'j':
        print(f"📥 Download gestartet für '{model_name}'...")
        print("🚀 Bitte warten, ich hole das Modell live von den Servern...")
        pull_url = "http://localhost:11434/api/pull"
        payload = {"name": model_name, "stream": False}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(pull_url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=1200) as response:
                res = json.loads(response.read().decode("utf-8"))
                if res.get("status") == "success":
                    print(f"✅ Download beendet! Modell '{model_name}' steht bereit.\n")
                    return model_name
        except Exception as e:
            print(f"❌ Download fehlgeschlagen: {e}")
    
    # IDEE 1: Plan-B-Fallback bei 'n' oder Fehler
    print(f"🔄 Plan-B aktiviert: Weiche auf installiertes Standard-Modell '{OLLAMA_DEFAULT}' aus.\n")
    return OLLAMA_DEFAULT

# ---------------------------------------------------------------------
# BACKEND-ANSTEUERUNG
# ---------------------------------------------------------------------
def _analysiere_mit_lm_studio(prompt):
    payload = {
        "model": LM_STUDIO_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "response_format": {"type": "json_object"}
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(LM_STUDIO_URL, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as response:
        res = json.loads(response.read().decode("utf-8"))
        return json.loads(res["choices"][0]["message"]["content"])

def _analysiere_mit_ollama(prompt, model_to_use):
    aktives_modell = _ollama_modell_mit_erlaubnis_laden(model_to_use)
    if not aktives_modell:
        raise Exception("Ollama-Dienst nicht verfügbar.")

    payload = {
        "model": aktives_modell, 
        "prompt": prompt, 
        "stream": False, 
        "format": "json"
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(OLLAMA_URL, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as response:
        res = json.loads(response.read().decode("utf-8"))
        return json.loads(res.get("response", "{}"))

# =====================================================================
# HYBRIDER VERTEILER MIT SMART-CHOICE (IDEE 3)
# =====================================================================
def _analysiere_textauszug(text_auszug):
    prompt = f"""
    Du bist der autonome Scout für den Künstler DETO. 
    Analysiere den folgenden Textauszug einer Ausschreibung oder eines Jobangebots.
    
    DEINE KRITERIEN:
    1. Sucht das Angebot nach kreativer Gestaltung, Event-Setup, Raumkonzepten, Live-Art oder Airbrush/Fluid-Art?
    2. Befindet sich der Einsatzort im Raum Aachen oder in einem Radius von maximal 20 km um Aachen?
    
    TEXTAUSZUG:
    \"\"\"{text_auszug[:2000]}\"\"\"
    
    ANTWORTE STRIKT NUR IM FOLGENDEN JSON-FORMAT (kein anderer Text, kein Smalltalk):
    {{
        "passt_profil": true oder false,
        "grund": "Kurze Begründung auf Deutsch warum es passt oder nicht",
        "titel": "Titel des Angebots",
        "ort": "Gefundener Einsatzort"
    }}
    """

    # IDEE 3: Smart Choice – Automatische Modell-Auswahl nach Textlänge
    text_laenge = len(text_auszug)
    if text_laenge < 400:
        # Sehr kurzer Text (z.B. kurzes RSS-Snippet) -> Nutze schnelles, ressourcensparendes Modell
        print(f"⚡ Kurztext erkannt ({text_laenge} Zeichen). Nutze Express-Modell '{OLLAMA_FAST}'...")
        try:
            return _analysiere_mit_ollama(prompt, OLLAMA_FAST)
        except Exception:
            print("⚠️ Express-Modell fehlgeschlagen. Wechsle zur Hauptstrategie...")

    # Standard- oder Langtext -> Nutze die definierte Hauptstrategie
    if KI_STRATEGIE == "lm-studio":
        try:
            return _analysiere_mit_lm_studio(prompt)
        except Exception as e:
            print(f"[Scout-Fehler] LM Studio fehlgeschlagen: {e}")
            return {"passt_profil": False}
            
    elif KI_STRATEGIE == "ollama":
        try:
            return _analysiere_mit_ollama(prompt, OLLAMA_DEEP)
        except Exception as e:
            print(f"[Scout-Fehler] Ollama-Hauptmodell fehlgeschlagen: {e}")
            return {"passt_profil": False}
            
    elif KI_STRATEGIE == "fallback":
        try:
            return _analysiere_mit_lm_studio(prompt)
        except Exception:
            print("⚠️ LM Studio offline. Wechsle automatisch auf Ollama-Backup...")
            try:
                return _analysiere_mit_ollama(prompt, OLLAMA_DEEP)
            except Exception as e:
                print(f"[Scout-Fehler] Beide Backends offline! {e}")
                return {"passt_profil": False}

    return {"passt_profil": False}

# =====================================================================
# HAUPTFUNKTION FÜR DIE JAGD
# =====================================================================
def scout_jagd_starten():
    print(f"🕵️ Agent_Scout zieht los (Strategie: {KI_STRATEGIE}, Smart-Choice aktiv)...")
    log_data = _load_scout_log()
    gefundene_treffer = []

    for url in ZIEL_QUELLEN:
        roh_inhalt = _seite_abrufen(url)
        if not roh_inhalt:
            continue
            
        eintraege = re.findall(f"<item>(.*?)</item>", roh_inhalt, re.DOTALL)
        if not eintraege:
            eintraege = [roh_inhalt]

        for block in eintraege:
            link_match = re.search(r"<link>(.*?)</link>", block)
            link = link_match.group(1) if link_match else url
            
            if link in log_data["bekannte_links"] and link != url:
                continue 
                
            rein_text = _html_bereinigen(block)
            if not rein_text:
                continue
                
            analyse = _analysiere_textauszug(rein_text)
            
            if analyse.get("passt_profil") == True:
                # IDEE 2: Perfekte Vorbereitung für den Telegram-Agenten
                analyse["link"] = link
                analyse["zeitstempel"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                analyse["telegram_gesendet"] = False  # Der "Schalter" für Telegram!
                
                gefundene_treffer.append(analyse)
                log_data["treffer"].append(analyse) # In separater Liste sammeln
                
                print(f"🎯 MATCH GEFUNDEN: {analyse.get('titel')} in {analyse.get('ort')}")
                
            if link != url and link not in log_data["bekannte_links"]:
                log_data["bekannte_links"].append(link)

    _save_scout_log(log_data)
    return gefundene_treffer

if __name__ == "__main__":
    scout_jagd_starten()