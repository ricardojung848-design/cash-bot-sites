# ============================================================
#  LOGIK.PY – VERSION C (Auto‑Reels, OpenAI TTS, Video Engine)
# ============================================================

from __future__ import annotations

import os
from datetime import datetime, time as dtime
from typing import Any, Dict, List, Optional, Tuple

# === interne Utils ===
from core.utils import (
    BASE_DIR,
    DATA_DIR,
    OUTPUT_DIR,
    SOCIAL_DIR,
    CONFIG_DIR,
    load_json,
    save_json,
    log_worker,
    warn_worker,
    error_worker,
)

# === Module ===
from modules.fabrik_engine import FABRIK
from modules.seo_keywords import generate_keyword_cluster
from modules.analytics_engine import log_event
from modules.optimizer_engine import build_evergreen_ranking, build_weekly_ranking
from modules.hook_generator import generate_hook

# Auto‑Reel Module
from modules.voice_engine import VoiceEngine
from modules.video_engine import VideoEngine
from modules.instagram_api import InstagramPoster

# ---------------------------------------------------------------------------
# Konfiguration laden
# ---------------------------------------------------------------------------

CONFIG_FILE = os.path.join(CONFIG_DIR, "cashbot_config.json")

DEFAULT_CONFIG = {
    "nische": "Business Automation",
    "produkt_typ": "Automations-Dienstleistungen & KI-Beratung",

    "social_media": {
        "instagram_reels": True,
        "auto_store_posts": True,
        "auto_post": False,
    },

    "instagram_api": {
        "access_token": "",
        "ig_user_id": "",
    },

    "tts": {
        "api_key": "",
    }
}

CONFIG = load_json(CONFIG_FILE, DEFAULT_CONFIG)

NISCHE = CONFIG["nische"]
PRODUKT_TYP = CONFIG["produkt_typ"]
SOCIAL_CFG = CONFIG["social_media"]

INSTAGRAM_TOKEN = CONFIG["instagram_api"]["access_token"]
INSTAGRAM_USER_ID = CONFIG["instagram_api"]["ig_user_id"]

TTS_API_KEY = CONFIG["tts"]["api_key"]

ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# ---------------------------------------------------------------------------
# Posting-Queue
# ---------------------------------------------------------------------------

POSTING_QUEUE_FILE = os.path.join(SOCIAL_DIR, "posting_queue.json")
# ---------------------------------------------------------------------------
# Posting-Queue
# ---------------------------------------------------------------------------

