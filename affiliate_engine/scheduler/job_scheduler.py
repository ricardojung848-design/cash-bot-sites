"""
Scheduler für automatische tägliche Content-Generierung
"""
import os
import json
from datetime import datetime
from typing import Dict, List
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from affiliate_engine.config import SCHEDULER_CONFIG
from affiliate_engine.db.database import AffiliateDatabase
from affiliate_engine.generators.program_selector import ProgramSelector
from affiliate_engine.generators.content_generator import ContentGenerator
from affiliate_engine.generators.tracking_manager import TrackingLinkManager

class SchedulerManager:
    """Verwaltet automatische Content-Generierung"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.db = AffiliateDatabase()
        self.program_selector = ProgramSelector()
        self.content_gen = ContentGenerator()
        self.tracking_manager = TrackingLinkManager()
        self.jobs = []

    def start(self):
        """Starten Sie den Scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            print("[✓] Scheduler gestartet")

    def stop(self):
        """Stoppe den Scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("[✓] Scheduler gestoppt")

    def schedule_daily_generation(self):
        """
        Plane tägliche Content-Generierung
        """
        hour = SCHEDULER_CONFIG["daily_generation_hour"]
        minute = SCHEDULER_CONFIG["daily_generation_minute"]
        timezone = SCHEDULER_CONFIG["timezone"]
        
        # Lösche existierende Jobs
        self.scheduler.remove_all_jobs()
        
        # Füge neuen Job ein
        self.scheduler.add_job(
            func=self.generate_daily_content,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=timezone),
            id="daily_content_generation",
            name="Tägliche Content-Generierung",
            replace_existing=True,
        )
        
        # Speichere Job in Datenbank
        self.db.connect()
        cursor = self.db.conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO scheduler_jobs 
        (job_name, job_type, schedule_cron, status)
        VALUES (?, ?, ?, ?)
        """, ("daily_content_generation", "content_generation", 
              f"{minute} {hour} * * *", "active"))
        self.db.conn.commit()
        
        print(f"[✓] Tägliche Generierung geplant für {hour:02d}:{minute:02d} {timezone}")

    def schedule_analytics_update(self):
        """Plane tägliche Analytics-Updates"""
        self.scheduler.add_job(
            func=self.update_analytics,
            trigger=CronTrigger(hour=3, minute=0),
            id="daily_analytics_update",
            name="Tägliche Analytics-Updates",
            replace_existing=True,
        )
        print("[✓] Analytics-Update geplant für 03:00 UTC")

    def generate_daily_content(self):
        """
        Generiere täglich neue Landing Pages
        """
        print(f"\n{'='*60}")
        print(f"[*] Starte tägliche Content-Generierung: {datetime.now()}")
        print(f"{'='*60}\n")
        
        try:
            # 1. Hole zu generierende Themen aus Config oder Datei
            topics = self._load_daily_topics()
            
            if not topics:
                print("[-] Keine Themen zum Generieren gefunden")
                return
            
            print(f"[*] Generiere Content für {len(topics)} Themen...")
            
            generated_count = 0
            
            for topic in topics:
                try:
                    result = self._generate_single_landing_page(topic)
                    if result["status"] == "success":
                        generated_count += 1
                        print(f"[✓] {result['title']}")
                    else:
                        print(f"[-] Fehler bei {topic}: {result.get('error')}")
                except Exception as e:
                    print(f"[-] Exception bei {topic}: {e}")
                    continue
            
            print(f"\n[✓] {generated_count}/{len(topics)} Landing Pages erfolgreich generiert!")
            
            # Updatee nächsten Job
            self.db.connect()
            cursor = self.db.conn.cursor()
            cursor.execute("""
            UPDATE scheduler_jobs 
            SET last_run = ?, next_run = datetime('now', '+1 day')
            WHERE job_name = ?
            """, (datetime.now(), "daily_content_generation"))
            self.db.conn.commit()
            
        except Exception as e:
            print(f"[-] Fehler bei Generierung: {e}")

    def _generate_single_landing_page(self, topic: Dict) -> Dict:
        """Generiere eine einzelne Landing Page"""
        
        title = topic.get("title", topic)
        keywords = topic.get("keywords", [])
        main_keyword = keywords[0] if keywords else title
        
        # 1. Wähle Programme
        programs = self.program_selector.select_programs_for_topic(
            topic=title,
            keywords=keywords,
            max_programs=5
        )
        
        # 2. Generiere Content
        content_result = self.content_gen.generate_article(
            topic=title,
            main_keyword=main_keyword,
            keywords=keywords,
            programs=programs
        )
        
        if content_result["status"] != "success":
            return content_result
        
        # 3. Erstelle Landing Page in DB
        slug = title.lower().replace(" ", "-").replace("ä", "ae").replace("ö", "oe")
        lp_id = self.db.add_landing_page(
            title=title,
            slug=slug,
            topic=title,
            content=content_result["content"],
            affiliate_programs=programs,
            seo_keywords=keywords,
            main_keyword=main_keyword,
            meta_description=content_result["meta_description"],
            h1_title=content_result["h1_title"],
            status="published"
        )
        
        # 4. Erstelle Tracking-Links
        tracking_links = self.tracking_manager.create_bulk_tracking_links(
            landing_page_id=lp_id,
            programs=programs,
            campaign_name=title
        )
        
        # 5. Füge Tracking-Links in Content ein
        final_html = self.content_gen.generate_landing_page(
            topic=title,
            article_content=content_result["content"],
            programs=programs
        )
        
        # 6. Speichere HTML-Datei
        html_filename = f"affiliate_engine/web/pages/{slug}.html"
        os.makedirs(os.path.dirname(html_filename), exist_ok=True)
        
        with open(html_filename, "w", encoding="utf-8") as f:
            f.write(final_html)
        
        # 7. Update LP mit Dateipfad
        self.db.update_landing_page(
            lp_id=lp_id,
            html_file_path=html_filename,
            published_at=datetime.now()
        )
        
        return {
            "status": "success",
            "title": title,
            "lp_id": lp_id,
            "filename": html_filename,
            "tracking_links": len(tracking_links),
            "keywords": keywords,
        }

    def _load_daily_topics(self) -> list:
        """Lade Themen zum Generieren"""
        # Versuche aus Konfigurationsdatei zu laden
        topics_file = "affiliate_engine/topics.json"
        
        if os.path.exists(topics_file):
            try:
                with open(topics_file, "r", encoding="utf-8") as f:
                    topics = json.load(f)
                return topics
            except:
                pass
        
        # Standard-Themen für Demo
        return [
            {
                "title": "Business Automation mit Zapier",
                "keywords": ["Zapier", "Workflow", "Automation", "Integration"]
            },
            {
                "title": "Make.com – Die bessere Alternative zu Zapier",
                "keywords": ["Make", "Automation", "Integration", "Workflow"]
            },
            {
                "title": "HubSpot CRM für Anfänger – Guide 2024",
                "keywords": ["HubSpot", "CRM", "Sales", "Marketing"]
            },
        ]

    def update_analytics(self):
        """Update tägliche Analytics"""
        print(f"\n[*] Update Analytics: {datetime.now()}")
        # TODO: Implementiere Analytics-Update
        pass

    def get_job_status(self) -> Dict:
        """Hole Status aller Jobs"""
        jobs_status = []
        
        for job in self.scheduler.get_jobs():
            jobs_status.append({
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time),
                "status": "active"
            })
        
        return {
            "scheduler_running": self.scheduler.running,
            "total_jobs": len(jobs_status),
            "jobs": jobs_status,
            "timestamp": datetime.now().isoformat(),
        }

    def test_generation(self):
        """Teste Content-Generierung einmalig"""
        print("[*] Starte Test-Generierung...")
        self.generate_daily_content()

if __name__ == "__main__":
    manager = SchedulerManager()
    manager.start()
    manager.schedule_daily_generation()
    manager.schedule_analytics_update()
    
    print("\n[✓] Scheduler läuft!")
    print(json.dumps(manager.get_job_status(), indent=2, ensure_ascii=False, default=str))
    
    # Für Testing: Kommentiere folgende Zeile aus
    # manager.test_generation()
