"""
Trend Analyzer
Analysiert Trends, bewertet Profitabilität und findet profitable Nischen
"""
import json
from datetime import datetime
from typing import List, Dict
from trend_radar.db.database import TrendDatabase
from trend_radar.config import TREND_ANALYSIS, NICHE_DISCOVERY, COMPETITOR_TRACKING

class TrendAnalyzer:
    """Analysiert und bewertet Trends"""
    
    def __init__(self):
        self.db = TrendDatabase()
        self.config = TREND_ANALYSIS
        self.niche_config = NICHE_DISCOVERY

    def analyze_trends(self) -> Dict:
        """Analysiere alle gesammelten Trends"""
        print("[*] Analysiere Trends...")
        
        analysis = {
            "trending_keywords": self._analyze_keywords(),
            "hot_niches": self._discover_niches(),
            "viral_content": self._analyze_viral_content(),
            "opportunities": self._find_opportunities(),
            "timestamp": datetime.now().isoformat(),
        }
        
        return analysis

    # =========================================================================
    # KEYWORD ANALYSE
    # =========================================================================

    def _analyze_keywords(self) -> List[Dict]:
        """Analysiere Keywords nach Profitabilität"""
        print("[*] Analysiere Keywords...")
        
        keywords = self.db.get_trending_keywords(limit=100)
        
        analyzed = []
        for kw in keywords:
            score = self._calculate_keyword_score(kw)
            
            if score["overall"] > 60:  # Nur gute Keywords
                analyzed.append({
                    "keyword": kw["keyword"],
                    "region": kw["region"],
                    "search_volume": kw["search_volume"],
                    "growth_rate": kw["growth_rate"],
                    "cpc": kw["cpc"],
                    "competition": kw["competition_level"],
                    "profitability_score": score["overall"],
                    "recommendation": score["recommendation"],
                })
        
        # Sortiere nach Score
        analyzed.sort(key=lambda x: x["profitability_score"], reverse=True)
        return analyzed[:50]

    def _calculate_keyword_score(self, kw: Dict) -> Dict:
        """Berechne Profitabilität eines Keywords"""
        
        score = 0
        details = {}
        
        # Growth Rate (0-30 Punkte)
        growth = min(kw.get("growth_rate", 0) / 100 * 30, 30)
        score += growth
        details["growth"] = growth
        
        # Search Volume (0-25 Punkte)
        volume = kw.get("search_volume", 0)
        if volume >= 10000:
            volume_score = 25
        elif volume >= 5000:
            volume_score = 20
        elif volume >= 1000:
            volume_score = 15
        else:
            volume_score = 5
        score += volume_score
        details["volume"] = volume_score
        
        # CPC (0-20 Punkte) - höher = besser
        cpc = kw.get("cpc", 0)
        if cpc >= 5:
            cpc_score = 20
        elif cpc >= 2:
            cpc_score = 15
        elif cpc >= 0.5:
            cpc_score = 10
        else:
            cpc_score = 5
        score += cpc_score
        details["cpc"] = cpc_score
        
        # Competition (0-25 Punkte) - niedrig = besser
        competition = kw.get("competition_level", "medium")
        if competition == "low":
            comp_score = 25
        elif competition == "medium":
            comp_score = 15
        else:
            comp_score = 5
        score += comp_score
        details["competition"] = comp_score
        
        # Empfehlung
        if score >= 80:
            rec = "⭐ Sehr empfohlen - Hochprofitabel"
        elif score >= 60:
            rec = "✅ Empfohlen - Gutes Potenzial"
        elif score >= 40:
            rec = "⚠️ Bedingt empfohlen"
        else:
            rec = "❌ Nicht empfohlen"
        
        return {
            "overall": round(score, 1),
            "details": details,
            "recommendation": rec,
        }

    # =========================================================================
    # NISCHEN DISCOVERY
    # =========================================================================

    def _discover_niches(self) -> List[Dict]:
        """Finde profitable Nischen"""
        print("[*] Entdecke Nischen...")
        
        keywords = self.db.get_trending_keywords(limit=200)
        
        niches = {}
        
        # Gruppiere Keywords zu Nischen
        for kw in keywords:
            niche_name = self._extract_niche(kw["keyword"])
            
            if niche_name not in niches:
                niches[niche_name] = {
                    "name": niche_name,
                    "keywords": [],
                    "total_volume": 0,
                    "avg_growth": 0,
                    "avg_cpc": 0,
                }
            
            niches[niche_name]["keywords"].append(kw["keyword"])
            niches[niche_name]["total_volume"] += kw.get("search_volume", 0)
            niches[niche_name]["avg_growth"] += kw.get("growth_rate", 0)
            niches[niche_name]["avg_cpc"] += kw.get("cpc", 0) if kw.get("cpc") else 0
        
        # Berechne Durchschnitte und Scores
        discovered_niches = []
        for niche_name, niche_data in niches.items():
            keyword_count = len(niche_data["keywords"])
            niche_data["avg_growth"] /= keyword_count
            niche_data["avg_cpc"] /= keyword_count if keyword_count > 0 else 1
            
            niche_score = self._calculate_niche_score(niche_data)
            
            if niche_score > 50:
                self.db.add_niche(
                    name=niche_name,
                    keywords=niche_data["keywords"],
                    search_volume=niche_data["total_volume"],
                    competition_level="medium",
                    profit_potential="high" if niche_score > 75 else "medium",
                    cpc=niche_data["avg_cpc"],
                    score=niche_score,
                    discovered_from="trend_analyzer"
                )
                
                discovered_niches.append({
                    "niche": niche_name,
                    "keyword_count": keyword_count,
                    "total_search_volume": niche_data["total_volume"],
                    "avg_growth_rate": round(niche_data["avg_growth"], 1),
                    "avg_cpc": round(niche_data["avg_cpc"], 2),
                    "niche_score": niche_score,
                    "recommendation": "⭐ HOT NICHE" if niche_score > 75 else "✅ GOOD NICHE",
                })
        
        discovered_niches.sort(key=lambda x: x["niche_score"], reverse=True)
        return discovered_niches[:20]

    def _extract_niche(self, keyword: str) -> str:
        """Extrahiere Nische aus Keyword"""
        # Simple Heuristik - würde in Production komplexer sein
        words = keyword.lower().split()
        
        # Kategorisierung
        if any(w in words for w in ["ai", "machine", "learning", "artificial"]):
            return "AI & Machine Learning"
        elif any(w in words for w in ["affiliate", "marketing", "money", "earn"]):
            return "Affiliate Marketing"
        elif any(w in words for w in ["business", "startup", "entrepreneur"]):
            return "Business & Entrepreneurship"
        elif any(w in words for w in ["automation", "workflow", "tool"]):
            return "Business Automation"
        elif any(w in words for w in ["digital", "online", "saas"]):
            return "Digital Products & SaaS"
        else:
            return "General"

    def _calculate_niche_score(self, niche_data: Dict) -> float:
        """Berechne Nischen-Profitabilitäts-Score"""
        score = 0
        
        # Suchvolumen (0-30)
        volume = niche_data["total_volume"]
        if volume > 100000:
            score += 30
        elif volume > 50000:
            score += 25
        elif volume > 10000:
            score += 20
        else:
            score += 10
        
        # Growth Rate (0-30)
        growth = niche_data["avg_growth"]
        score += min(growth / 10, 30)
        
        # CPC (0-20)
        cpc = niche_data["avg_cpc"]
        if cpc > 3:
            score += 20
        elif cpc > 1:
            score += 15
        else:
            score += 10
        
        # Keyword Diversität (0-20)
        keyword_count = len(niche_data["keywords"])
        score += min(keyword_count / 5, 20)
        
        return round(score, 1)

    # =========================================================================
    # VIRALE INHALTE ANALYSE
    # =========================================================================

    def _analyze_viral_content(self) -> Dict:
        """Analysiere virale Videos und Trends"""
        print("[*] Analysiere virale Inhalte...")
        
        tiktok_trends = self.db.get_tiktok_trends(limit=20)
        twitter_trends = self.db.get_twitter_trends(limit=20)
        
        return {
            "viral_tiktok_hashtags": [
                {
                    "hashtag": t["hashtag"],
                    "views": t["view_count"],
                    "monetization": t["monetization_potential"]
                } for t in tiktok_trends[:5]
            ],
            "viral_twitter_topics": [
                {
                    "trend": t["trend_name"],
                    "volume": t["tweet_volume"],
                    "rank": t["rank"]
                } for t in twitter_trends[:5]
            ],
        }

    # =========================================================================
    # OPPORTUNITY FINDER
    # =========================================================================

    def _find_opportunities(self) -> Dict:
        """Finde beste Geschäftsmöglichkeiten"""
        print("[*] Suche nach Opportunities...")
        
        opportunities = {
            "emerging_niches": [],
            "low_competition_high_volume": [],
            "high_cpc_keywords": [],
        }
        
        keywords = self.db.get_trending_keywords(limit=100)
        
        for kw in keywords:
            # Emerging Niches (wachsend aber noch wenig Konkurrenz)
            if kw.get("growth_rate", 0) > 100 and kw.get("competition_level") == "low":
                opportunities["emerging_niches"].append({
                    "keyword": kw["keyword"],
                    "growth": kw["growth_rate"],
                    "competition": "Low",
                })
            
            # High Volume, Low Competition
            if kw.get("search_volume", 0) > 10000 and kw.get("competition_level") in ["low", "medium"]:
                opportunities["low_competition_high_volume"].append({
                    "keyword": kw["keyword"],
                    "volume": kw["search_volume"],
                    "cpc": kw.get("cpc", 0),
                })
            
            # High CPC Keywords
            if kw.get("cpc", 0) > 5:
                opportunities["high_cpc_keywords"].append({
                    "keyword": kw["keyword"],
                    "cpc": kw["cpc"],
                    "volume": kw.get("search_volume", 0),
                })
        
        return opportunities

    # =========================================================================
    # COMPETITOR ANALYSE
    # =========================================================================

    def analyze_competitors(self, niche: str) -> List[Dict]:
        """Analysiere Competitor in einer Nische"""
        print(f"[*] Analysiere Competitors in {niche}...")
        
        competitors = self.db.get_competitors_in_niche(niche)
        
        analyzed = []
        for comp in competitors:
            analyzed.append({
                "domain": comp["domain"],
                "estimated_traffic": comp["estimated_traffic"],
                "backlinks": comp["backlink_count"],
                "programs": json.loads(comp["affiliate_programs"]) if comp["affiliate_programs"] else [],
                "strategy": comp["content_strategy"],
            })
        
        return analyzed

    def get_analysis_summary(self) -> Dict:
        """Kurzzusammenfassung der Analyse"""
        analysis = self.analyze_trends()
        
        return {
            "hot_keywords_count": len(analysis["trending_keywords"]),
            "hot_niches_count": len(analysis["hot_niches"]),
            "top_opportunity": analysis["opportunities"]["emerging_niches"][0] if analysis["opportunities"]["emerging_niches"] else None,
            "analysis_date": datetime.now().isoformat(),
        }

    def close(self):
        self.db.close()

if __name__ == "__main__":
    analyzer = TrendAnalyzer()
    
    analysis = analyzer.analyze_trends()
    
    print("\n" + "="*60)
    print("📊 TREND-ANALYSE ZUSAMMENFASSUNG")
    print("="*60)
    print(f"\n🔥 Hot Keywords: {len(analysis['trending_keywords'])}")
    if analysis["trending_keywords"]:
        print(f"   Top: {analysis['trending_keywords'][0]['keyword']} (Score: {analysis['trending_keywords'][0]['profitability_score']})")
    
    print(f"\n🎯 Heiße Nischen: {len(analysis['hot_niches'])}")
    if analysis["hot_niches"]:
        print(f"   Top: {analysis['hot_niches'][0]['niche']} (Score: {analysis['hot_niches'][0]['niche_score']})")
    
    print(f"\n💎 Opportunities: {len(analysis['opportunities']['emerging_niches'])} Emerging Niches")
    
    analyzer.close()
