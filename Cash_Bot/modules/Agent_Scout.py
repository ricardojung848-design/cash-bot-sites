import os
import sys
from pathlib import Path

# Stammverzeichnis (CASH_BOT) absolut absichern, damit doctor_core gefunden wird
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import json
import urllib.request
import urllib.parse
import re
from datetime import datetime
from typing import Any, List, Dict

from doctor_core.logging import log_doctor
from doctor_core.engine_manager import EngineManager

# =====================================================================
# KI-KONFIGURATION (HYBRID, DYNAMISCH & INTERAKTIV)
# =====================================================================
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
LM_STUDIO_MODEL = "mistralai/mistral-7b-instruct-v0.3"

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_DEFAULT = "llama3"
OLLAMA_FAST = "gemma2:2b"
OLLAMA_DEEP = "llama3"

KI_STRATEGIE = "fallback"

# Pfade relativ zum Scout-Modul (robust gegen Arbeitsverzeichnis-Verschiebungen)
SCOUT_DIR = Path(__file__).resolve().parent
LOCAL_XML = SCOUT_DIR / "crypto-rss.xml"
RSS_PFAD = LOCAL_XML

# Versuche, 'requests' zu verwenden, wenn installiert (besseres Browser-Simulating)
try:
    import requests  # type: ignore
except Exception:
    requests = None

ZIEL_QUELLEN = [
    str(LOCAL_XML),
    "https://www.bundesweit-kreativ.de/feeder/rss/rss.xml",
]


