# 🤖 CashBot Content Automation Engine

**Vollautomatisierte Content-Generierung & Distribution für Instagram, TikTok, YouTube Shorts & Pinterest**

---

## 📋 Überblick

Dieses System automatisiert die komplette Content-Pipeline:

```
Research Engine (Trends) 
    ↓
Content Factory (Generierung)
    ↓
Publisher (Distribution)
    ↓
Dashboard (Monitoring)
```

---

## 🎯 Module

### 1. **Modul_ContentFactory.py** - Kern-Generierung
Generiert alle Content-Assets vollautomatisch:

#### ✅ Was die Content Factory tut:
- **📹 Skripte**: 30/60-Sekunden Video-Skripte mit Hook, Body, CTA
- **🎨 Bild-Prompts**: 
  - Midjourney Prompts (kreativ, detailliert)
  - DALL-E 3 Prompts (strukturiert)
  - Stable Diffusion Prompts (technisch)
  - Color Palettes (HEX-Codes)
  
- **📝 Captions**: 
  - High-Engagement Varianten
  - Viral-Hook Versionen
  - Sales-Focused CTAs
  - Community-Building Texte
  - Platform-optimiert (Instagram, TikTok, Pinterest, YouTube)

- **#️⃣ Hashtag-Bündel**:
  - Trending Hashtags (hohe Reichweite)
  - Niche Hashtags (hohes Engagement)
  - Long-Tail Keywords (geringer Wettbewerb)
  - Branded Hashtags (Community)
  - Platform-spezifisch (Instagram 20x, TikTok 10x, etc.)

- **🎬 Video-Konzepte**: 
  - Komplette Storyboards (Frame-by-Frame)
  - Schnitt-Anweisungen (Übergänge, Effekte)
  - Audio-Design (Musik, Voice-Over, SFX)
  - Text/Graphics Overlay Timing

#### 💻 Beispiel-Verwendung:

```python
from module.Modul_ContentFactory import ContentFactory

factory = ContentFactory()

# Einzelne Assets generieren
script = factory.generate_script(
    topic="Die Top 5 KI-Tools 2024",
    duration_seconds=30,
    style="motivational"
)

image_prompts = factory.generate_image_prompt(
    topic="KI-Tools",
    style="modern",
    platform="instagram"
)

captions = factory.generate_caption(
    topic="KI-Tools",
    platform="instagram",
    engagement_goal="reach"
)

hashtags = factory.generate_hashtag_bundle(
    topic="KI-Tools",
    niche="technology",
    platforms=["instagram", "tiktok", "youtube_shorts", "pinterest"]
)

video_concept = factory.generate_video_concept(
    topic="KI-Tools",
    platform="tiktok",
    duration=30
)

# KOMPLETTES BUNDLE generieren
bundle = factory.generate_content_bundle(
    topic="KI-Tools 2024",
    platforms=["instagram", "tiktok", "youtube_shorts", "pinterest"]
)

# In verschiedene Formate exportieren
factory.export_bundle(bundle, format="json")
factory.export_bundle(bundle, format="markdown")

# In Google Sheets speichern
factory.save_bundle_to_sheet(bundle, spreadsheet_name="CashBot_Content")
```

---

### 2. **Modul_ResearchToContent.py** - Integration mit Research Engine
Verbindet die Trend-Recherche mit der Content-Generierung:

#### 🔗 Was das Modul tut:
- Liest recherchierte Trends aus Google Sheets
- Generiert automatisch Content-Assets für jedes Thema
- Speichert Ergebnisse im Output-Sheet
- Batch-Processing von Hunderten Themes
- A/B-Testing mit mehreren Varianten

#### 💻 Beispiel-Verwendung:

```python
from module.Modul_ResearchToContent import ResearchToContentPipeline, ABTestContentVariants

# Research-to-Content Pipeline
pipeline = ResearchToContentPipeline(
    research_sheet="CashBot_Trends",
    output_sheet="CashBot_Content"
)

# Starte die komplette Pipeline
pipeline.run_pipeline(
    batch_size=50,  # Verarbeite max 50 Themen
    delay_between_items=2  # 2 Sekunden Verzögerung zwischen Items
)

# A/B-Testing
ab_tester = ABTestContentVariants()
variants = ab_tester.generate_ab_variants(
    topic="KI-Tools 2024",
    num_variants=3
)
```

---

### 3. **Modul_ContentPublisher.py** - Automatische Distribution
Veröffentlicht Content auf allen Plattformen mit Smart-Scheduling:

#### 📲 Unterstützte Plattformen:
- ✅ Instagram (Feed + Stories)
- ✅ TikTok (Videos)
- ✅ YouTube Shorts (Verticalvideos)
- ✅ Pinterest (Pins)

#### ⏱️ Smart-Scheduling:
- **Automatische Timing-Optimierung** basierend auf:
  - Platform-spezifische beste Posting-Zeiten
  - Wochentag vs. Wochenende
  - Timezone des Audiences
  - Engagement-Patterns

#### 💻 Beispiel-Verwendung:

```python
from module.Modul_ContentPublisher import ContentPublisher, SmartScheduler, AutoPublisher

# Manuelles Publishing
publisher = ContentPublisher()

# Sofort veröffentlichen
publisher.publish_now(
    bundle=content_bundle,
    platform="instagram",
    caption="Custom Caption...",
    hashtags={"complete_set": "#custom #hashtags"}
)

# Für später planen
from datetime import datetime, timedelta
tomorrow = datetime.now() + timedelta(days=1)
publisher.schedule_post(
    bundle=content_bundle,
    platform="tiktok",
    publish_time=tomorrow
)

# Smart-Scheduling - Auto-Optimale Zeiten
schedule = SmartScheduler.create_posting_schedule(
    bundle=content_bundle,
    platforms=["instagram", "tiktok", "youtube_shorts", "pinterest"]
)

# Auto-Publishing auf allen Plattformen
auto_pub = AutoPublisher()
auto_pub.auto_publish_bundle(
    bundle=content_bundle,
    platforms=["instagram", "tiktok", "youtube_shorts", "pinterest"],
    schedule=True,  # Mit Smart-Scheduling
    delay_between_posts=300  # 5 Minuten zwischen Posts
)
```

---

### 4. **Modul_MasterOrchestrator.py** - Zentrale Steuerung
Koordiniert alle Module und orches die komplette Pipeline:

#### 🎛️ Funktionen:
- **3-Phasen Pipeline**:
  1. 🔍 Research Phase - Trends recherchieren
  2. 🎬 Content Generation Phase - Assets generieren
  3. 📤 Publishing Phase - Veröffentlichen

- **Monitoring & Optimization**:
  - Kontinuierliche Performance-Überwachung
  - Automatische Optimierungsvorschläge
  - HTML-Dashboard für Visualisierung

- **Error Handling & Recovery**:
  - Fehlerbehandlung mit Retry-Logik
  - Detailliertes Logging
  - Final Reports mit Statistiken

#### 💻 Beispiel-Verwendung:

```python
from module.Modul_MasterOrchestrator import MasterOrchestrator, DashboardGenerator

# Orchestrator initialisieren
orchestrator = MasterOrchestrator(config_file="cashbot_config.json")

# Komplette Pipeline ausführen
success = orchestrator.run_full_pipeline()

# Monitoring & Optimization
metrics = orchestrator.monitor_and_optimize()

# Dashboard generieren
DashboardGenerator.generate_html_dashboard(metrics)
```

---

## 📊 Konfiguration (cashbot_config.json)

```json
{
  "research_sheet": "CashBot_Trends",
  "content_sheet": "CashBot_Content",
  "platforms": ["instagram", "tiktok", "youtube_shorts", "pinterest"],
  "auto_publish": false,
  "batch_size": null,
  "delay_between_items": 2,
  "delay_between_posts": 300,
  "schedule_posts": true,
  "generate_variants": false,
  "variant_count": 3,
  "enable_monitoring": true
}
```

---

## 🚀 Quick Start

### Setup:

```bash
# 1. Abhängigkeiten installieren
pip install openai gspread oauth2client

# 2. LM Studio Server starten (lokal)
# Port: 1234
# Modell: Ein beliebiges lokales Modell laden

# 3. Google Sheets Credentials
# credentials.json im Hauptverzeichnis platzieren

# 4. Konfiguration anpassen
# cashbot_config.json bearbeiten (wird auto-erstellt)
```

### Ausführung:

```bash
# Option 1: Komplette Pipeline (Research → Content → Publishing)
python module/Modul_MasterOrchestrator.py

# Option 2: Nur Content Factory
python module/Modul_ContentFactory.py

# Option 3: Research zu Content
python module/Modul_ResearchToContent.py

# Option 4: Publishing & Distribution
python module/Modul_ContentPublisher.py
```

---

## 📁 Output-Struktur

```
generated_content/
├── bundle_ki-tools-2024_20240627_194458.json
├── bundle_ki-tools-2024_20240627_194458.md
├── content_variants/
│   └── ab_test_ki-tools-2024.json
└── orchestration_logs/
    ├── pipeline_20240627.log
    ├── status.json
    └── report_20240627_194458.json

dashboard.html  # Analytics Dashboard
published_content.json  # Publikations-Log
```

---

## 🎨 Content-Output Beispiel

### Script:
```json
{
  "hook": "Hast du schon diese 5 KI-Tools genutzt? 🚀",
  "body": [
    {
      "second": 3,
      "text": "ChatGPT revolutioniert Content-Erstellung...",
      "action": "Schnitt zu ChatGPT Demo"
    }
  ],
  "cta": "Follow für mehr KI-Tools!",
  "total_seconds": 30,
  "b_roll_suggestions": ["AI Screen Recording", "Code Editor Footage"]
}
```

### Bild-Prompts:
```json
{
  "midjourney": "Modern AI interface, neon colors, 8K, cinematic, trending on artstation",
  "dalle3": "Minimalist AI tools dashboard with bright neon accents",
  "stable_diffusion": "cyberpunk AI interface, high quality, trending, 4K",
  "color_palette": ["#FF6B6B", "#4ECDC4", "#FFE66D", "#95E1D3", "#000000"]
}
```