class PostingQueue:
    def __init__(self, path: str) -> None:
        self.path = path
        self._ensure_file()

    def _ensure_file(self) -> None:
        queue = load_json(self.path, [])
        if not isinstance(queue, list):
            warn_worker("Posting-Queue beschädigt – neu initialisiert.")
            queue = []
            save_json(self.path, queue)

    def _load(self) -> List[Dict[str, Any]]:
        queue = load_json(self.path, [])
        if not isinstance(queue, list):
            warn_worker("Posting-Queue beschädigt – neu initialisiert.")
            queue = []
            save_json(self.path, queue)
        return queue

    def _save(self, queue: List[Dict[str, Any]]) -> None:
        save_json(self.path, queue)

    def _next_id(self, queue: List[Dict[str, Any]]) -> int:
        if not queue:
            return 1
        return max(item.get("id", 0) for item in queue) + 1

    def add_entry(self, script: Dict[str, Any], json_path: str, txt_path: str, auto_post: bool = False) -> Dict[str, Any]:
        queue = self._load()
        entry = {
            "id": self._next_id(queue),
            "thema": script["thema"],
            "nische": script["nische"],
            "produkt_typ": script["produkt_typ"],
            "json_path": json_path,
            "txt_path": txt_path,
            "status": "pending",
            "scheduled_at": None,
            "platforms": ["instagram"],
            "auto_post": auto_post,
            "created_at": datetime.now().isoformat(),
            "posted_at": None,
            "cancelled_at": None,
        }
        queue.append(entry)
        self._save(queue)
        return entry

    def list_entries(self) -> List[Dict[str, Any]]:
        return self._load()

    def save_entries(self, queue: List[Dict[str, Any]]) -> None:
        self._save(queue)

    def clear(self) -> None:
        self._save([])

    def cancel_by_id(self, post_id: int) -> str:
        queue = self._load()
        for item in queue:
            if item.get("id") == post_id and item["status"] in ("pending", "scheduled"):
                item["status"] = "cancelled"
                item["cancelled_at"] = datetime.now().isoformat()
                self._save(queue)
                return f"🛑 Posting mit ID {post_id} abgebrochen."
        return f"❌ Kein aktiver Eintrag mit ID {post_id}."

    def overview_text(self) -> str:
        queue = self._load()
        if not queue:
            return "📭 Posting-Queue ist leer."

        lines = ["📋 Posting-Queue:"]
        for item in queue:
            sched = item.get("scheduled_at")
            sched_str = f"📅 {sched}" if sched else ""
            lines.append(f"- ID {item['id']}: {item['thema']} [{item['status']}] {sched_str}")
        return "\n".join(lines)

    def status_text(self) -> str:
        queue = self._load()
        if not queue:
            return "📭 Keine Einträge."

        total = len(queue)
        pending = sum(1 for x in queue if x["status"] == "pending")
        scheduled = sum(1 for x in queue if x["status"] == "scheduled")
        posted = sum(1 for x in queue if x["status"] == "posted")
        cancelled = sum(1 for x in queue if x["status"] == "cancelled")

        return (
            "📊 Posting-Status:\n"
            f"• Gesamt: {total}\n"
            f"• Pending: {pending}\n"
            f"• Scheduled: {scheduled}\n"
            f"• Posted: {posted}\n"
            f"• Cancelled: {cancelled}"
        )


# ---------------------------------------------------------------------------
# Posting-Engine
# ---------------------------------------------------------------------------

class PostingEngine:
    def __init__(self, queue: PostingQueue) -> None:
        self.queue = queue

    def _perform_post(self, entry: Dict[str, Any]) -> str:
        log_worker(f"Simuliere Posting für: {entry['thema']}")
        msg = f"💥 Simuliertes Posting veröffentlicht: {entry['thema']}"
        log_worker(msg)
        return msg

    def _mark_posted(self, entry: Dict[str, Any]) -> None:
        entry["status"] = "posted"
        entry["posted_at"] = datetime.now().isoformat()

    def auto_posting_tick(self) -> None:
        queue = self.queue.list_entries()
        changed = False
        now = datetime.now()

        for entry in queue:
            if entry["status"] not in ("pending", "scheduled"):
                continue

            if entry.get("auto_post"):
                self._perform_post(entry)
                self._mark_posted(entry)
                changed = True
                continue

            sched = entry.get("scheduled_at")
            if sched:
                try:
                    sched_dt = datetime.fromisoformat(sched)
                    if now >= sched_dt:
                        self._perform_post(entry)
                        self._mark_posted(entry)
                        changed = True
                except:
                    warn_worker("Fehler beim Lesen von scheduled_at")

        if changed:
            self.queue.save_entries(queue)

    def handle_post_command(self, text: str) -> str:
        t = text.lower().strip()

        if t.startswith("post now"):
            parts = text.split(" ", 2)
            if len(parts) < 3:
                return "❌ Nutze: post now <Thema>"
            thema = parts[2].strip()
            queue = self.queue.list_entries()
            for entry in queue:
                if entry["thema"].lower() == thema.lower() and entry["status"] in ("pending", "scheduled"):
                    entry["auto_post"] = True
                    self.queue.save_entries(queue)
                    return f"🚀 Posting für '{thema}' wird sofort ausgeführt."
            return f"❌ Kein Eintrag für '{thema}'."

        if t.startswith("post schedule"):
            parts = text.split(" ", 4)
            if len(parts) < 5:
                return "❌ Nutze: post schedule <YYYY-MM-DD> <HH:MM> <Thema>"
            date_str, time_str, thema = parts[2], parts[3], parts[4]
            try:
                sched = datetime.fromisoformat(f"{date_str} {time_str}")
            except:
                return "❌ Ungültiges Datum."
            queue = self.queue.list_entries()
            for entry in queue:
                if entry["thema"].lower() == thema.lower():
                    entry["scheduled_at"] = sched.isoformat()
                    entry["status"] = "scheduled"
                    self.queue.save_entries(queue)
                    return f"📅 Posting geplant: {sched}"
            return f"❌ Kein Eintrag für '{thema}'."

        if t.startswith("post cancel"):
            parts = text.split(" ", 2)
            if len(parts) < 3:
                return "❌ Nutze: post cancel <ID>"
            try:
                pid = int(parts[2])
            except:
                return "❌ ID muss Zahl sein."
            return self.queue.cancel_by_id(pid)

        if t.startswith("post clear"):
            self.queue.clear()
            return "🧹 Queue geleert."

        if t.startswith("post status"):
            return self.queue.status_text()

        if t.startswith("post list"):
            return self.queue.overview_text()

        return "❌ Unbekannter Post-Befehl."
