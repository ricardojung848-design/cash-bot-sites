"""
Trend-Radar Main API
Integration mit Affiliate-Engine
"""
import json
from datetime import datetime
from typing import Dict, List
from trend_radar.scrapers.trend_scraper import TrendScraper
from trend_radar.analyzers.trend_analyzer import TrendAnalyzer
from trend_radar.db.database import TrendDatabase
from trend_radar.integrations.scheduler import TrendRadarScheduler

class TrendRadarEngine:
    """Haupt-API für Trend-Radar System"""
    
    def __init__(self):
        self.db = TrendDatabase()
        self.scraper = TrendScraper()
        self.analyzer = TrendAnalyzer()
        self.scheduler = TrendRadarScheduler()

    # =========================================================================
    # ÖFFENTLICHE API
    # =========================================================================

    def get_hot_keywords(self, limit: int = 50, region: str = None) -> List[Dict]:
        """Hole heiße Keywords"""
        keywords = self.db.get_trending_keywords(region=region, limit=limit)
        return [dict(kw) for kw in keywords]

    def get_hot_niches(self, limit: int = 20) -> List[Dict]:
        """Hole heiße Nischen"""
        niches = self.db.get_hot_niches(limit=limit)
        return [dict(niche) for niche in niches]

    def get_viral_trends(self, platform: str = "tiktok", region: str = "US") -> List[Dict]:
        """Hole virale Trends von Platform"""
        if platform == "tiktok":
            trends = self.db.get_tiktok_trends(region=region)
        elif platform == "twitter":
            trends = self.db.get_twitter_trends(region=region)
        else:
            trends = []
        
        return [dict(t) for t in trends]

    def get_discovered_programs(self) -> List[Dict]:
        """Hole neu entdeckte Affiliate-Programme"""
        programs = self.db.get_new_programs()
        return [dict(p) for p in programs]

    def get_full_analysis(self) -> Dict:
        """Hole komplette Trend-Analyse"""
        analysis = self.analyzer.analyze_trends()
        return analysis

    def get_opportunities(self) -> Dict:
        """Hole beste Geschäftsmöglichkeiten"""
        # Kombiniere Daten aus verschiedenen Quellen
        opportunities = {
            "emerging_niches": self._get_emerging_niches(),
            "high_potential_keywords": self._get_high_potential_keywords(),
            "low_competition_markets": self._get_low_competition_markets(),
            "timestamp": datetime.now().isoformat(),
        }
        return opportunities

    def get_competitor_analysis(self, niche: str) -> List[Dict]:
        """Hole Competitor-Analyse für Nische"""
        return self.analyzer.analyze_competitors(niche)

    # =========================================================================
    # SCHEDULER CONTROL
    # =========================================================================

    def start_scheduler(self):
        """Starte Scheduler"""
        self.scheduler.start()
        self.scheduler.schedule_daily_scan()
        return {"status": "Scheduler gestartet"}

    def stop_scheduler(self):
        """Stoppe Scheduler"""
        self.scheduler.stop()
        return {"status": "Scheduler gestoppt"}

    def manual_scan(self):
        """Führe manuellen Scan durch"""
        self.scheduler.manual_scan()
        return {"status": "Manueller Scan gestartet"}

    def get_scheduler_status(self) -> Dict:
        """Hole Scheduler-Status"""
        return self.scheduler.get_status()

    # =========================================================================
    # INTEGRATION MIT AFFILIATE-ENGINE
    # =========================================================================

    def get_recommendations_for_affiliate(self) -> Dict:
        """
        Gebe Empfehlungen für Affiliate-Engine
        Diese Daten können direkt von der Affiliate-Engine genutzt werden
        """
        hot_niches = self.get_hot_niches(limit=10)
        hot_keywords = self.get_hot_keywords(limit=20)
        opportunities = self.get_opportunities()
        
        recommendations = {
            "suggested_landing_pages": [
                {
                    "topic": niche["niche"],
                    "keywords": niche.get("keywords", []),
                    "priority": "high" if niche["niche_score"] > 75 else "medium",
                    "estimated_traffic": niche["total_search_volume"],
                } for niche in hot_niches[:5]
            ],
            "trending_keywords_to_target": hot_keywords[:10],
            "quick_opportunities": opportunities["emerging_niches"][:5],
            "generation_timestamp": datetime.now().isoformat(),
        }
        
        return recommendations

    # =========================================================================
    # PRIVATE HELPER
    # =========================================================================

    def _get_emerging_niches(self) -> List[Dict]:
        """Hole Emerging Niches"""
        niches = self.get_hot_niches(limit=50)
        return [n for n in niches if n.get("niche_score", 0) > 70][:10]

    def _get_high_potential_keywords(self) -> List[Dict]:
        """Hole High-Potential Keywords"""
        keywords = self.get_hot_keywords(limit=100)
        return [k for k in keywords if k.get("profitability_score", 0) > 75][:10]

    def _get_low_competition_markets(self) -> List[Dict]:
        """Hole Low-Competition Markets"""
        keywords = self.get_hot_keywords(limit=100)
        return [k for k in keywords 
                if k.get("competition") == "low" 
                and k.get("search_volume", 0) > 5000][:10]

    # =========================================================================
    # EXPORT
    # =========================================================================

    def export_analysis_report(self, filename: str = None) -> str:
        """Exportiere kompletten Analysis-Report"""
        if filename is None:
            filename = f"trend_radar_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "report_date": datetime.now().isoformat(),
            "hot_keywords": self.get_hot_keywords(limit=50),
            "hot_niches": self.get_hot_niches(limit=20),
            "viral_trends": {
                "tiktok": self.get_viral_trends("tiktok")[:10],
                "twitter": self.get_viral_trends("twitter")[:10],
            },
            "opportunities": self.get_opportunities(),
            "recommendations": self.get_recommendations_for_affiliate(),
        }
        
        with open(f"trend_radar/exports/{filename}", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return f"Report exportiert: trend_radar/exports/{filename}"

    def close(self):
        """Schließe alle Verbindungen"""
        self.db.close()
        self.scraper.close()
        self.analyzer.close()

if __name__ == "__main__":
    import sys
    
    engine = TrendRadarEngine()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "scan":
            engine.manual_scan()
        elif command == "start":
            engine.start_scheduler()
        elif command == "status":
            print(json.dumps(engine.get_scheduler_status(), indent=2, default=str))
        elif command == "hot-keywords":
            print(json.dumps(engine.get_hot_keywords(limit=20), indent=2, default=str))
        elif command == "hot-niches":
            print(json.dumps(engine.get_hot_niches(limit=10), indent=2, default=str))
        elif command == "opportunities":
            print(json.dumps(engine.get_opportunities(), indent=2, default=str))
        elif command == "recommendations":
            print(json.dumps(engine.get_recommendations_for_affiliate(), indent=2, default=str))
        elif command == "export":
            print(engine.export_analysis_report())
        else:
            print(f"Unknown command: {command}")
    else:
        print("""
        Trend-Radar Engine
        
        Verfügbare Befehle:
        - scan                : Manuellen Scan ausführen
        - start              : Scheduler starten
        - status             : Scheduler-Status anzeigen
        - hot-keywords       : Heiße Keywords anzeigen
        - hot-niches         : Heiße Nischen anzeigen
        - opportunities      : Geschäftsmöglichkeiten anzeigen
        - recommendations    : Affiliate-Empfehlungen
        - export             : Report exportieren
        """)
    
    engine.close()
