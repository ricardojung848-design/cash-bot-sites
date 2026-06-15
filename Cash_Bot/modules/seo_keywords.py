import re
from datetime import datetime

# Dynamische Keyword-Engine
# Aggressiv + Trend-Boost + SERP-Varianten

def normalize(text):
    return re.sub(r"[^a-zA-Z0-9äöüÄÖÜß ]", "", text).strip()

def is_trend_topic(thema):
    thema_low = thema.lower()
    trend_keywords = ["2026", "trend", "neu", "ai", "ki", "automation", "tiktok", "instagram", "viral"]
    return any(tk in thema_low for tk in trend_keywords)

def generate_longtails(base):
    return [
        f"{base} erklärung",
        f"{base} beispiele",
        f"{base} workflow",
        f"{base} fehler vermeiden",
        f"{base} best practices",
        f"{base} tools",
        f"{base} für anfänger",
        f"{base} für profis",
        f"{base} anleitung",
        f"{base} tipps",
    ]

def generate_serp_variants(base):
    return [
        f"was ist {base}",
        f"wie funktioniert {base}",
        f"{base} vorteile",
        f"{base} nachteile",
        f"{base} kosten",
        f"{base} nutzen",
        f"{base} guide",
        f"{base} tutorial",
    ]

def dynamic_cluster_size(thema):
    thema_low = thema.lower()

    if len(thema_low) < 10:
        return 8  # enges Thema
    if len(thema_low) < 20:
        return 15  # mittel
    return 25  # breites Thema

def generate_keyword_cluster(thema):
    thema = normalize(thema)
    base = thema.lower()

    cluster = []

    # Basis-Keyword
    cluster.append(base)

    # Longtails
    cluster.extend(generate_longtails(base))

    # SERP-Varianten
    cluster.extend(generate_serp_variants(base))

    # Dynamische Größe
    size = dynamic_cluster_size(thema)

    # Trend-Boost
    if is_trend_topic(thema):
        size = int(size * 1.5)

    # Begrenzen auf aggressiven Modus (max 40)
    size = min(size, 40)

    # Finales Cluster kürzen
    cluster = cluster[:size]

    return {
        "thema": thema,
        "count": len(cluster),
        "keywords": cluster,
        "trend_boost": is_trend_topic(thema),
        "timestamp": datetime.now().isoformat()
    }