class AgentScout:
    """
    PRO-Version des Agent_Scout:
    - Überwacht RSS-Feeds nach Ausschreibungen für DETO (Aachen + 20km)
    - Nutze eine hybride LLM-Infrastruktur (LM Studio / Ollama) mit Smart-Choice-Logik
    - Speichert Funde transaktionssicher direkt in der SQLite-Zustandsdatenbank
    """

    def __init__(self, engine_manager: EngineManager, ui_instance=None):
        self.engines = engine_manager
        if not self.engines.has("state"):
            raise RuntimeError("AgentScout benötigt einen registrierten State-Manager im EngineManager!")
        self.state = self.engines.get("state")
        self.ui = ui_instance  # Optionale GUI-Referenz für Live-Logs

    def _log_to_ui(self, message: str):
        """Hilfsmethode, um Logs sowohl in die DB als auch live ins UI zu schreiben."""
        log_doctor(message)
        if self.ui and hasattr(self.ui, "_log_ui"):
            self.ui._log_ui(message)

    def _html_bereinigen(self, html_text: str) -> str:
        """Entfernt HTML-Tags und bereinigt Whitespaces."""
        clean = re.compile('<.*?>|&([a-z0-9]+|#[0-9]+|#x[0-9a-f]+);')
        text = re.sub(clean, ' ', html_text)
        return " ".join(text.split())

    def _seite_abrufen(self, url: str) -> str:
        """Lädt den Inhalt einer lokalen Datei oder einer Webseite absolut stabil."""
        # 1. Fall: Es handelt sich um einen lokalen Systempfad
        try:
            if url and (url.startswith("C:") or url.startswith("/") or "\\" in url or (not url.startswith("http"))):
                try:
                    from pathlib import Path as _Path
                    lokaler_pfad = _Path(url).resolve()
                    if lokaler_pfad.exists():
                        return lokaler_pfad.read_text(encoding="utf-8", errors="ignore")
                    else:
                        self._log_to_ui(f"[SCOUT ENGINE] ⚠️ Lokale Quelle existiert nicht: {lokaler_pfad}")
                        return ""
                except Exception as e:
                    self._log_to_ui(f"[SCOUT ENGINE] ⚠️ Fehler beim Lesen der lokalen Datei: {e}")
                    return ""

            # 2. Fall: Es ist eine externe Web-URL
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }

            # Falls 'requests' installiert ist (bevorzugte, stabilere Methode)
            if requests is not None:
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        return response.text
                    else:
                        self._log_to_ui(f"[SCOUT ENGINE] ⚠️ HTTP-Fehler {response.status_code} für {url}")
                        return ""
                except Exception as e:
                    self._log_to_ui(f"[SCOUT ENGINE] ⚠️ Netzwerk-Timeout/Fehler bei Web-Quelle: {e}")
                    return ""

            # Fallback auf urllib, falls requests fehlt
            else:
                try:
                    import urllib.request as _ur
                    req = _ur.Request(url, headers=headers)
                    with _ur.urlopen(req, timeout=10) as response:
                        return response.read().decode('utf-8', errors='ignore')
                except Exception as e:
                    self._log_to_ui(f"[SCOUT ENGINE] ⚠️ Urllib-Fallback fehlgeschlagen für {url}: {e}")
                    return ""
        except Exception as e:
            self._log_to_ui(f"[SCOUT ENGINE] ⚠️ Unbekannter Fehler beim Abruf von {url}: {e}")
            return ""

    def _hole_installierte_ollama_modelle(self) -> List[str]:
        """Gibt eine Liste aller lokal installierten Ollama-Modelle zurück."""
        try:
            with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3) as response:
                lokale_modelle = json.loads(response.read().decode("utf-8"))
                return [m["name"] for m in lokale_modelle.get("models", [])]
        except Exception:
            return []

    def _ollama_modell_bereitstellen(self, model_name: str) -> str:
        """Prüft das Modell. Wenn es fehlt, greift der automatische Fallback."""
        installierte = self._hole_installierte_ollama_modelle()
        if not installierte:
            return ""

        if model_name in installierte or f"{model_name}:latest" in installierte:
            return model_name

        log_doctor(f"AgentScout: Modell '{model_name}' fehlt lokal. Verwende Fallback '{OLLAMA_DEFAULT}'.")
        return OLLAMA_DEFAULT

    def _analysiere_mit_lm_studio(self, prompt: str) -> Dict[str, Any]:
        """Sendet den Analyse-Prompt an die LM-Studio-API."""
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

    def _analysiere_mit_ollama(self, prompt: str, model_to_use: str) -> Dict[str, Any]:
        """Sendet den Analyse-Prompt an die lokale Ollama-Instanz."""
        aktives_modell = self._ollama_modell_bereitstellen(model_to_use)
        if not aktives_modell:
            raise RuntimeError("Ollama-Dienst antwortet nicht.")

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

    def _analysiere_textauszug(self, text_auszug: str) -> Dict[str, Any]:
        """Smarter KI-Verteiler: Entscheidet nach Textlänge und Strategie."""
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

        text_laenge = len(text_auszug)
        
        # Smart Choice für extrem kurze Textschnipsel
        if text_laenge < 400:
            try:
                return self._analysiere_mit_ollama(prompt, OLLAMA_FAST)
            except Exception:
                pass

        # Reguläre Strategie-Abarbeitung
        if KI_STRATEGIE == "lm-studio":
            try: return self._analysiere_mit_lm_studio(prompt)
            except Exception: return {"passt_profil": False}
                
        elif KI_STRATEGIE == "ollama":
            try: return self._analysiere_mit_ollama(prompt, OLLAMA_DEEP)
            except Exception: return {"passt_profil": False}
                
        elif KI_STRATEGIE == "fallback":
            try:
                return self._analysiere_mit_lm_studio(prompt)
            except Exception:
                log_doctor("AgentScout: LM Studio offline. Wechsle zu Ollama-Backup...")
                try:
                    return self._analysiere_mit_ollama(prompt, OLLAMA_DEEP)
                except Exception as e:
                    log_doctor(f"AgentScout: Beide KI-Backends ausgefallen! {e}")
                    return {"passt_profil": False}

        return {"passt_profil": False}

    def scout_jagd_starten(self) -> List[Dict[str, Any]]:
        """Startet den synchronisierten Scraping- und Analyse-Durchlauf."""
        self._log_to_ui("\n" + "="*40)
        self._log_to_ui(f"[SCOUT ENGINE] Aufklärungslauf gestartet (Strategie: {KI_STRATEGIE}).")
        
        # Zustände aus der SQLite-Datenbank laden
        scout_data = self.state.get_state("scout_engine", {"bekannte_links": [], "treffer": []})
        bekannte_links = set(scout_data.get("bekannte_links", []))
        gefundene_treffer = []

        for url in ZIEL_QUELLEN:
            self._log_to_ui(f"[SCOUT ENGINE] Scanne Quelle: {url}")
            roh_inhalt = self._seite_abrufen(url)
            if not roh_inhalt:
                self._log_to_ui(f"[SCOUT ENGINE] ⚠️ Konnte Daten von Quelle nicht abrufen.")
                continue
                
            eintraege = re.findall(r"<item>(.*?)</item>", roh_inhalt, re.DOTALL)
            if not eintraege:
                eintraege = [roh_inhalt]

            for block in eintraege:
                link_match = re.search(r"<link>(.*?)</link>", block)
                link = link_match.group(1) if link_match else url
                
                # Duplikate filtern
                if link in bekannte_links and link != url:
                    continue 
                    
                rein_text = self._html_bereinigen(block)
                if not rein_text:
                    continue
                    
                self._log_to_ui(f"[SCOUT ENGINE] Sende Textfragment an KI zur Analyse...")
                analyse = self._analysiere_textauszug(rein_text)
                
                if analyse.get("passt_profil") is True:
                    analyse["link"] = link
                    analyse["zeitstempel"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    analyse["telegram_gesendet"] = False  # Bereitstellung für den Telegram-Bot
                    
                    gefundene_treffer.append(analyse)
                    scout_data["treffer"].append(analyse)
                    self._log_to_ui(f"[SCOUT ENGINE] 🎯 TREFFER GEFUNDEN -> '{analyse.get('titel')}' ({analyse.get('ort')})")
                else:
                    self._log_to_ui(f"[SCOUT ENGINE] Fragment geprüft: Kein Match für DETO.")
                    
                if link != url:
                    bekannte_links.add(link)

        # Datensatz zurück in die DB schreiben
        scout_data["bekannte_links"] = list(bekannte_links)
        self.state.set_state("scout_engine", scout_data)
        
        self._log_to_ui(f"[SCOUT ENGINE] Aufklärungslauf beendet. {len(gefundene_treffer)} neue Matches gesichert.")
        if self.ui and hasattr(self.ui, "say"):
            self.ui.say(f"Scout-Lauf beendet. {len(gefundene_treffer)} neue Treffer.")
        return gefundene_treffer


# Direkter Testlauf-Einstiegspunkt
if __name__ == "__main__":
    from doctor_core.state import DoctorState
    
    manager = EngineManager()
    db_state = DoctorState()
    manager.register("state", db_state)
    
    scout = AgentScout(manager)
    scout.scout_jagd_starten()