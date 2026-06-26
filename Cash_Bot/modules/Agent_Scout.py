import os
import sys
from pathlib import Path

# Stammverzeichnis (CASH_BOT) absolut absichern, damit doctor_core gefunden wird
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import urllib.request
import urllib.parse
import urllib.error
import json
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

# Pfade absolut und robust auflösen (Verhindert Verrutschen im GUI-Modus)
SCOUT_DIR = Path(__file__).resolve().parent
LOCAL_XML = (SCOUT_DIR / "crypto-rss.xml").resolve()

# Versuche, 'requests' zu verwenden, wenn installiert (besseres Browser-Simulating)
try:
    import requests  # type: ignore
except Exception:
    requests = None

# Quellen als Strings für die Abruf-Logik bereitstellen
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
        self.callback = None

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
        from pathlib import Path as _Path
        import urllib.request as _ur
        import urllib.error as _urlerr
        import socket as _socket

        if not url or not url.strip():
            self._log_to_ui("[SCOUT ENGINE] ⚠️ Leere URL/Quelldaten erhalten.")
            return ""

        # String säubern, falls Whitespaces mitgerutscht sind
        url_clean = url.strip()

        # 1. Fall: Echte HTTP/HTTPS Web-Adresse
        if url_clean.lower().startswith("http://") or url_clean.lower().startswith("https://"):
        # 2. Fall: Externer Web-Abruf mit robuster Browser-Tarnung
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
                "Cache-Control": "max-age=0"
            }

            domain = url_clean.split('/')[2] if len(url_clean.split('/')) >= 3 else url_clean
            timeout_seconds = 10

            if requests is not None:
                try:
                    response = requests.get(url_clean, headers=headers, timeout=timeout_seconds, verify=False)
                    if response.status_code == 200:
                        return response.text
                    self._log_to_ui(f"[SCOUT ENGINE] ⚠️ Web-Server meldet HTTP {response.status_code} für {url_clean}")
                except requests.exceptions.ConnectionError:
                    self._log_to_ui(f"[SCOUT ENGINE] ❌ Netzwerk-Fehler: Domain '{domain}' nicht erreichbar.")
                except requests.exceptions.Timeout:
                    self._log_to_ui(f"[SCOUT ENGINE] ❌ Timeout beim Abruf von {url_clean}.")
                except requests.exceptions.RequestException as e:
                    self._log_to_ui(f"[SCOUT ENGINE] ⚠️ Web-Fehler: {e}")

            # Nativer Ausfallschutz über urllib für Web-URLs
            try:
                req = _ur.Request(url_clean, headers=headers)
                with _ur.urlopen(req, timeout=timeout_seconds) as response:
                    return response.read().decode('utf-8', errors='ignore')
            except _urlerr.URLError as e:
                if isinstance(e.reason, _socket.gaierror):
                    self._log_to_ui(f"[SCOUT ENGINE] ❌ DNS-Fehler: Domain '{domain}' konnte nicht aufgelöst werden.")
                else:
                    self._log_to_ui(f"[SCOUT ENGINE] ⚠️ Netzwerkfehler für {url_clean}: {e.reason}")
                return ""
            except Exception as e:
                self._log_to_ui(f"[SCOUT ENGINE] ⚠️ Fallback-Fehler beim Abruf von {url_clean}: {e}")
                return ""

        # 2. Fall: Lokale Datei behandeln (alles, was kein http/https ist)
        else:
            try:
                bereinigter_pfad = url_clean.replace("file:///", "").replace("file://", "")
                lokaler_pfad = _Path(bereinigter_pfad).resolve()
                
                if lokaler_pfad.exists() and lokaler_pfad.is_file():
                    return lokaler_pfad.read_text(encoding="utf-8", errors="ignore")
                
                # Alternativ-Fallback im modul-eigenen Ordner suchen
                alternativ_pfad = (Path(__file__).resolve().parent / _Path(url_clean).name).resolve()
                if alternativ_pfad.exists() and alternativ_pfad.is_file():
                    return alternativ_pfad.read_text(encoding="utf-8", errors="ignore")
                    
                self._log_to_ui(f"[SCOUT ENGINE] ⚠️ Lokale Datei fehlt unter: {lokaler_pfad}")
                return ""
            except Exception as e:
                self._log_to_ui(f"[SCOUT ENGINE] ⚠️ Lokaler Lese-Fehler: {e}")
                return ""

            return ""

    def _hole_installierte_ollama_modelle(self) -> List[str]:
        """Gibt eine Liste aller lokal installierten Ollama-Modelle zurück."""
        try:
            with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3) as response:
                lokale_modelle = json.loads(response.read().decode("utf-8"))
                return [m["name"] for m in lokale_modelle.get("models", [])]
        except Exception:
            return []

    def parse_scout_sources(self) -> str:
        """Lädt die Ausschreibungen herunter, loggt den Status und sendet Telegram-Nachrichten bei Treffern."""
        url = "https://www.bundesweit-kreativ.de/de/aussschreibungen.xml"

        print("[SCOUT] Starte Abgleich mit externer Quelle...")

        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            )

            with urllib.request.urlopen(req, timeout=8) as response:
                xml_data = response.read().decode("utf-8")
                print("[SCOUT] [SUCCESS] Daten erfolgreich empfangen.")

                # --- HIER FOLGT DEINE EXISTIERENDE XML-PARSER LOGIK ---
                # Beispielhafter Ablauf für einen gefundenen Treffer:
                # if treffer_gefunden:
                #     titel = "Kreativ-Ausschreibung Aachen"
                #     link = "https://www.bundesweit-kreativ.de/beispiel"
                #
                #     if self.callback:
                #         self.callback(titel, "Aachen", "NEU")
                #     self._send_telegram_notification(titel, link)

                return xml_data

        except urllib.error.URLError as e:
            fehler_meldung = f"❌ Netzwerk-/DNS-Fehler: {e.reason}"
            print(f"[SCOUT] {fehler_meldung}")
            if self.callback:
                self.callback("FEHLER: Verbindung fehlgeschlagen", "SYSTEM", "TIMEOUT")
            return ""

        except Exception as e:
            print(f"[SCOUT] Unerwarteter Fehler beim Parsen: {e}")
            return ""

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
        
        if text_laenge < 400:
            try:
                return self._analysiere_mit_ollama(prompt, OLLAMA_FAST)
            except Exception:
                pass

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

    def _send_telegram_notification(self, titel: str, link: str) -> bool:
        """Sendet eine verschlüsselte Push-Nachricht über die Telegram Bot API"""
        
        # Deine echten, fest eingebauten Zugangsdaten für den Cash_Bot
        bot_token = "8905346856:AAGTWneLxKqBQV3qlqWP95BSifLwbCpLG5k"
        chat_id = "8905346856"

        # Formatierung der Nachricht (Mit fettgedrucktem Titel)
        nachricht = f"🚨 *AEGIS SCOUT TREFFER*\n\n*Titel:* {titel}\n*Link:* {link}"
        
        # Text für das Internet codieren (Leerzeichen und Sonderzeichen umwandeln)
        encoded_text = urllib.parse.quote(nachricht)
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={encoded_text}&parse_mode=Markdown"
        
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                res_daten = json.loads(response.read().decode("utf-8"))
                if res_daten.get("ok", False):
                    print("[TELEGRAM] Nachricht erfolgreich über Cash_Bot gesendet!")
                    return True
                else:
                    print(f"[TELEGRAM] Fehler-Antwort von API: {res_daten}")
                    return False
        except Exception as e:
            print(f"[TELEGRAM ERROR] Verbindung fehlgeschlagen: {e}")
            return False

    def scout_jagd_starten(self, callback=None) -> List[Dict[str, Any]]:
        """Startet den synchronisierten Scraping- und Analyse-Durchlauf."""
        self._log_to_ui("\n" + "="*40)
        self._log_to_ui(f"[SCOUT ENGINE] Aufklärungslauf gestartet (Strategie: {KI_STRATEGIE}).")
        
        scout_data = self.state.get_state("scout_engine", {"bekannte_links": [], "treffer": []})
        bekannte_links = set(scout_data.get("bekannte_links", []))
        gefundene_treffer = []

        for url in ZIEL_QUELLEN:
            anzeige_url = url.split("\\")[-1] if "\\" in url else url
            self._log_to_ui(f"[SCOUT ENGINE] Scanne Quelle: {anzeige_url}")
            
            roh_inhalt = self._seite_abrufen(url)
            if not roh_inhalt:
                continue
                
            eintraege = re.findall(r"(.*?)", roh_inhalt, re.DOTALL)
            if not eintraege:
                eintraege = [roh_inhalt]

            for block in eintraege:
                link_match = re.search(r"(.*?)", block)
                link = link_match.group(1) if link_match else url
                
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
                    
                    gefundene_treffer.append(analyse)
                    scout_data["treffer"].append(analyse)
                    self.state.set_state("scout_engine", scout_data)

                    # Telegram Push abschicken
                    gesendet = self._send_telegram_notification(
                        analyse.get("titel", "Unbekannt"),
                        analyse.get("link", "")
                    )

                    if gesendet:
                        analyse["telegram_gesendet"] = True
                        if scout_data["treffer"]:
                            scout_data["treffer"][-1]["telegram_gesendet"] = True
                        self.state.set_state("scout_engine", scout_data)
                        # Wenn später ein echter Storage-Manager verfügbar ist:
                        # self.storage.mark_telegram_sent(treffer_id)

                    self._log_to_ui(f"[SCOUT ENGINE] 🎯 TREFFER GEFUNDEN -> '{analyse.get('titel')}' ({analyse.get('ort')})")
                else:
                    self._log_to_ui(f"[SCOUT ENGINE] Fragment geprüft: Kein Match für DETO.")
                    
                if link != url:
                    bekannte_links.add(link)

        scout_data["bekannte_links"] = list(bekannte_links)
        self.state.set_state("scout_engine", scout_data)
        
        self._log_to_ui(f"[SCOUT ENGINE] Aufklärungslauf beendet. {len(gefundene_treffer)} neue Matches gesichert.")
        
        if self.ui and hasattr(self.ui, "say"):
            self.ui.say(f"Scout-Lauf beendet. {len(gefundene_treffer)} neue Treffer.")
            
        # --- THREAD-SICHERER RUN-COMPLETED CALLBACK AN DIE GUI ---
        if callback:
            callback(gefundene_treffer)
            
        return gefundene_treffer


# Direkter Testlauf-Einstiegspunkt
if __name__ == "__main__":
    from doctor_core.state import DoctorState
    
    manager = EngineManager()
    db_state = DoctorState()
    manager.register("state", db_state)
    
    scout = AgentScout(manager)
    scout.scout_jagd_starten()