### Captions:
```json
{
  "high_engagement": "Diese 5 KI-Tools haben mein Business verändert 🤖\n\nWelches nutzt ihr schon?",
  "viral_hook": "❌ Ohne KI im 2024\n✅ Mit diesen 5 Tools\n\nDer Unterschied ist KRASS 👇",
  "sales_focused": "Automatisiere deinen Content in Minuten →",
  "community_building": "Teilt eure liebsten KI-Tools in den Comments! 💬"
}
```

### Hashtags:
```json
{
  "instagram": {
    "trending": ["#AI", "#AITools", "#ArtificialIntelligence", "#Tech", "#Automation"],
    "niche": ["#AIContent", "#AIMarketing", "#DigitalTools", "#ProductivityHacks"],
    "long_tail": ["#2024AITrends", "#ContentAutomation"],
    "complete_set": "#AI #AITools #ArtificialIntelligence #Tech #Automation #AIContent..."
  },
  "tiktok": {
    "trending": ["#AI", "#FYP", "#ForYou", "#Tech"],
    "complete_set": "#AI #FYP #ForYou #Tech #AITools"
  }
}
```

---

## 🔄 Workflow-Beispiel

### Szenario: Automatische Content-Pipeline für 50 Trend-Themen

```python
# 1. Start Master Orchestrator
orchestrator = MasterOrchestrator()

# 2. Research Phase (recherchierte Trends aus Google Sheets laden)
orchestrator.run_research_phase()
# → Findet 50 aktuelle Trends

# 3. Content Factory Phase
# → Generiert für jedes Thema:
#   - Script
#   - Bild-Prompts (3x: Midjourney, DALL-E, Stable Diffusion)
#   - Captions (5x Varianten pro Platform)
#   - Hashtag-Bündel (pro Platform)
#   - Video-Konzept + Storyboard

# 4. A/B-Testing (optional)
# → Generiert 3 Varianten pro Thema für Testing

# 5. Publishing Phase
# → Smart-Scheduling für optimal Posting-Zeiten
# → Verteilt auf Instagram, TikTok, YouTube Shorts, Pinterest
# → Automatische Post-Planung basierend auf Engagement-Patterns

# 6. Monitoring
# → Trackt Engagement, Reach, Viral-Score
# → Generiert automatische Optimierungsempfehlungen
# → Erstellt HTML-Dashboard

# 7. Gesamtzeit: ~30-45 Minuten für 50 Themen
#    (Abhängig von LM Studio Model Speed)
```

---

## 📈 Performance & Metriken

Das System trackt automatisch:

| Metrik | Beschreibung |
|--------|-------------|
| **Engagement Rate** | Likes, Comments, Shares kombiniert |
| **Reach** | Wie viele Menschen sehen den Post |
| **Viral Score** | 1-10 Rating für Viral-Potential |
| **Best Platform** | Welche Platform beste Performance hat |
| **Processing Time** | Wie lange die Pipeline dauert |
| **Error Rate** | Wie viele Fehler aufgetreten sind |

---

## 🛠️ Customization

### Eigene Styles hinzufügen:

```python
# Neue Caption-Variante
def generate_custom_caption(topic):
    prompt = f"Schreibe eine Caption im [CUSTOM_STYLE] über {topic}"
    # Implementierung...
```

### Platform erweitern:

```python
# Neue Platform hinzufügen (z.B. LinkedIn)
class LinkedInPublisher:
    def publish(self, post_content):
        # LinkedIn-spezifische Logik
        pass

# In ContentPublisher registrieren:
self.platforms["linkedin"] = LinkedInPublisher()
```

### Eigene Prompts:

```python
# Anpasse die LLM-Prompts in den Generierungs-Funktionen
# Sie sind vollständig customizable für deine Use-Cases
```

---

## 🚨 Troubleshooting

### Problem: "LM Studio Server nicht erreichbar"
```
Lösung:
1. LM Studio auf localhost:1234 starten
2. Ein Modell laden (z.B. Mistral, Llama)
3. API aktivieren
```

### Problem: "Google Sheets Verbindung fehlgeschlagen"
```
Lösung:
1. credentials.json im Hauptverzeichnis platzieren
2. Service Account mit Sheet-Zugriff erstellen
3. Spreadsheet-Namen in Config.json anpassen
```

### Problem: "Content Quality nicht optimal"
```
Lösung:
1. Besseres LM Studio Modell laden (größer = besser)
2. Prompts in den Funktionen verbessern
3. A/B-Testing nutzen um beste Varianten zu finden
```

---

## 📞 Support & Weitere Entwicklung

Geplante Features:
- ✅ Instagram Stories Auto-Generation
- ✅ LinkedIn Post Generierung
- ✅ Email-Newsletter Automation
- ✅ Automatisches Image-Generation (Midjourney/DALL-E Integration)
- ✅ Video-Rendering (FFmpeg Integration)
- ✅ Advanced Analytics Dashboard
- ✅ Multi-Account Management

---

## 📄 Lizenz

Privat - Nur für CashBot Automation

---

**Erstellt mit ❤️ für vollautomatisierte Content-Generierung**

V1.0 | 2024-06-27
