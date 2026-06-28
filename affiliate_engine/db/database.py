"""
Datenbank-Manager für Affiliate Engine
Verwaltet alle Tabellen: Programme, Content, Links, Tracking
"""
import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class AffiliateDatabase:
    def __init__(self, db_path: str = "affiliate_engine/db/affiliate_engine.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = None
        self.init_db()

    def connect(self):
        """Verbindung zur Datenbank"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def init_db(self):
        """Erstelle alle Tabellen"""
        conn = self.connect()
        cursor = conn.cursor()

        # =====================================================================
        # AFFILIATE PROGRAMME
        # =====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS affiliate_programs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            network TEXT NOT NULL,
            api_endpoint TEXT,
            commission_rate REAL,
            min_commission REAL,
            max_commission REAL,
            cookie_lifetime INTEGER,
            categories TEXT,
            payout_method TEXT,
            min_payout REAL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # =====================================================================
        # KEYWORDS & NISCHEN
        # =====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT UNIQUE NOT NULL,
            search_volume INTEGER,
            difficulty INTEGER,
            competition TEXT,
            program_ids TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # =====================================================================
        # GENERIERTE LANDING PAGES
        # =====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS landing_pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            topic TEXT NOT NULL,
            content TEXT,
            affiliate_programs TEXT,
            seo_keywords TEXT,
            main_keyword TEXT,
            url TEXT,
            html_file_path TEXT,
            meta_description TEXT,
            meta_keywords TEXT,
            h1_title TEXT,
            status TEXT DEFAULT 'draft',
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            published_at TIMESTAMP,
            views INTEGER DEFAULT 0,
            conversions INTEGER DEFAULT 0
        )
        """)

        # =====================================================================
        # TRACKING LINKS
        # =====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tracking_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            landing_page_id INTEGER NOT NULL,
            affiliate_program_id INTEGER NOT NULL,
            original_link TEXT NOT NULL,
            tracking_link TEXT NOT NULL,
            utm_source TEXT,
            utm_medium TEXT,
            utm_campaign TEXT,
            utm_content TEXT,
            short_link TEXT,
            clicks INTEGER DEFAULT 0,
            conversions INTEGER DEFAULT 0,
            revenue REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (landing_page_id) REFERENCES landing_pages(id),
            FOREIGN KEY (affiliate_program_id) REFERENCES affiliate_programs(id)
        )
        """)

        # =====================================================================
        # CONTENT GENERATOR LOG
        # =====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS content_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            landing_page_id INTEGER,
            topic TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            generated_text TEXT,
            error_message TEXT,
            generation_time_seconds REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (landing_page_id) REFERENCES landing_pages(id)
        )
        """)

        # =====================================================================
        # SCHEDULER JOBS
        # =====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scheduler_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT NOT NULL,
            job_type TEXT NOT NULL,
            schedule_cron TEXT,
            last_run TIMESTAMP,
            next_run TIMESTAMP,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # =====================================================================
        # PERFORMANCE ANALYTICS
        # =====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            landing_page_id INTEGER,
            date DATE NOT NULL,
            clicks INTEGER DEFAULT 0,
            impressions INTEGER DEFAULT 0,
            conversions INTEGER DEFAULT 0,
            revenue REAL DEFAULT 0,
            ctr REAL,
            conversion_rate REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (landing_page_id) REFERENCES landing_pages(id)
        )
        """)

        # =====================================================================
        # API CALL LOGS
        # =====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_name TEXT NOT NULL,
            endpoint TEXT,
            method TEXT,
            status_code INTEGER,
            response_time_ms INTEGER,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        print("[✓] Datenbank initialisiert")

    def close(self):
        """Schließe Datenbankverbindung"""
        if self.conn:
            self.conn.close()

    # =========================================================================
    # AFFILIATE PROGRAMME
    # =========================================================================

    def add_program(self, name: str, network: str, **kwargs) -> int:
        """Füge ein Affiliate-Programm hinzu"""
        cursor = self.connect().cursor()
        cursor.execute("""
        INSERT INTO affiliate_programs 
        (name, network, api_endpoint, commission_rate, categories, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (name, network, kwargs.get("api_endpoint"), 
              kwargs.get("commission_rate"), kwargs.get("categories"), 1))
        self.conn.commit()
        return cursor.lastrowid

    def get_all_programs(self) -> List[Dict]:
        """Hole alle aktiven Affiliate-Programme"""
        cursor = self.connect().cursor()
        cursor.execute("SELECT * FROM affiliate_programs WHERE is_active = 1")
        return [dict(row) for row in cursor.fetchall()]

    def get_program_by_name(self, name: str) -> Optional[Dict]:
        """Hole Programm nach Name"""
        cursor = self.connect().cursor()
        cursor.execute("SELECT * FROM affiliate_programs WHERE name = ?", (name,))
        row = cursor.fetchone()
        return dict(row) if row else None

    # =========================================================================
    # LANDING PAGES
    # =========================================================================

    def add_landing_page(self, title: str, slug: str, topic: str, **kwargs) -> int:
        """Erstelle neue Landing Page"""
        cursor = self.connect().cursor()
        cursor.execute("""
        INSERT INTO landing_pages 
        (title, slug, topic, content, affiliate_programs, seo_keywords, 
         main_keyword, meta_description, h1_title, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, slug, topic, kwargs.get("content", ""),
              json.dumps(kwargs.get("affiliate_programs", [])),
              json.dumps(kwargs.get("seo_keywords", [])),
              kwargs.get("main_keyword", ""),
              kwargs.get("meta_description", ""),
              kwargs.get("h1_title", ""),
              kwargs.get("status", "draft")))
        self.conn.commit()
        return cursor.lastrowid

    def get_landing_pages(self, status: str = None) -> List[Dict]:
        """Hole Landing Pages"""
        cursor = self.connect().cursor()
        if status:
            cursor.execute("SELECT * FROM landing_pages WHERE status = ? ORDER BY created_at DESC", (status,))
        else:
            cursor.execute("SELECT * FROM landing_pages ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

    def update_landing_page(self, lp_id: int, **updates):
        """Update Landing Page"""
        cursor = self.connect().cursor()
        updates["updated_at"] = datetime.now()
        cols = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [lp_id]
        cursor.execute(f"UPDATE landing_pages SET {cols} WHERE id = ?", values)
        self.conn.commit()

    # =========================================================================
    # TRACKING LINKS
    # =========================================================================

    def add_tracking_link(self, lp_id: int, prog_id: int, original: str, 
                         tracking: str, **kwargs) -> int:
        """Erstelle Tracking-Link"""
        cursor = self.connect().cursor()
        cursor.execute("""
        INSERT INTO tracking_links 
        (landing_page_id, affiliate_program_id, original_link, tracking_link,
         utm_source, utm_medium, utm_campaign, utm_content)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (lp_id, prog_id, original, tracking,
              kwargs.get("utm_source", ""),
              kwargs.get("utm_medium", ""),
              kwargs.get("utm_campaign", ""),
              kwargs.get("utm_content", "")))
        self.conn.commit()
        return cursor.lastrowid

    def get_tracking_links(self, lp_id: int) -> List[Dict]:
        """Hole Tracking-Links für Landing Page"""
        cursor = self.connect().cursor()
        cursor.execute("SELECT * FROM tracking_links WHERE landing_page_id = ?", (lp_id,))
        return [dict(row) for row in cursor.fetchall()]

    # =========================================================================
    # KEYWORDS
    # =========================================================================

    def add_keyword(self, keyword: str, search_volume: int = 0, difficulty: int = 0):
        """Füge Keyword hinzu"""
        cursor = self.connect().cursor()
        cursor.execute("""
        INSERT OR IGNORE INTO keywords (keyword, search_volume, difficulty)
        VALUES (?, ?, ?)
        """, (keyword, search_volume, difficulty))
        self.conn.commit()

    def get_keywords(self) -> List[Dict]:
        """Hole alle Keywords"""
        cursor = self.connect().cursor()
        cursor.execute("SELECT * FROM keywords ORDER BY search_volume DESC")
        return [dict(row) for row in cursor.fetchall()]

    # =========================================================================
    # ANALYTICS
    # =========================================================================

    def get_analytics(self, days: int = 30) -> Dict:
        """Hole Analytics für letzte N Tage"""
        cursor = self.connect().cursor()
        cursor.execute("""
        SELECT SUM(clicks) as total_clicks, 
               SUM(conversions) as total_conversions,
               SUM(revenue) as total_revenue,
               COUNT(DISTINCT landing_page_id) as active_pages
        FROM analytics 
        WHERE date >= date('now', '-' || ? || ' days')
        """, (days,))
        row = cursor.fetchone()
        return dict(row) if row else {}

    def log_click(self, link_id: int):
        """Registriere Click"""
        cursor = self.connect().cursor()
        cursor.execute("UPDATE tracking_links SET clicks = clicks + 1 WHERE id = ?", (link_id,))
        self.conn.commit()

    def log_conversion(self, link_id: int, revenue: float = 0):
        """Registriere Conversion"""
        cursor = self.connect().cursor()
        cursor.execute("""
        UPDATE tracking_links 
        SET conversions = conversions + 1, revenue = revenue + ? 
        WHERE id = ?
        """, (revenue, link_id))
        self.conn.commit()

if __name__ == "__main__":
    db = AffiliateDatabase()
    print("[✓] Datenbank erfolgreich initialisiert!")
    db.close()
