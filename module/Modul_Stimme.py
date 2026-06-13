import sounddevice as sd
from scipy.io import wavfile
import requests
import os
import ollama
import pyttsx3

TEMP_FILE = "temp_voice.wav"

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def run_modul():
    # Keine SpeechRecognition Bibliothek hier!
    samplerate = 16000
    duration = 4
    
    try:
        print("🎙️ [STIMME] Aufnahme startet...")
        # device=1 ist dein Standard-Mikrofon
        audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16', device=1)
        sd.wait()
        
        wavfile.write(TEMP_FILE, samplerate, audio_data)
        
        with open(TEMP_FILE, 'rb') as f:
            audio_bytes = f.read()
        
        # Google API (erfordert nur requests)
        url = "https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&lang=de-DE"
        headers = {'Content-Type': 'audio/l16; rate=16000'}
        
        response = requests.post(url, data=audio_bytes, headers=headers)
        
        # Text extrahieren
        user_text = ""
        for line in response.text.split('\n'):
            if "utterance" in line:
                user_text = line.split('"utterance":"')[1].split('"')[0]
                break
        
        if not user_text:
            return "❌ API hat nichts verstanden. Das Mikrofon blieb stumm."
            
        print(f"🗣️ Erkannt: {user_text}")
        res = ollama.generate(model="deto_agent", prompt=user_text)
        antwort = res['response'].strip()
        
        speak(antwort)
        return f"✅ Erfolg: {user_text}"
        
    except Exception as e:
        return f"❌ Fehler: {str(e)}"