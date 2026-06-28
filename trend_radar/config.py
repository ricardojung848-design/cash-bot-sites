"""
Trend-Radar Konfiguration
Alle API-Keys und Settings für Trend-Tracking
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# DATENQUELLEN KONFIGURATION
# ============================================================================

TREND_SOURCES = {
    "google_trends": {
        "enabled": True,
        "api_key": os.getenv("GOOGLE_TRENDS_API_KEY", ""),
        "regions": ["US", "DE", "UK", "FR", "ES", "IT", "JP", "AU", "CA"],
        "update_frequency": "daily",
        "fetch_top_n": 50,
    },
    
    "tiktok": {
        "enabled": True,
        "api_key": os.getenv("TIKTOK_API_KEY", ""),
        "bearer_token": os.getenv("TIKTOK_BEARER_TOKEN", ""),
        "regions": ["US", "DE", "UK", "FR", "ES", "IT", "JP", "AU", "CA", "BR", "IN"],
        "update_frequency": "daily",
        "fetch_top_n": 100,
        "scrape_method": "unofficial",  # official API oder scraping
    },
    
    "youtube": {
        "enabled": True,
        "api_key": os.getenv("YOUTUBE_API_KEY", ""),
        "regions": ["US", "DE", "UK", "FR", "ES", "IT", "JP", "AU", "CA"],
        "update_frequency": "daily",
        "fetch_top_n": 50,
        "categories": ["all"],  # oder spezifische Categories
    },
    
    "twitter_x": {
        "enabled": True,
        "api_key": os.getenv("TWITTER_API_KEY", ""),
        "api_secret": os.getenv("TWITTER_API_SECRET", ""),
        "bearer_token": os.getenv("TWITTER_BEARER_TOKEN", ""),
        "update_frequency": "daily",
        "languages": ["en", "de", "fr", "es", "it"],
        "fetch_top_n": 100,
    },
    
    "reddit": {
        "enabled": True,
        "client_id": os.getenv("REDDIT_CLIENT_ID", ""),
        "client_secret": os.getenv("REDDIT_CLIENT_SECRET", ""),
        "user_agent": "TrendRadar/1.0",
        "subreddits": ["all", "todayilearned", "news", "AskReddit", "technology", "business"],
        "update_frequency": "daily",
        "fetch_top_n": 50,
    },
    
    "semrush": {
        "enabled": False,  # Premium Service
        "api_key": os.getenv("SEMRUSH_API_KEY", ""),
        "update_frequency": "weekly",
    },
}

# ============================================================================
# TREND-ANALYSE SETTINGS
# ============================================================================

TREND_ANALYSIS = {
    "min_search_volume": 1000,
    "min_growth_rate": 10,  # percent
    "min_cpc": 0.5,  # USD
    "max_competition": 0.8,  # 0-1 scale
    "trending_keywords_limit": 50,
    "hot_niches_limit": 20,
    "analysis_period_days": 7,
}

# ============================================================================
# NISCHEN-DISCOVERY SETTINGS
# ============================================================================

NICHE_DISCOVERY = {
    "min_monthly_searches": 5000,
    "max_competition_level": "medium",
    "min_cpc": 0.75,
    "target_long_tail_keywords": True,
    "min_keyword_length": 3,
    "max_keyword_length": 5,
}

# ============================================================================
# AFFILIATE-PROGRAM CRAWLER
# ============================================================================

AFFILIATE_CRAWLER = {
    "networks_to_crawl": [
        "amazon",
        "digistore24",
        "awin",
        "cj_affiliate",
        "shareasale",
        "clickbank",
        "impact",
        "rakuten",
        "tradedoubler",
    ],
    "min_commission_rate": 5,  # percent
    "fetch_new_programs_frequency": "weekly",
    "crawl_timeout": 30,
}

# ============================================================================
# COMPETITOR TRACKING
# ============================================================================

COMPETITOR_TRACKING = {
    "enabled": True,
    "track_affiliate_managers": True,
    "tracked_domains": [
        # Beliebte Affiliate-Marketing Sites
        "niche-sites.com",
        "seo-optimized-review.com",
        "best-tools-for-*.com",
        "comparison-*.com",
    ],
    "update_frequency": "daily",
    "analyze_content_strategy": True,
    "track_backlinks": True,
}

# ============================================================================
# DATABASE SETTINGS
# ============================================================================

TREND_DB_CONFIG = {
    "path": os.getenv("TREND_DB_PATH", "trend_radar/db/trends.db"),
    "backup_path": os.getenv("TREND_DB_BACKUP_PATH", "trend_radar/db/backups"),
}

# ============================================================================
# SCHEDULER
# ============================================================================

TREND_SCHEDULER = {
    "daily_scan_hour": int(os.getenv("TREND_SCAN_HOUR", "6")),
    "daily_scan_minute": int(os.getenv("TREND_SCAN_MINUTE", "0")),
    "timezone": os.getenv("TIMEZONE", "Europe/Berlin"),
}

# ============================================================================
# EXPORT SETTINGS
# ============================================================================

EXPORT_CONFIG = {
    "format": ["json", "csv", "db"],  # Export-Formate
    "export_location": "trend_radar/exports",
    "retention_days": 90,  # Alte Daten löschen nach X Tagen
}

print("[✓] Trend-Radar Config geladen")
