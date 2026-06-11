import pyttsx3
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def text_zu_sprache_anlegen(text):
    """Wandelt Text offline in eine zeitgestempelte MP3-Audiodatei um."""
    # Generiert einen dynamischen Dateinamen, um Windows-Dateisperren (PermissionError) zu verhindern
    timestamp = int(time.time())
    dynamischer_ausgabepfad = os.path.join(BASE_DIR, f"agent_antwort_{timestamp}.mp3")
    
    print(f"🎙️ Sprache wird generiert: '{text[:50]}...'")
    
    try:
        # Initialisiert die native Windows-Sprach-Engine
        engine = pyttsx3.init()
        
        # Stimmen auslesen und auf Deutsch filtern
        voices = engine.getProperty('voices')
        de_voice = None
        for voice in voices:
            if "DE" in voice.id.upper() or "GERMAN" in voice.id.upper():
                de_voice = voice.id
                break
        
        if de_voice:
            engine.setProperty('voice', de_voice)
            
        # Sprechgeschwindigkeit (165 ist perfekt für eine natürliche, ruhige Stimme)
        engine.setProperty('rate', 165)
        
        # Datei absichern: Falls exakt diese Sekunde schon eine Datei existiert, löschen
        if os.path.exists(dynamischer_ausgabepfad):
            try:
                os.remove(dynamischer_ausgabepfad)
            except Exception:
                pass 
                
        # Text in die dynamische Datei schreiben und Engine ausführen
        engine.save_to_file(text, dynamischer_ausgabepfad)
        engine.runAndWait()
        
        # Kurze Gedenksekunde, damit Windows den Schreibvorgang physisch abschließt
        time.sleep(0.3)
        
        return dynamischer_ausgabepfad
    except Exception as e:
        print(f"❌ Fehler bei der Sprachgenerierung: {str(e)}")
        return None

def audio_loeschen(datei_pfad):
    """Löscht die temporäre MP3-Datei nach dem Senden, um die Festplatte sauber zu halten."""
    try:
        if datei_pfad and os.path.exists(datei_pfad):
            os.remove(datei_pfad)
            print(f"🧹 Temporäre Datei gelöscht: {os.path.basename(datei_pfad)}")
    except Exception as e:
        print(f"⚠️ Datei konnte nicht gelöscht werden (wird evtl. noch blockiert): {e}")

if __name__ == "__main__":
    # Schneller lokaler Testlauf
    test_text = "Hallo Ricardo. Die Sprachausgabe der Kunstagentur ist jetzt vollständig einsatzbereit."
    datei = text_zu_sprache_anlegen(test_text)
    if datei:
        print(f"✅ Test erfolgreich! Audiodatei liegt hier: {datei}")
        # Test-Cleanup
        time.sleep(1)
        audio_loeschen(datei)