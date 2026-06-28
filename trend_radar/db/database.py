"""
Trend-Radar Datenbank
Speichert Trends, Keywords, Nischen und Competitor-Daten
"""
import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Optional

class TrendDatabase:
    def __init__(self, db_path: str = "trend_radar/db/trends.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = None
        self.init_db()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def init_db(self):
        """Erstelle alle Tabellen"""
        conn = self.connect()
        cursor = conn.cursor()

        # =====================================================================
        # TRENDING KEYWORDS
        # =====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS trending_keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            region TEXT NOT NULL,
            source TEXT NOT NULL,
            search_volume INTEGER,
            growth_rate REAL,
            trend_value INTEGER,
            is_rising BOOLEAN,
            related_keywords TEXT,
            cpc REAL,
            competition_level TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(keyword, region, source)
        )
        """)

        # =====================================================================
        # NISCHEN
        # =====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS niches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            keywords TEXT,
            search_volume INTEGER,
            competition_level TEXT,
            profit_potential TEXT,
            cpc REAL,
            related_keywords TEXT,
            affiliated_programs TEXT,
            score REAL,
            discovered_from TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # =====================================================================
        # TIKTOK TRENDS
        # =====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tiktok_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hashtag TEXT NOT NULL,
            region TEXT NOT NULL,
            view_count INTEGER,
            video_count INTEGER,
            trend_rank INTEGER,
            growth_rate REAL,
            description TEXT,
            related_hashtags TEXT,
            monetization_potential TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(hashtag, region)
        )
        """)

        # =====================================================================
        # YOUTUBE TRENDS
        # =====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS youtube_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            channel TEXT,
            category TEXT,
            view_count INTEGER,
            like_count INTEGER,
            comment_count INTEGER,
            region TEXT,
            trend_score REAL,
            keywords TEXT,
            upload_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # =====================================================================
        # TWITTER/X TRENDS
        # =====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS twitter_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trend_name TEXT NOT NULL,
            region TEXT NOT NULL,
            tweet_volume INTEGER,
            rank INTEGER,
            promoted BOOLEAN DEFAULT 0,
            sentiment TEXT,
            related_keywords TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(trend_name, region)
        )
        """)

        # =====================================================================
        # REDDIT DISCUSSIONS
        # =====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reddit_discussions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id TEXT UNIQUE NOT NULL,
            subreddit TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            score INTEGER,
            comment_count INTEGER,
            keywords TEXT,
            sentiment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # =====================================================================
        # AFFILIATE PROGRAMME (neu erkannt)
        # =====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS discovered_programs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            network TEXT NOT NULL,
            commission_rate REAL,
            categories TEXT,
            relevant_niches TEXT,
            discovered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_source TEXT,
            status TEXT DEFAULT 'new'
        )
        """)

        # =====================================================================
        # COMPETITOR TRACKING
        # =====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS competitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT UNIQUE NOT NULL,
            niche TEXT,
            targeting_keywords TEXT,
            estimated_traffic INTEGER,
            backlink_count INTEGER,
            affiliate_programs TEXT,
            content_strategy TEXT,
            last_analyzed TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # =====================================================================
        # TREND SCORES & ANALYTICS
        # =====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS trend_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id INTEGER,
            entity_type TEXT,
            profitability_score REAL,
            competition_score REAL,
            traffic_potential REAL,
            trend_velocity REAL,
            overall_score REAL,
            recommendation TEXT,
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # =====================================================================
        # SCAN LOG
        # =====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            region TEXT,
            items_found INTEGER,
            scan_duration_seconds REAL,
            status TEXT,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        print("[✓] Trend-Datenbank initialisiert")

    def close(self):
        if self.conn:
            self.conn.close()

    # =========================================================================
    # TRENDING KEYWORDS
    # =========================================================================

    def add_keyword(self, keyword: str, region: str, source: str, **kwargs) -> int:
        cursor = self.connect().cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO trending_keywords 
        (keyword, region, source, search_volume, growth_rate, trend_value, 
         is_rising, cpc, competition_level, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (keyword, region, source, kwargs.get("search_volume"), 
              kwargs.get("growth_rate"), kwargs.get("trend_value"),
              kwargs.get("is_rising", 0), kwargs.get("cpc"),
              kwargs.get("competition_level", "medium"), datetime.now()))
        self.conn.commit()
        return cursor.lastrowid

    def get_trending_keywords(self, region: str = None, limit: int = 50) -> List[Dict]:
        cursor = self.connect().cursor()
        if region:
            cursor.execute("""
            SELECT * FROM trending_keywords 
            WHERE region = ? AND is_rising = 1
            ORDER BY growth_rate DESC LIMIT ?
            """, (region, limit))
        else:
            cursor.execute("""
            SELECT * FROM trending_keywords 
            WHERE is_rising = 1
            ORDER BY growth_rate DESC LIMIT ?
            """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    # =========================================================================
    # NICHES
    # =========================================================================

    def add_niche(self, name: str, **kwargs) -> int:
        cursor = self.connect().cursor()
        cursor.execute("""
        INSERT INTO niches 
        (name, keywords, search_volume, competition_level, profit_potential, 
         cpc, score, discovered_from)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, json.dumps(kwargs.get("keywords", [])),
              kwargs.get("search_volume"), kwargs.get("competition_level"),
              kwargs.get("profit_potential"), kwargs.get("cpc"),
              kwargs.get("score", 0), kwargs.get("discovered_from")))
        self.conn.commit()
        return cursor.lastrowid

    def get_hot_niches(self, limit: int = 20) -> List[Dict]:
        cursor = self.connect().cursor()
        cursor.execute("""
        SELECT * FROM niches 
        ORDER BY score DESC, search_volume DESC 
        LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    # =========================================================================
    # TIKTOK TRENDS
    # =========================================================================

    def add_tiktok_trend(self, hashtag: str, region: str, **kwargs) -> int:
        cursor = self.connect().cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO tiktok_trends 
        (hashtag, region, view_count, video_count, trend_rank, growth_rate, 
         monetization_potential)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (hashtag, region, kwargs.get("view_count"),
              kwargs.get("video_count"), kwargs.get("trend_rank"),
              kwargs.get("growth_rate"), kwargs.get("monetization_potential")))
        self.conn.commit()
        return cursor.lastrowid

    def get_tiktok_trends(self, region: str = "US", limit: int = 50) -> List[Dict]:
        cursor = self.connect().cursor()
        cursor.execute("""
        SELECT * FROM tiktok_trends 
        WHERE region = ? 
        ORDER BY view_count DESC 
        LIMIT ?
        """, (region, limit))
        return [dict(row) for row in cursor.fetchall()]

    # =========================================================================
    # TWITTER TRENDS
    # =========================================================================

    def add_twitter_trend(self, trend_name: str, region: str, **kwargs) -> int:
        cursor = self.connect().cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO twitter_trends 
        (trend_name, region, tweet_volume, rank, sentiment)
        VALUES (?, ?, ?, ?, ?)
        """, (trend_name, region, kwargs.get("tweet_volume"),
              kwargs.get("rank"), kwargs.get("sentiment")))
        self.conn.commit()
        return cursor.lastrowid

    def get_twitter_trends(self, region: str = "US", limit: int = 50) -> List[Dict]:
        cursor = self.connect().cursor()
        cursor.execute("""
        SELECT * FROM twitter_trends 
        WHERE region = ? 
        ORDER BY tweet_volume DESC 
        LIMIT ?
        """, (region, limit))
        return [dict(row) for row in cursor.fetchall()]

    # =========================================================================
    # DISCOVERED PROGRAMS
    # =========================================================================

    def add_program(self, name: str, network: str, **kwargs) -> int:
        cursor = self.connect().cursor()
        cursor.execute("""
        INSERT OR IGNORE INTO discovered_programs 
        (name, network, commission_rate, categories, data_source)
        VALUES (?, ?, ?, ?, ?)
        """, (name, network, kwargs.get("commission_rate"),
              json.dumps(kwargs.get("categories", [])),
              kwargs.get("data_source")))
        self.conn.commit()
        return cursor.lastrowid

    def get_new_programs(self) -> List[Dict]:
        cursor = self.connect().cursor()
        cursor.execute("SELECT * FROM discovered_programs WHERE status = 'new' LIMIT 50")
        return [dict(row) for row in cursor.fetchall()]

    # =========================================================================
    # COMPETITORS
    # =========================================================================

    def add_competitor(self, domain: str, **kwargs) -> int:
        cursor = self.connect().cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO competitors 
        (domain, niche, targeting_keywords, estimated_traffic, backlink_count, 
         affiliate_programs, content_strategy, last_analyzed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (domain, kwargs.get("niche"),
              json.dumps(kwargs.get("keywords", [])),
              kwargs.get("traffic"), kwargs.get("backlinks"),
              json.dumps(kwargs.get("programs", [])),
              kwargs.get("strategy"), datetime.now()))
        self.conn.commit()
        return cursor.lastrowid

    def get_competitors_in_niche(self, niche: str) -> List[Dict]:
        cursor = self.connect().cursor()
        cursor.execute("SELECT * FROM competitors WHERE niche = ? ORDER BY estimated_traffic DESC", (niche,))
        return [dict(row) for row in cursor.fetchall()]

    # =========================================================================
    # SCAN LOG
    # =========================================================================

    def log_scan(self, source: str, region: str = None, items_found: int = 0, 
                 duration: float = 0, status: str = "success", error: str = None):
        cursor = self.connect().cursor()
        cursor.execute("""
        INSERT INTO scan_logs 
        (source, region, items_found, scan_duration_seconds, status, error_message)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (source, region, items_found, duration, status, error))
        self.conn.commit()

if __name__ == "__main__":
    db = TrendDatabase()
    print("[✓] Trend-DB erfolgreich initialisiert!")
    db.close()
