# 🚀 CashBot Content Factory - Quick Reference

## ⚡ Schnellstart in 5 Minuten

### 1️⃣ Setup
```bash
pip install openai gspread oauth2client
# LM Studio starten auf localhost:1234
# credentials.json im Hauptverzeichnis platzieren
```

### 2️⃣ Vollautomatische Pipeline
```bash
python module/Modul_MasterOrchestrator.py
```
✅ Fertig! Alle 3 Phasen laufen automatisch:
- 🔍 Research
- 🎬 Content Generation  
- 📤 Publishing

---

## 📚 Was jedes Modul macht

| Modul | Funktion | Output |
|-------|----------|--------|
| **ContentFactory** | Generiert alle Assets | JSON/Markdown Bundles |
| **ResearchToContent** | Trends → Content | Google Sheets + Dateien |
| **ContentPublisher** | Veröffentlicht Posts | Smart-Scheduled Posts |
| **MasterOrchestrator** | Koordiniert alles | Dashboard + Reports |

---

## 🎯 Content-Assets die generiert werden

### Pro Thema:
- ✅ 1 Video-Script (30-60s)
- ✅ 4 Bild-Prompts (1 pro Platform)
- ✅ 5 Caption-Varianten (pro Platform)
- ✅ Hashtag-Bündel (pro Platform)
- ✅ Komplettes Video-Konzept + Storyboard

### Insgesamt pro Thema:
- 📝 ~4 Scripts
- 🎨 ~16 Bild-Prompts
- 📱 ~20 Captions
- #️⃣ ~20 Hashtag-Sets
- 🎬 ~4 Video-Konzepte

---

## 💻 Code-Snippets zum Copy/Paste

### Scenario 1: Ein einzelnes Content-Bundle generieren
```python
from module.Modul_ContentFactory import ContentFactory

factory = ContentFactory()
bundle = factory.generate_content_bundle("Dein Thema hier")

# Export
factory.export_bundle(bundle, format="json")
factory.export_bundle(bundle, format="markdown")
```

### Scenario 2: Trends recherchiert → Content generiert → Veröffentlicht
```python
from module.Modul_ResearchToContent import ResearchToContentPipeline

pipeline = ResearchToContentPipeline()
pipeline.run_pipeline(batch_size=10)
```

### Scenario 3: A/B-Testing mit 3 Varianten
```python
from module.Modul_ResearchToContent import ABTestContentVariants

ab_tester = ABTestContentVariants()
variants = ab_tester.generate_ab_variants("Dein Thema", num_variants=3)
```

### Scenario 4: Sofort auf Instagram veröffentlichen
```python
from module.Modul_ContentPublisher import ContentPublisher

publisher = ContentPublisher()
publisher.publish_now(bundle, platform="instagram")
```

### Scenario 5: Smart-Scheduling für alle Platforms
```python
from module.Modul_ContentPublisher import AutoPublisher

auto_pub = AutoPublisher()
auto_pub.auto_publish_bundle(bundle, schedule=True)
```

---

## 📊 Plattform-Optionen

### Instagram
- Caption: bis zu 2.200 Zeichen
- Hashtags: ~20 (trending + niche mix)
- Emojis: 3-5 (optimiert)
- Format: Feed oder Stories
- Beste Zeiten: 9h, 11h, 14h, 18h, 21h

### TikTok
- Caption: max 150 Zeichen
- Hashtags: 8-10 (trending dominant)
- Emojis: 2-3 (minimal)
- Trending Sounds: Auto-Vorschläge
- Beste Zeiten: 6h, 12h, 18h, 21h

### YouTube Shorts
- Caption: bis 5.000 Zeichen
- Hashtags: 10-15 (Top 3 wichtig)
- Format: Vertical Video 9:16
- Video-Länge: max 60 Sekunden
- Beste Zeiten: 9h, 12h, 15h, 20h

### Pinterest
- Title: max 100 Zeichen
- Description: ~300 Zeichen
- Keywords: 5-8 (SEO-optimiert)
- Format: Tall Image 1000x1500
- Beste Zeiten: 8h, 14h (Pins viral über Zeit)

