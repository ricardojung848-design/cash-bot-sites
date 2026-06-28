"""
Konfiguration für Affiliate & SEO Engine
Alle API-Keys und Einstellungen hier definieren
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# API CREDENTIALS (Placeholder - wird später mit Keys gefüllt)
# ============================================================================

AFFILIATE_APIS = {
    "amazon": {
        "enabled": True,
        "api_key": os.getenv("AMAZON_API_KEY", "YOUR_AMAZON_API_KEY_HERE"),
        "api_secret": os.getenv("AMAZON_API_SECRET", "YOUR_AMAZON_API_SECRET_HERE"),
        "partner_tag": os.getenv("AMAZON_PARTNER_TAG", "YOUR_AMAZON_TAG_HERE"),
        "region": "DE",
    },
    "digistore24": {
        "enabled": True,
        "api_token": os.getenv("DIGISTORE24_TOKEN", "YOUR_DIGISTORE24_TOKEN_HERE"),
        "partner_id": os.getenv("DIGISTORE24_PARTNER_ID", "YOUR_PARTNER_ID_HERE"),
    },
    "awin": {
        "enabled": True,
        "api_key": os.getenv("AWIN_API_KEY", "YOUR_AWIN_API_KEY_HERE"),
        "publisher_id": os.getenv("AWIN_PUBLISHER_ID", "YOUR_PUBLISHER_ID_HERE"),
    },
    "cj_affiliate": {
        "enabled": True,
        "api_token": os.getenv("CJ_API_TOKEN", "YOUR_CJ_API_TOKEN_HERE"),
    },
    "shareasale": {
        "enabled": True,
        "api_key": os.getenv("SHAREASALE_API_KEY", "YOUR_SHAREASALE_KEY_HERE"),
    },
    "clickbank": {
        "enabled": True,
        "api_key": os.getenv("CLICKBANK_API_KEY", "YOUR_CLICKBANK_KEY_HERE"),
    },
}

# ============================================================================
# CONTENT GENERATION
# ============================================================================

CONTENT_CONFIG = {
    "lm_studio_url": os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1"),
    "lm_studio_model": os.getenv("LM_STUDIO_MODEL", "local-model"),
    "lm_studio_timeout": 300.0,
    "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
    "use_openai": os.getenv("USE_OPENAI", "false").lower() == "true",
}

# ============================================================================
# DATABASE
# ============================================================================

DB_CONFIG = {
    "path": os.getenv("DB_PATH", "affiliate_engine/db/affiliate_engine.db"),
    "backup_path": os.getenv("DB_BACKUP_PATH", "affiliate_engine/db/backups"),
}

# ============================================================================
# SCHEDULER
# ============================================================================

SCHEDULER_CONFIG = {
    "daily_generation_hour": int(os.getenv("DAILY_GENERATION_HOUR", "2")),
    "daily_generation_minute": int(os.getenv("DAILY_GENERATION_MINUTE", "0")),
    "timezone": os.getenv("TIMEZONE", "Europe/Berlin"),
}

# ============================================================================
# WEB UI
# ============================================================================

WEB_CONFIG = {
    "host": os.getenv("WEB_HOST", "0.0.0.0"),
    "port": int(os.getenv("WEB_PORT", "5000")),
    "debug": os.getenv("DEBUG", "true").lower() == "true",
    "secret_key": os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"),
}

# ============================================================================
# LANDING PAGE DEFAULTS
# ============================================================================

LP_CONFIG = {
    "default_theme": "modern-dark",
    "include_testimonials": True,
    "include_faq": True,
    "include_comparison_table": True,
    "cta_text": "Jetzt starten",
    "enable_countdown": False,
}

# ============================================================================
# SEO SETTINGS
# ============================================================================

SEO_CONFIG = {
    "target_keywords": 5,
    "include_lsi_keywords": True,
    "min_word_count": 800,
    "max_word_count": 2000,
    "include_schema_markup": True,
}

# ============================================================================
# TRACKING
# ============================================================================

TRACKING_CONFIG = {
    "enable_utm_params": True,
    "utm_source": "affiliate_engine",
    "utm_medium": "cpc",
    "utm_campaign": "{campaign_name}",
    "enable_link_shortening": False,
}

print("[✓] Config geladen - API Placeholders aktiv")