# ---------------------------------------------------------------------------
# Reel-Engine (Auto‑Reels, Voiceover, Video, Upload)
# ---------------------------------------------------------------------------

class ReelEngine:
    def __init__(
        self,
        queue: PostingQueue,
        access_token: str,
        ig_user_id: str,
        tts_api_key: str,
        assets_dir: str,
    ) -> None:
        self.queue = queue
        self.poster = InstagramPoster(access_token, ig_user_id)
        self.voice_engine = VoiceEngine(tts_api_key)
        self.video_engine = VideoEngine(assets_dir)

    # ---------------------------------------------------------
    # Standard Reel-Skript (Hook + Content + CTA)
    # ---------------------------------------------------------
    def generate_reel_script(self, thema: str) -> Dict[str, Any]:
        thema_clean = thema.strip()

        return {
            "thema": thema_clean,
            "nische": NISCHE,
            "produkt_typ": PRODUKT_TYP,

            # PHASE 11 HOOK ENGINE
            "hook": generate_hook(thema_clean),

            "content": [
                f"{thema_clean} ist einer der schnellsten Wege, um Prozesse zu automatisieren.",
                "Viele machen Fehler, weil sie ohne System starten.",
                f"Mit einem klaren Workflow kannst du {thema_clean} in wenigen Tagen umsetzen.",
            ],

            "cta": (
                f"Wenn du {PRODUKT_TYP} ernsthaft skalieren willst, "
                f"fang mit einem kleinen Workflow rund um {thema_clean} an."
            ),

            "hashtags": [
                "#automation",
                "#businessautomation",
                "#kiberatung",
                "#onlineskalierung",
                "#prozesse",
                "#cashbot",
            ],

            "timestamp": datetime.now().isoformat(),
        }

    # ---------------------------------------------------------
    # Speichern als JSON + TXT
    # ---------------------------------------------------------
    def save_reel_script(self, script: Dict[str, Any]) -> Tuple[str, str]:
        thema = script["thema"].replace(" ", "_").lower()
        json_path = os.path.join(SOCIAL_DIR, f"{thema}.json")
        txt_path = os.path.join(SOCIAL_DIR, f"{thema}.txt")

        save_json(json_path, script)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"Reel für Thema: {script['thema']}\n")
            f.write(f"Hook: {script['hook']}\n\n")
            f.write("Content:\n")
            for line in script["content"]:
                f.write(f"- {line}\n")
            f.write(f"\nCTA: {script['cta']}\n")
            f.write("\nHashtags:\n")
            f.write(" ".join(script["hashtags"]))

        return json_path, txt_path

    # ---------------------------------------------------------
    # Standard Reel Command
    # ---------------------------------------------------------
    def handle_reel_command(self, text: str) -> str:
        parts = text.split(" ", 1)
        if len(parts) < 2:
            return "❌ Bitte nutze: reel <Thema>"

        thema = parts[1].strip()
        script = self.generate_reel_script(thema)
        json_path, txt_path = self.save_reel_script(script)

        if SOCIAL_CFG.get("auto_store_posts", True):
            self.queue.add_entry(script, json_path, txt_path)

        return (
            f"🎬 Reel-Skript erstellt für: {thema}\n"
            f"📁 Gespeichert unter:\n"
            f"- {json_path}\n"
            f"- {txt_path}"
        )

    # ---------------------------------------------------------
    # AUTO‑REEL (Hook + Content + Voice + Video + Upload)
    # ---------------------------------------------------------
    def handle_auto_reel(self, text: str) -> str:
        parts = text.split(" ", 2)
        if len(parts) < 3:
            return "❌ Nutze: reel auto <Thema>"

        thema = parts[2].strip()

        # 1. Skript erzeugen
        script = self.generate_reel_script(thema)

        # 2. Voiceover erzeugen
        voice_path = os.path.join(SOCIAL_DIR, f"{thema}_voice.mp3")
        voice_path = self.voice_engine.generate_voiceover(
            script["hook"] + "\n" + "\n".join(script["content"]) + "\n" + script["cta"],
            voice_path
        )
        if not voice_path:
            return "❌ Voiceover konnte nicht erzeugt werden."

        # 3. Video erzeugen
        video_path = os.path.join(SOCIAL_DIR, f"{thema}_auto.mp4")
        video_path = self.video_engine.create_reel(script, voice_path, video_path)
        if not video_path:
            return "❌ Video konnte nicht erzeugt werden."

        # 4. Reel posten
        caption = script["hook"] + "\n\n" + script["cta"]
        self.poster.post_reel(video_path, caption)

        return f"🚀 Auto-Reel erstellt & gepostet für: {thema}"
