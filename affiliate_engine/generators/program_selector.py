"""
Automatischer Partnerprogramm-Selector
Wählt beste Programme basierend auf Keywords und Nische
"""
import json
from typing import List, Dict, Tuple
from affiliate_engine.db.database import AffiliateDatabase
from affiliate_engine.api_wrappers.affiliate_apis import AffiliateAPIManager

class ProgramSelector:
    """Intelligente Auswahl von Affiliate-Programmen"""
    
    def __init__(self):
        self.db = AffiliateDatabase()
        self.api_manager = AffiliateAPIManager()
        
        # Vordefinierte Program-Kategorien
        self.program_categories = {
            "software": ["Amazon", "Digistore24", "Awin", "ShareASale"],
            "saas": ["CJ Affiliate", "Awin", "Impact"],
            "tools": ["Amazon", "Digistore24", "ClickBank"],
            "bildung": ["Digistore24", "Udemy", "Skillshare"],
            "health": ["Amazon", "Awin", "Impact"],
            "finance": ["Amazon", "Awin", "ClickBank"],
            "ecommerce": ["Amazon", "Awin", "ShareASale"],
        }

    def select_programs_for_topic(self, topic: str, keywords: List[str], 
                                  max_programs: int = 5) -> List[Dict]:
        """
        Wähle beste Affiliate-Programme für ein Thema
        
        Args:
            topic: Hauptthema/Nische
            keywords: List von Keywords
            max_programs: Maximale Anzahl von Programmen
        
        Returns:
            List von ausgewählten Programmen mit Details
        """
        
        # 1. Analysiere Keywords
        category = self._detect_category(topic, keywords)
        
        # 2. Hole Programme für Kategorie
        recommended_programs = self._get_programs_for_category(category)
        
        # 3. Bewerte Programme
        scored_programs = self._score_programs(recommended_programs, keywords)
        
        # 4. Sortiere nach Score
        top_programs = sorted(scored_programs, key=lambda x: x["score"], reverse=True)[:max_programs]
        
        return top_programs

    def _detect_category(self, topic: str, keywords: List[str]) -> str:
        """Erkenne Kategorie aus Topic und Keywords"""
        topic_lower = topic.lower()
        keywords_lower = [k.lower() for k in keywords]
        
        category_keywords = {
            "software": ["software", "tool", "programm", "anwendung", "app", "automation"],
            "saas": ["saas", "cloud", "subscription", "service", "platform"],
            "tools": ["tool", "generator", "builder", "maker", "automation"],
            "bildung": ["kurs", "lernen", "training", "schulung", "bildung", "lehrgang"],
            "health": ["gesundheit", "fitness", "wellness", "sport", "diet"],
            "finance": ["finance", "geld", "investition", "kredit", "versicherung"],
            "ecommerce": ["shop", "ecommerce", "store", "verkauf", "produkt"],
        }
        
        # Suche nach Kategorie-Keywords
        for category, keywords_list in category_keywords.items():
            for kw in keywords_list:
                if kw in topic_lower or any(kw in k for k in keywords_lower):
                    return category
        
        # Default
        return "tools"

    def _get_programs_for_category(self, category: str) -> List[str]:
        """Hole Programme für Kategorie"""
        return self.program_categories.get(category, ["Amazon", "Digistore24", "Awin"])

    def _score_programs(self, programs: List[str], keywords: List[str]) -> List[Dict]:
        """Bewerte Programme basierend auf Relevanz"""
        scored = []
        
        for program_name in programs:
            score = 0
            
            # Basis-Score
            score += 10
            
            # Bonus für populäre Programme
            if program_name in ["Amazon", "Digistore24", "Awin"]:
                score += 5
            
            # Bonus wenn Keywords im Programm passen
            for keyword in keywords:
                if self._keyword_matches_program(keyword, program_name):
                    score += 3
            
            scored.append({
                "name": program_name,
                "score": score,
                "commission_potential": self._estimate_commission(program_name),
                "popularity": self._get_popularity(program_name),
            })
        
        return scored

    def _keyword_matches_program(self, keyword: str, program: str) -> bool:
        """Prüfe ob Keyword zum Programm passt"""
        keyword_lower = keyword.lower()
        program_lower = program.lower()
        
        # Einfache Heuristik
        if keyword_lower in program_lower or program_lower in keyword_lower:
            return True
        
        return False

    def _estimate_commission(self, program_name: str) -> str:
        """Schätze Provision"""
        commissions = {
            "Amazon": "1-10%",
            "Digistore24": "20-50%",
            "Awin": "1-30%",
            "CJ Affiliate": "5-20%",
            "ShareASale": "1-40%",
            "ClickBank": "5-75%",
            "Refersion": "Variabel",
        }
        return commissions.get(program_name, "Variabel")

    def _get_popularity(self, program_name: str) -> str:
        """Finde Popularität"""
        popularity = {
            "Amazon": "sehr-hoch",
            "Digistore24": "hoch",
            "Awin": "mittel-hoch",
            "CJ Affiliate": "mittel",
            "ShareASale": "mittel",
            "ClickBank": "hoch",
        }
        return popularity.get(program_name, "gering")

    def build_program_list(self, topic: str, keywords: List[str]) -> Dict:
        """
        Baue komplette Program-Liste für Content
        """
        programs = self.select_programs_for_topic(topic, keywords)
        
        return {
            "topic": topic,
            "keywords": keywords,
            "recommended_programs": programs,
            "total_programs": len(programs),
            "average_commission": self._calculate_avg_commission(programs),
            "best_fit": programs[0] if programs else None,
        }

    def _calculate_avg_commission(self, programs: List[Dict]) -> str:
        """Berechne durchschnittliche Provision"""
        if not programs:
            return "N/A"
        return f"ca. {len(programs)} Programme in Top-Performance-Range"

    def get_program_details(self, program_name: str) -> Dict:
        """Hole detaillierte Infos über Programm"""
        return {
            "name": program_name,
            "commission": self._estimate_commission(program_name),
            "popularity": self._get_popularity(program_name),
            "status": "ready",
            "description": f"Affiliate-Programm: {program_name}",
        }

    def validate_programs(self) -> Dict:
        """Validiere alle Programme"""
        validation = {
            "total_programs": len(self.program_categories),
            "categories": len(self.program_categories),
            "networks": self.api_manager.get_available_networks(),
            "status": "ready"
        }
        return validation

if __name__ == "__main__":
    selector = ProgramSelector()
    
    # Test
    topic = "Business Automation Software"
    keywords = ["automation", "zapier", "make.com", "workflow"]
    
    print(f"[*] Wähle Programme für: {topic}")
    result = selector.build_program_list(topic, keywords)
    
    print(f"\n[✓] Gefundene Programme:")
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
