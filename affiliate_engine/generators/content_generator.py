"""
SEO Content Generator
Generiert E-E-A-T optimierte Inhalte mit Keywords und LSI-Begriffen
"""
import re
import time
from datetime import datetime
from typing import Dict, List, Optional
from openai import OpenAI
from affiliate_engine.config import CONTENT_CONFIG
from affiliate_engine.db.database import AffiliateDatabase

class ContentGenerator:
    """Generiert SEO-optimierte Inhalte"""
    
    def __init__(self):
        self.db = AffiliateDatabase()
        self.config = CONTENT_CONFIG
        self.client = self._init_client()

    def _init_client(self):
        """Initialisiere OpenAI/LM Studio Client"""
        if self.config["use_openai"] and self.config["openai_api_key"]:
            return OpenAI(api_key=self.config["openai_api_key"])
        else:
            # LM Studio (lokal)
            return OpenAI(
                base_url=self.config["lm_studio_url"],
                api_key="not-needed",
                timeout=self.config["lm_studio_timeout"]
            )

    def generate_article(self, topic: str, main_keyword: str, 
                        keywords: List[str], programs: List[Dict]) -> Dict:
        """
        Generiere SEO-optimierten Artikel
        
        Args:
            topic: Artikel-Thema
            main_keyword: Haupt-Keyword
            keywords: LSI Keywords
            programs: Affiliate-Programme
        
        Returns:
            Dict mit HTML-Content und Metadaten
        """
        
        start_time = time.time()
        
        # 1. Baue Prompt
        prompt = self._build_prompt(topic, main_keyword, keywords, programs)
        
        try:
            # 2. Generiere Content
            print(f"[*] Generiere Content für: {topic}...")
            content = self._generate_with_llm(prompt)
            
            if not content:
                raise Exception("Leerer Content von LLM erhalten")
            
            # 3. Post-Processing
            content = self._clean_content(content)
            
            # 4. Metadaten
            meta_description = self._generate_meta_description(topic, content)
            h1_title = self._extract_h1(content)
            
            generation_time = time.time() - start_time
            
            result = {
                "status": "success",
                "topic": topic,
                "main_keyword": main_keyword,
                "keywords": keywords,
                "content": content,
                "meta_description": meta_description,
                "h1_title": h1_title,
                "word_count": len(content.split()),
                "generation_time": round(generation_time, 2),
                "timestamp": datetime.now().isoformat(),
            }
            
            print(f"[✓] Content generiert ({generation_time:.1f}s, {result['word_count']} Wörter)")
            return result
            
        except Exception as e:
            print(f"[-] Fehler bei Content-Generierung: {e}")
            return {
                "status": "error",
                "error": str(e),
                "topic": topic,
                "timestamp": datetime.now().isoformat(),
            }

    def _build_prompt(self, topic: str, main_keyword: str, 
                     keywords: List[str], programs: List[Dict]) -> str:
        """Baue LLM-Prompt"""
        
        keywords_str = ", ".join(keywords[:5])
        programs_str = ", ".join([p.get("name", "") for p in programs[:3]])
        
        prompt = f"""
Du bist ein renommierter SEO-Experte und Autor für hochwertige Fachkontent.
Schreibe einen tiefgehenden, professionellen HTML-Artikel mit E-E-A-T Standards.

THEMA: {topic}
HAUPT-KEYWORD: {main_keyword}
SEKUNDÄRE KEYWORDS: {keywords_str}
VERWANDTE PROGRAMME: {programs_str}

ANFORDERUNGEN:
1. STRUKTUR:
   - H1-Überschrift mit Haupt-Keyword
   - Einleitung (2-3 Absätze)
   - Mindestens 5 H2-Abschnitte
   - Umfassende Inhalte (min. 1500 Wörter)
   - 1-2 HTML-Tabellen mit Vor/Nachteilen
   - FAQ-Sektion mit 5+ Fragen

2. SEO OPTIMIERUNG:
   - Keywords natürlich in H1, H2, ersten Absätzen integrieren
   - Verwende LSI-Keywords und Variationen
   - Meta-Description vorbereiten (160 Zeichen)
   - Interne Verlinkungsstrukturen

3. E-E-A-T REGELN:
   - Experience: Schreibe aus praktischer Perspektive
   - Expertise: Verwende korrekte Fachbegriffe
   - Authoritativeness: Zitiere vertrauenswürdige Quellen
   - Trustworthiness: Sei transparent und ehrlich

4. FORMAT:
   - Antworte NUR mit HTML-Tags (kein Markdown!)
   - Beginne mit <h1>, dann <p>, <h2>, etc.
   - Verwende semantische HTML5-Tags
   - Kein ```html Code-Block-Wrapper

5. STYLE:
   - Deutsche Sprache
   - Fachlich, aber verständlich
   - Conversational Tone
   - Praktische Beispiele

STARTEN mit:
<h1>{main_keyword}</h1>
"""
        return prompt

    def _generate_with_llm(self, prompt: str) -> str:
        """Generiere Content mit LLM"""
        try:
            completion = self.client.chat.completions.create(
                model=self.config["lm_studio_model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                top_p=0.9,
            )
            
            raw_content = completion.choices[0].message.content
            
            # Entferne Markdown Code-Wrapper
            clean_content = re.sub(r"```html|```", "", raw_content).strip()
            
            return clean_content
            
        except Exception as e:
            print(f"[-] LLM Error: {e}")
            return None

    def _clean_content(self, content: str) -> str:
        """Räume Content auf"""
        # Entferne extra Whitespace
        content = re.sub(r'\n\n+', '\n\n', content)
        
        # Prüfe auf gültige HTML-Tags
        if not content.strip().startswith('<'):
            content = f"<h1>Artikel</h1>\n{content}"
        
        return content.strip()

    def _generate_meta_description(self, topic: str, content: str) -> str:
        """Generiere Meta-Description"""
        # Extrahiere ersten Absatz
        p_match = re.search(r'<p>(.+?)</p>', content, re.DOTALL)
        if p_match:
            text = p_match.group(1)
            # Entferne HTML-Tags
            text = re.sub(r'<[^>]+>', '', text)
            # Begrenzte auf 160 Zeichen
            return text[:160].rstrip() + ("..." if len(text) > 160 else "")
        
        return f"Umfassender Guide: {topic}"

    def _extract_h1(self, content: str) -> str:
        """Extrahiere H1-Tag"""
        h1_match = re.search(r'<h1>(.+?)</h1>', content)
        return h1_match.group(1) if h1_match else "Artikel"

    def generate_landing_page(self, topic: str, article_content: str, 
                              programs: List[Dict]) -> str:
        """
        Baue vollständige Landing Page aus Content + Affiliates
        """
        
        programs_section = self._build_programs_section(programs)
        
        html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic} | Affiliate Hub</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.8; color: #333; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 40px 20px; }}
        .article {{ background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 40px; }}
        .article h1 {{ color: #1a1a1a; margin-bottom: 20px; font-size: 2.5rem; }}
        .article h2 {{ color: #0066cc; margin-top: 30px; margin-bottom: 15px; font-size: 1.8rem; }}
        .article p {{ margin-bottom: 15px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f0f0f0; font-weight: bold; }}
        .programs-section {{ background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .programs-section h2 {{ color: #0066cc; margin-bottom: 20px; }}
        .program-card {{ background: #f9f9f9; padding: 20px; margin-bottom: 15px; border-radius: 5px; border-left: 4px solid #0066cc; }}
        .program-card h3 {{ color: #0066cc; margin-bottom: 10px; }}
        .cta-button {{ display: inline-block; background: #0066cc; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 10px 0; font-weight: bold; }}
        .cta-button:hover {{ background: #0052a3; }}
    </style>
</head>
<body>
<div class="container">
    <div class="article">
        {article_content}
    </div>
    
    <div class="programs-section">
        <h2>🎯 Empfohlenene Partnerprogramme</h2>
        {programs_section}
    </div>
</div>
</body>
</html>"""
        
        return html

    def _build_programs_section(self, programs: List[Dict]) -> str:
        """Baue Affiliate-Programm-Sektion"""
        html = ""
        for program in programs[:5]:
            html += f"""
    <div class="program-card">
        <h3>{program.get("name", "Programm")}</h3>
        <p><strong>Provision:</strong> {program.get("commission_potential", "Variabel")}</p>
        <p><strong>Popularität:</strong> {program.get("popularity", "Mittel")}</p>
        <a href="#" class="cta-button">Mehr erfahren</a>
    </div>
"""
        return html

if __name__ == "__main__":
    gen = ContentGenerator()
    
    # Test
    article = gen.generate_article(
        topic="Business Automation mit Zapier",
        main_keyword="Zapier Automation",
        keywords=["Make.com", "Workflow", "Integration", "Automation"],
        programs=[
            {"name": "Amazon", "commission_potential": "1-10%"},
            {"name": "Digistore24", "commission_potential": "20-50%"},
        ]
    )
    
    print(f"\n[✓] Artikel generiert:")
    print(f"   Status: {article.get('status')}")
    print(f"   Wörter: {article.get('word_count')}")
    print(f"   Zeit: {article.get('generation_time')}s")
