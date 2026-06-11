from duckduckgo_search import DDGS
import ollama

def run_modul(): 
    return "Suchmodul mit Zusammenfassung bereit."

def suche(begriff):
    with DDGS() as ddgs:
        # Ergebnisse abrufen
        ergebnisse = list(ddgs.text(begriff, max_results=2))
        if not ergebnisse: return "Nichts gefunden."
        
        # Texte der ersten zwei Treffer sammeln
        kontext = ""
        for r in ergebnisse:
            kontext += f"Quelle: {r['title']}\nInhalt: {r['body']}\n\n"
        
        # Ollama bitten, das zusammenzufassen
        prompt = f"Hier sind Suchergebnisse zu '{begriff}':\n\n{kontext}\n\nFasse das kurz und präzise auf Deutsch zusammen."
        try:
            res = ollama.generate(model="deto_agent", prompt=prompt)
            return res['response']
        except:
            return "Suche erfolgreich, aber Zusammenfassung durch KI fehlgeschlagen."