# ---------------------------------------------------------------------------
# Fabrik-Engine 2.0 (C1 + C2 + Multi-Output)
# ---------------------------------------------------------------------------

class FabrikEngine:
    def _slugify(self, thema: str) -> str:
        return thema.strip().replace(" ", "_").lower()

    # -------------------------
    # C1 – Social Content
    # -------------------------
    def _build_social_content(self, thema: str) -> Dict[str, Any]:
        return {
            "title": f"{thema} – Quick Overview",
            "meta_description": f"Schneller Überblick zu {thema} für Social Media & Reels.",
            "sections": [
                {
                    "heading": "Warum dieses Thema wichtig ist",
                    "bullets": [
                        f"{thema} spart dir Zeit und Nerven.",
                        "Du kannst Prozesse automatisieren statt alles manuell zu machen.",
                        "Perfekt, um mit kleinen Automationen zu starten.",
                    ],
                },
                {
                    "heading": "3 schnelle Umsetzungsideen",
                    "bullets": [
                        "Starte mit einem Mini-Workflow.",
                        "Automatisiere eine wiederkehrende Aufgabe.",
                        "Nutze KI, um Routinearbeit zu reduzieren.",
                    ],
                },
                {
                    "heading": "Call to Action",
                    "bullets": [
                        "Speichere dir diese Seite.",
                        "Teste heute eine kleine Automation.",
                        "Teile das Thema mit jemandem, der es braucht.",
                    ],
                },
            ],
        }

    # -------------------------
    # C2 – SEO Content
    # -------------------------
    def _build_seo_content(self, thema: str) -> Dict[str, Any]:
        return {
            "title": f"{thema} – Leitfaden für Business Automation",
            "meta_description": (
                f"Ausführlicher Leitfaden zu {thema} mit Praxisbeispielen, "
                f"Automations-Ideen und System-Strategien."
            ),
            "sections": [
                {
                    "heading": f"Einführung in {thema}",
                    "paragraphs": [
                        f"{thema} ist ein zentraler Baustein moderner Business Automation.",
                        "Richtig eingesetzt, hilft es dir, Zeit zu sparen, Fehler zu reduzieren und dein Unternehmen skalierbar zu machen.",
                    ],
                },
                {
                    "heading": "Typische Probleme ohne Automationen",
                    "paragraphs": [
                        "Viele Teams arbeiten mit manuellen Prozessen, Excel-Listen und Copy-Paste.",
                        "Das führt zu Fehlern, Verzögerungen und Frust – sowohl intern als auch bei Kunden.",
                    ],
                },
                {
                    "heading": f"Wie du {thema} in deinem Business einführst",
                    "paragraphs": [
                        "Starte mit einer klaren Prozessanalyse: Welche Schritte wiederholen sich ständig?",
                        "Definiere ein Minimum Viable System – eine erste, einfache Version deiner Automation.",
                        "Nutze Tools, die zu deinem Tech-Stack passen, statt alles neu zu erfinden.",
                    ],
                },
                {
                    "heading": "Best Practices & nächste Schritte",
                    "paragraphs": [
                        "Dokumentiere deine Workflows, bevor du sie automatisierst.",
                        "Teste jede Automation in einer sicheren Umgebung.",
                        "Iteriere regelmäßig und optimiere auf Basis von echten Daten.",
                    ],
                },
            ],
        }

    # -------------------------
    # HTML Renderer
    # -------------------------
    def _render_html(self, thema: str, content: Dict[str, Any]) -> str:
        title = content["title"]
        meta_desc = content["meta_description"]

        sections_html = []
        for sec in content.get("sections", []):
            block = f"<h2>{sec.get('heading')}</h2>\n"
            for p in sec.get("paragraphs", []):
                block += f"<p>{p}</p>\n"
            if sec.get("bullets"):
                block += "<ul>\n"
                for b in sec["bullets"]:
                    block += f"<li>{b}</li>\n"
                block += "</ul>\n"
            sections_html.append(block)

        sections_joined = "\n".join(sections_html)

        return f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