---

## 🔧 Konfiguration anpassen

**cashbot_config.json:**
```json
{
  "research_sheet": "CashBot_Trends",
  "content_sheet": "CashBot_Content",
  "platforms": ["instagram", "tiktok", "youtube_shorts", "pinterest"],
  "auto_publish": false,  // ← Set true für Auto-Veröffentlichung
  "batch_size": 50,  // ← Max. Themen pro Run
  "schedule_posts": true,  // ← Smart-Scheduling aktiviert
  "generate_variants": false,  // ← A/B-Testing (true = 3x pro Thema)
  "enable_monitoring": true  // ← Dashboard + Reports
}
```

---

## 📈 Was das System damit macht

**Eingabe:**
```
Trend: "KI-Tools für Content-Erstellung 2024"
```

**Output:**
```
✅ Script für 30s Video
✅ Midjourney Prompt
✅ DALL-E 3 Prompt  
✅ Stable Diffusion Prompt
✅ 5 verschiedene Captions
✅ 20 optimierte Hashtags
✅ Komplettes Storyboard
✅ Video-Concept mit Timing
✅ Color Palette (HEX-Codes)
✅ Audio-Empfehlungen
```

**Dann automatisch:**
```
📅 Smart-Scheduling für opt. Zeiten
📱 Posts auf Instagram, TikTok, YouTube, Pinterest
📊 Performance-Tracking
💡 Auto-Optimierungsvorschläge
```

---

## ⏱️ Zeitaufwand

| Task | Dauer |
|------|-------|
| 1 Content-Bundle | 15-30 Sekunden |
| 10 Bundles | 2-5 Minuten |
| 50 Bundles | 10-15 Minuten |
| Mit A/B-Testing (3x) | 3x so lange |
| Publishing + Scheduling | +1-2 Minuten |
| **Komplette Pipeline (50 Themen)** | **~30 Minuten** |

**Während das System läuft:** Kaffee trinken ☕ und sich entspannen 😎

---

## 🐛 Häufigste Fehler & Lösungen

| Fehler | Lösung |
|--------|--------|
| "LM Studio nicht erreichbar" | LM Studio starten, Modell laden |
| "Google Sheets Fehler" | credentials.json prüfen, Sheet-Namen anpassen |
| "Timeout bei Generierung" | Kleineres Batch_size in Config setzen |
| "Zu wenig Speicher" | Nur 5-10 Bundles gleichzeitig verarbeiten |
| "Schlechte Content-Qualität" | Größeres LM Studio Modell laden |

---

## 🎯 Performance-Tipps

✅ **Optimal:**
- Nutze Batch-Processing (10-50 Items)
- Smart-Scheduling aktiviert
- A/B-Testing für Top-Topics
- Monitoring + Optimierung aktiv

❌ **Zu Vermeiden:**
- Zu viele Items gleichzeitig (>100)
- Ohne Delay zwischen Requests
- Ohne Fehler-Handling
- Manuelle Veröffentlichung (vs. Auto)

---

## 📞 Debug & Logs

**Log-Dateien:**
```
orchestration_logs/
├── pipeline_20240627.log  (Komplette Protokolle)
├── status.json  (Aktuelle Status)
└── report_20240627_194458.json  (Detailliert Report)
```

**Dashboard:**
```
Öffne: dashboard.html
Zeigt: Engagement, Reach, Viral Score, Empfehlungen
```

---

## 🚀 Nächste Schritte

1. **Jetzt starten:**
   ```bash
   python module/Modul_MasterOrchestrator.py
   ```

2. **Monitoring:**
   - Öffne `dashboard.html`
   - Check `orchestration_logs/`

3. **Optimieren:**
   - Bestseller identifizieren
   - Mehr A/B-Testing für Top-Topics
   - Captions + Hashtags fine-tunen

4. **Skalieren:**
   - Batch-Size erhöhen
   - Mehrere Research-Sources
   - Additional Platforms

---

**Made with ❤️ for Complete Content Automation**

*V1.0 | Juni 2024*
