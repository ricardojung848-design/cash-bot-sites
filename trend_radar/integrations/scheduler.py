"""
Trend-Radar Scheduler
Führt tägliche automatische Trend-Scans durch
"""
import json
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from trend_radar.config import TREND_SCHEDULER
from trend_radar.scrapers.trend_scraper import TrendScraper
from trend_radar.analyzers.trend_analyzer import TrendAnalyzer

class TrendRadarScheduler:
    """Scheduler für automatische Trend-Analysen"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scraper = TrendScraper()
        self.analyzer = TrendAnalyzer()
        self.jobs = []

    def start(self):
        """Starten Sie den Scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            print("[✓] Trend-Radar Scheduler gestartet")

    def stop(self):
        """Stoppe den Scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("[✓] Trend-Radar Scheduler gestoppt")

    def schedule_daily_scan(self):
        """Plane täglichen Scan"""
        hour = TREND_SCHEDULER["daily_scan_hour"]
        minute = TREND_SCHEDULER["daily_scan_minute"]
        timezone = TREND_SCHEDULER["timezone"]
        
        self.scheduler.add_job(
            func=self.run_daily_scan,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=timezone),
            id="daily_trend_scan",
            name="Täglicher Trend-Scan",
            replace_existing=True,
        )
        
        print(f"[✓] Täglicher Scan geplant für {hour:02d}:{minute:02d} {timezone}")

    def run_daily_scan(self):
        """Führe täglichen Trend-Scan durch"""
        print(f"\n{'='*70}")
        print(f"[🔍] Starte Trend-Radar Scan: {datetime.now()}")
        print(f"{'='*70}\n")
        
        try:
            # 1. Scrape alle Quellen
            print("[PHASE 1] Trends scrapen...\n")
            scan_results = self.scraper.scan_all_sources(
                regions=["US", "DE", "UK", "FR", "ES", "IT", "JP", "AU", "CA"]
            )
            
            # 2. Analysiere Trends
            print("\n[PHASE 2] Trends analysieren...\n")
            analysis = self.analyzer.analyze_trends()
            
            # 3. Generiere Report
            print("\n[PHASE 3] Generiere Report...\n")
            report = self._generate_report(scan_results, analysis)
            
            # 4. Exportiere Daten
            print("\n[PHASE 4] Exportiere Daten...\n")
            self._export_results(report)
            
            print(f"\n{'='*70}")
            print(f"[✓] Scan abgeschlossen! {datetime.now()}")
            print(f"{'='*70}\n")
            
        except Exception as e:
            print(f"\n[-] Fehler beim Scan: {e}\n")

    def _generate_report(self, scan_results: dict, analysis: dict) -> dict:
        """Generiere Scan-Report"""
        
        report = {
            "scan_date": datetime.now().isoformat(),
            "sources_scanned": {
                "google_trends": len(scan_results.get("google_trends", [])),
                "tiktok_trends": len(scan_results.get("tiktok_trends", [])),
                "youtube_trends": len(scan_results.get("youtube_trends", [])),
                "twitter_trends": len(scan_results.get("twitter_trends", [])),
                "reddit_trends": len(scan_results.get("reddit_trends", [])),
                "affiliate_programs": len(scan_results.get("affiliate_programs", [])),
            },
            "hot_keywords": analysis.get("trending_keywords", [])[:10],
            "hot_niches": analysis.get("hot_niches", [])[:10],
            "viral_content": analysis.get("viral_content", {}),
            "opportunities": analysis.get("opportunities", {}),
            "stats": {
                "total_keywords_analyzed": len(analysis.get("trending_keywords", [])),
                "total_niches_discovered": len(analysis.get("hot_niches", [])),
                "total_opportunities": sum(len(v) if isinstance(v, list) else 0 
                                          for v in analysis.get("opportunities", {}).values()),
            }
        }
        
        return report

    def _export_results(self, report: dict):
        """Exportiere Ergebnisse"""
        os.makedirs("trend_radar/exports", exist_ok=True)
        
        # JSON Export
        json_path = f"trend_radar/exports/trend_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"[✓] Report exportiert: {json_path}")
        
        # CSV Export (Keywords)
        csv_path = f"trend_radar/exports/keywords_{datetime.now().strftime('%Y%m%d')}.csv"
        if report.get("hot_keywords"):
            import csv
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["keyword", "growth_rate", "cpc", "profitability_score"])
                writer.writeheader()
                for kw in report["hot_keywords"]:
                    writer.writerow(kw)
            print(f"[✓] CSV exportiert: {csv_path}")

    def get_next_scan_time(self):
        """Hole nächste Scan-Zeit"""
        for job in self.scheduler.get_jobs():
            if job.id == "daily_trend_scan":
                return str(job.next_run_time)
        return "Nicht geplant"

    def manual_scan(self):
        """Führe manuellen Scan durch"""
        print("[*] Starte manuellen Trend-Scan...")
        self.run_daily_scan()

    def get_status(self) -> dict:
        """Hole Scheduler-Status"""
        return {
            "scheduler_running": self.scheduler.running,
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": str(job.next_run_time),
                } for job in self.scheduler.get_jobs()
            ],
            "timestamp": datetime.now().isoformat(),
        }

if __name__ == "__main__":
    scheduler = TrendRadarScheduler()
    scheduler.start()
    scheduler.schedule_daily_scan()
    
    print(json.dumps(scheduler.get_status(), indent=2, default=str))
    
    # Für Testing:
    # scheduler.manual_scan()
