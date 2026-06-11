import urllib.request
import urllib.parse
import re

def run_modul(): 
    return "Suchmodul bereit (Windows-ARM64 optimiert)."

def suche(begriff):
    try:
        # Wir nutzen die offizielle, schlanke HTML-Version von DuckDuckGo
        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote_plus(begriff)
        
        # Wir geben uns als normaler Webbrowser aus, um nicht blockiert zu werden
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        )
        
        # Seite abrufen
        with urllib.request.urlopen(req, timeout=8) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        # Filtert die Titel und Textausschnitte direkt aus dem HTML-Code
        titles = re.findall(r'class="result__url"[^>]*>(.*?)<\/a>', html, re.DOTALL)
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)<\/a>', html, re.DOTALL)
        
        if not snippets:
            return "Fehler: Die Suchmaschine hat die Anfrage blockiert oder keine Ergebnisse geliefert."
        
        # Die besten 3 Ergebnisse sauber formatieren
        ergebnisse = []
        for i in range(min(3, len(snippets))):
            title_text = re.sub(r'<[^>]+>', '', titles[i]).strip() if i < len(titles) else "Webseite"
            snippet_text = re.sub(r'<[^>]+>', '', snippets[i]).strip()
            ergebnisse.append(f"Quelle: {title_text} | Inhalt: {snippet_text}")
            
        return " ".join(ergebnisse)
        
    except Exception as e:
        return f"Fehler bei der ARM64-Direktsuche: {e}"