</head>
<body>
    <header>
        <h1>{title}</h1>
        <p>Nische: {NISCHE} – Produkt-Typ: {PRODUKT_TYP}</p>
    </header>
    <main>
        {sections_joined}
    </main>
    <footer>
        <p>Erstellt am: {datetime.now().isoformat()}</p>
    </footer>
</body>
</html>
        """.strip()

    # -------------------------
    # Markdown Renderer
    # -------------------------
    def _render_markdown(self, thema: str, content: Dict[str, Any]) -> str:
        lines = [
            f"# {content['title']}",
            "",
            f"_Nische: {NISCHE} – Produkt-Typ: {PRODUKT_TYP}_",
            "",
        ]
        for sec in content.get("sections", []):
            lines.append(f"## {sec.get('heading')}")
            for p in sec.get("paragraphs", []):
                lines.append(p)
                lines.append("")
            for b in sec.get("bullets", []):
                lines.append(f"- {b}")
            lines.append("")
        return "\n".join(lines)

    # -------------------------
    # Page Creator (C1 + C2)
    # -------------------------
    def create_page(self, thema: str, variant: str) -> Dict[str, str]:
        slug = self._slugify(thema)

        if variant == "social":
            content = self._build_social_content(thema)
            suffix = "social"
        else:
            content = self._build_seo_content(thema)
            suffix = "seo"

        html = self._render_html(thema, content)
        md = self._render_markdown(thema, content)

        json_data = {
            "thema": thema,
            "variant": variant,
            "title": content["title"],
            "meta_description": content["meta_description"],
            "sections": content["sections"],
            "nische": NISCHE,
            "produkt_typ": PRODUKT_TYP,
            "created_at": datetime.now().isoformat(),
        }

        html_path = os.path.join(OUTPUT_DIR, f"{slug}_{suffix}.html")
        json_path = os.path.join(OUTPUT_DIR, f"{slug}_{suffix}.json")
        md_path = os.path.join(OUTPUT_DIR, f"{slug}_{suffix}.md")

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        save_json(json_path, json_data)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md)

        return {"html": html_path, "json": json_path, "md": md_path}


# ---------------------------------------------------------------------------
# Cluster-Engine
# ---------------------------------------------------------------------------

class ClusterEngine:
    def __init__(self, fabrik_engine: FabrikEngine) -> None:
        self.fabrik_engine = fabrik_engine

    def create_cluster_tasks(self, thema: str) -> str:
        cluster = generate_keyword_cluster(thema)
        keywords = cluster["keywords"]

        for kw in keywords:
            FABRIK.add_task(
                kw,
                lambda t, fe=self.fabrik_engine: fe.create_page(t, "seo")
            )

        return (
            f"🔗 Cluster erstellt für '{thema}'\n"
            f"📌 Keywords: {len(keywords)}\n"
            f"🚀 Tasks in Fabrik-Queue gelegt."
        )

    def handle_cluster_command(self, text: str) -> str:
        parts = text.split(" ", 1)
        if len(parts) < 2:
            return "❌ Bitte nutze: cluster <Thema>"
        thema = parts[1].strip()
        return self.create_cluster_tasks(thema)


# ---------------------------------------------------------------------------
# Pipeline-Engine (Daily + Weekly Pipelines)
# ---------------------------------------------------------------------------

class PipelineEngine:
    def __init__(
        self,
        fabrik_engine: FabrikEngine,
        reel_engine: ReelEngine,
        cluster_engine: ClusterEngine,
        queue: PostingQueue,
    ) -> None:
        self.fabrik_engine = fabrik_engine
        self.reel_engine = reel_engine
        self.cluster_engine = cluster_engine
        self.queue = queue

    def run_pipeline(self, thema: str) -> None:
        log_worker(f"Starte Pipeline für Thema: {thema}")

        slug = thema.strip().replace(" ", "_").lower()

        # 1) Fabrik C1 + C2
        paths_social = self.fabrik_engine.create_page(thema, "social")
        paths_seo = self.fabrik_engine.create_page(thema, "seo")

        log_worker(
            f"Fabrik-Seiten erstellt: Social={paths_social['html']} | SEO={paths_seo['html']}"
        )

        # 2) Cluster
        cluster_msg = self.cluster_engine.create_cluster_tasks(thema)
        log_worker(cluster_msg)

        # 3) Reel + Queue
        script = self.reel_engine.generate_reel_script(thema)
        json_path, txt_path = self.reel_engine.save_reel_script(script)
        self.queue.add_entry(script, json_path, txt_path)

        # 4) Analytics
        log_event(f"page_social_{slug}", "fabrik", {"produced": 1}, {"thema": thema})
        log_event(f"page_seo_{slug}", "fabrik", {"produced": 1}, {"thema": thema})
        log_event(f"reel_{slug}", "reel", {"produced": 1}, {"thema": thema})

        log_worker(f"Pipeline abgeschlossen für Thema: {thema}")


# ---------------------------------------------------------------------------
# Scheduler-Engine
# ---------------------------------------------------------------------------

SCHEDULER_STATE_FILE = os.path.join(CONFIG_DIR, "scheduler_state.json")

DAILY_TIME_STR = "18:00"
DAILY_TIME: dtime = dtime.fromisoformat(DAILY_TIME_STR)

WEEKLY_TOPICS: Dict[int, str] = {
    0: "Automation Basics",
    1: "KI Tools & Agenten",
    2: "Deep Dive",
    3: "Business Automation",
    4: "Quick Wins",
    5: "System Thinking",
}

EVERGREEN_TOPICS: List[str] = [
    "Die 5 wichtigsten Automationen für jedes Business",
    "Wie du deinen ersten Workflow baust",
    "Automationen, die dir 10 Stunden pro Woche sparen",
    "Die häufigsten Fehler bei Automationen",
    "Wie du Prozesse richtig dokumentierst",
    "Die beste Struktur für Automations-Workflows",
    "Wie du Automationen testest, bevor du live gehst",
    "Die 3 Automationen, die jedes kleine Unternehmen braucht",
    "Die besten KI-Tools für Unternehmer",
    "Wie KI-Agenten deinen Alltag automatisieren",
    "Der perfekte KI-Workflow für Lead-Generierung",
    "KI-Agenten für Sales",
    "KI-Agenten für Support",
    "KI-Agenten für Content-Produktion",
    "Wie du KI-Tools kombinierst, um Systeme zu bauen",
    "Die Zukunft von KI-Automationen",
    "Sales-Automationen, die wirklich funktionieren",
    "CRM-Automationen, die du sofort brauchst",
    "Wie du deinen Funnel automatisierst",
    "Reporting-Automationen für Skalierung",
    "Follow-Up-Automationen, die Umsatz bringen",
    "Wie du Leads automatisch qualifizierst",
    "Automatisierte Onboarding-Prozesse",
    "Automatisierte Kundenbindung",
    "Wie du wie ein System-Designer denkst",
    "Die 3 Ebenen eines skalierbaren Systems",
    "Bottlenecks erkennen und lösen",
    "Warum Systeme wichtiger sind als Tools",
    "Wie du dein Business in 90 Tagen systematisierst",
    "Die 5 größten System-Fehler",
    "Wie du Prozesse standardisierst",
    "Wie du dein Business skalierbar machst",
    "1-Minute-Automation für mehr Leads",
    "3 KI-Prompts, die dir sofort Zeit sparen",
    "Mini-Workflow für Content-Planung",
    "Mini-Workflow für Kundenkommunikation",
    "Mini-Workflow für Rechnungen",
    "Mini-Workflow für Social Media",
    "Mini-Workflow für E-Mails",
    "Mini-Workflow für Reporting",
]


class SchedulerStateManager:
    def __init__(self, path: str) -> None:
        self.path = path
        self._ensure_state()

    def _ensure_state(self) -> None:
        default = {
            "paused": False,
            "last_daily_date": None,
            "last_weekly_date": None,
            "evergreen_index": 0,
        }
        state = load_json(self.path, default)
        if not isinstance(state, dict):
            save_json(self.path, default)

    def load(self) -> Dict[str, Any]:
        default = {
            "paused": False,
            "last_daily_date": None,
            "last_weekly_date": None,
            "evergreen_index": 0,
        }
        state = load_json(self.path, default)
        if not isinstance(state, dict):
            save_json(self.path, default)
            return default
        return state

    def save(self, state: Dict[str, Any]) -> None:
        save_json(self.path, state)


class SchedulerEngine:
    def __init__(
        self,
        state_manager: SchedulerStateManager,
        pipeline_engine: PipelineEngine,
    ) -> None:
        self.state_manager = state_manager
        self.pipeline_engine = pipeline_engine

    # -------------------------
    # Daily
    # -------------------------
    def run_daily(self, state: Optional[Dict[str, Any]] = None) -> str:
        if state is None:
            state = self.state_manager.load()

        idx = state.get("evergreen_index", 0)
        thema = EVERGREEN_TOPICS[idx % len(EVERGREEN_TOPICS)]

        self.pipeline_engine.run_pipeline(thema)

        state["evergreen_index"] = idx + 1
        state["last_daily_date"] = datetime.now().date().isoformat()
        self.state_manager.save(state)

        msg = f"📆 Daily-Pipeline ausgeführt für: {thema}"
        log_worker(msg)
        return msg

    # -------------------------
    # Weekly
    # -------------------------
    def run_weekly(self, state: Optional[Dict[str, Any]] = None) -> str:
        if state is None:
            state = self.state_manager.load()

        weekday = datetime.now().weekday()
        thema = WEEKLY_TOPICS.get(weekday)

        if not thema:
            msg = "ℹ️ Kein Weekly-Thema für diesen Tag."
            log_worker(msg)
            return msg

        self.pipeline_engine.run_pipeline(thema)

        state["last_weekly_date"] = datetime.now().date().isoformat()
        self.state_manager.save(state)

        msg = f"📆 Weekly-Pipeline ausgeführt für: {thema}"
        log_worker(msg)
        return msg

    # -------------------------
    # Evergreen (manuell)
    # -------------------------
    def run_evergreen(self, state: Optional[Dict[str, Any]] = None) -> str:
        if state is None:
            state = self.state_manager.load()

        idx = state.get("evergreen_index", 0)
        thema = EVERGREEN_TOPICS[idx % len(EVERGREEN_TOPICS)]

        self.pipeline_engine.run_pipeline(thema)

        state["evergreen_index"] = idx + 1
        self.state_manager.save(state)

        msg = f"🌲 Evergreen-Pipeline ausgeführt für: {thema}"
        log_worker(msg)
        return msg
# ---------------------------------------------------------------------------
# CashBotContext – Zentrale Steuerung aller Engines
# ---------------------------------------------------------------------------

class CashBotContext:
    def __init__(self) -> None:
        # Posting
        self.posting_queue = PostingQueue(POSTING_QUEUE_FILE)
        self.posting_engine = PostingEngine(self.posting_queue)

        # Reel Engine (Auto‑Reels, Voice, Video, Upload)
        self.reel_engine = ReelEngine(
            self.posting_queue,
            INSTAGRAM_TOKEN,
            INSTAGRAM_USER_ID,
            TTS_API_KEY,
            ASSETS_DIR,
        )

        # Fabrik + Cluster
        self.fabrik_engine = FabrikEngine()
        self.cluster_engine = ClusterEngine(self.fabrik_engine)

        # Scheduler
        self.scheduler_state_manager = SchedulerStateManager(SCHEDULER_STATE_FILE)
        self.pipeline_engine = PipelineEngine(
            self.fabrik_engine,
            self.reel_engine,
            self.cluster_engine,
            self.posting_queue,
        )
        self.scheduler_engine = SchedulerEngine(
            self.scheduler_state_manager,
            self.pipeline_engine,
        )

        # Scheduler Command Engine
        self.scheduler_cmd_engine = SchedulerCommandEngine(self.scheduler_engine)

        # KI Router (Command‑Router)
        self.ki_router = KIRouter(
            self.scheduler_cmd_engine,
            self.posting_engine,
            self.reel_engine,
            self.fabrik_engine,
            self.cluster_engine,
        )


# ---------------------------------------------------------------------------
# Globaler Context Loader
# ---------------------------------------------------------------------------

_CTX: Optional[CashBotContext] = None

def _get_context() -> CashBotContext:
    global _CTX
    if _CTX is None:
        _CTX = CashBotContext()
    return _CTX


# ---------------------------------------------------------------------------
# Haupt‑Command‑Router
# ---------------------------------------------------------------------------

def process_ki_anfrage(text: str) -> str:
    ctx = _get_context()
    t = text.lower().strip()

    # Auto‑Reels
    if t.startswith("reel auto"):
        return ctx.reel_engine.handle_auto_reel(text)

    # Standard Reels
    if t.startswith("reel "):
        return ctx.reel_engine.handle_reel_command(text)

    # Posting
    if t.startswith("post "):
        return ctx.posting_engine.handle_post_command(text)

    # Fabrik
    if t.startswith("fabrik "):
        return ctx.fabrik_engine.handle_fabrik_command(text)

    # Cluster
    if t.startswith("cluster "):
        return ctx.cluster_engine.handle_cluster_command(text)

    # Scheduler
    if t.startswith("scheduler "):
        return ctx.scheduler_cmd_engine.handle_scheduler_command(text)

    return "❌ Unbekannter Befehl."
