"""
core/Logik.py – CashBot / Logik (Version B+ – Agentur-Level, Pipelines + Phase 10 Analytics)
"""

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
}

CONFIG = load_json(CONFIG_FILE, DEFAULT_CONFIG)
NISCHE = CONFIG["nische"]
PRODUKT_TYP = CONFIG["produkt_typ"]
SOCIAL_CFG = CONFIG["social_media"]


# ---------------------------------------------------------------------------
# Posting-Queue (JSON-basiert)
# ---------------------------------------------------------------------------

POSTING_QUEUE_FILE = os.path.join(SOCIAL_DIR, "posting_queue.json")


class PostingQueue:
    """
    JSON-basierte Posting-Queue.
    Status: pending | scheduled | posted | cancelled
    """

    def __init__(self, path: str) -> None:
        self.path = path
        self._ensure_file()

    def _ensure_file(self) -> None:
        queue = load_json(self.path, [])
        if not isinstance(queue, list):
            warn_worker("Posting-Queue war beschädigt – neu initialisiert.")
            queue = []
            save_json(self.path, queue)

    def _load(self) -> List[Dict[str, Any]]:
        queue = load_json(self.path, [])
        if not isinstance(queue, list):
            warn_worker("Posting-Queue war beschädigt – neu initialisiert.")
            queue = []
            save_json(self.path, queue)
        return queue

    def _save(self, queue: List[Dict[str, Any]]) -> None:
        save_json(self.path, queue)

    def _next_id(self, queue: List[Dict[str, Any]]) -> int:
        if not queue:
            return 1
        return max(item.get("id", 0) for item in queue) + 1

    def add_entry(
        self,
        script: Dict[str, Any],
        json_path: str,
        txt_path: str,
        auto_post: bool = False,
    ) -> Dict[str, Any]:
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
                return f"🛑 Posting mit ID {post_id} wurde abgebrochen."
        return f"❌ Kein aktiver Eintrag mit ID {post_id} gefunden."

    def overview_text(self) -> str:
        queue = self._load()
        if not queue:
            return "📭 Posting-Queue ist leer."

        lines = ["📋 Posting-Queue:"]
        for item in queue:
            sched = item.get("scheduled_at")
            sched_str = f"📅 {sched}" if sched else ""
            lines.append(
                f"- ID {item['id']}: {item['thema']} [{item['status']}] {sched_str}"
            )
        return "\n".join(lines)

    def status_text(self) -> str:
        queue = self._load()
        if not queue:
            return "📭 Keine Einträge in der Posting-Queue."

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
        msg = f"💥 Simuliertes Posting veröffentlicht für: {entry['thema']}"
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
            status = entry.get("status", "pending")

            if status not in ("pending", "scheduled"):
                continue

            if entry.get("auto_post") is True:
                result = self._perform_post(entry)
                self._mark_posted(entry)
                changed = True
                continue

            sched_str = entry.get("scheduled_at")
            if sched_str:
                try:
                    sched = datetime.fromisoformat(sched_str)
                    if now >= sched:
                        result = self._perform_post(entry)
                        self._mark_posted(entry)
                        changed = True
                except Exception as e:
                    warn_worker(f"Fehler beim Lesen von scheduled_at: {e}")

        if changed:
            self.queue.save_entries(queue)

    def handle_post_command(self, text: str) -> str:
        t = text.lower().strip()

        if t.startswith("post now"):
            parts = text.split(" ", 2)
            if len(parts) < 3:
                return "❌ Bitte nutze: post now <Thema>"
            thema = parts[2].strip()
            queue = self.queue.list_entries()
            for entry in queue:
                if entry["thema"].lower() == thema.lower() and entry["status"] in ("pending", "scheduled"):
                    entry["auto_post"] = True
                    self.queue.save_entries(queue)
                    return f"🚀 Posting für '{thema}' wird sofort ausgeführt."
            return f"❌ Kein aktiver Eintrag für '{thema}' gefunden."

        if t.startswith("post schedule"):
            parts = text.split(" ", 4)
            if len(parts) < 5:
                return "❌ Nutze: post schedule <YYYY-MM-DD> <HH:MM> <Thema>"
            date_str = parts[2]
            time_str = parts[3]
            thema = parts[4]
            try:
                sched = datetime.fromisoformat(f"{date_str} {time_str}")
            except:
                return "❌ Ungültiges Datum/Uhrzeit."
            queue = self.queue.list_entries()
            for entry in queue:
                if entry["thema"].lower() == thema.lower() and entry["status"] in ("pending", "scheduled"):
                    entry["scheduled_at"] = sched.isoformat()
                    entry["status"] = "scheduled"
                    self.queue.save_entries(queue)
                    return f"📅 Posting geplant am {sched}"
            return f"❌ Kein Eintrag für '{thema}' gefunden."

        if t.startswith("post cancel"):
            parts = text.split(" ", 2)
            if len(parts) < 3:
                return "❌ Nutze: post cancel <ID>"
            try:
                post_id = int(parts[2])
            except:
                return "❌ ID muss eine Zahl sein."
            return self.queue.cancel_by_id(post_id)

        if t.startswith("post clear"):
            self.queue.clear()
            return "🧹 Queue geleert."

        if t.startswith("post status"):
            return self.queue.status_text()

        if t.startswith("post list"):
            return self.queue.overview_text()

        return "❌ Unbekannter Post-Befehl."
# ---------------------------------------------------------------------------
# Reel-Engine
# ---------------------------------------------------------------------------

class ReelEngine:
    def __init__(self, queue: PostingQueue) -> None:
        self.queue = queue

    def generate_reel_script(self, thema: str) -> Dict[str, Any]:
        thema_clean = thema.strip()
        return {
            "thema": thema_clean,
            "nische": NISCHE,
            "produkt_typ": PRODUKT_TYP,
            "hook": (
                f"🔥 Du willst {thema_clean} endlich meistern – "
                f"aber weißt nicht, wo du anfangen sollst?"
            ),
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

    # -------------------------
    # Fabrik Command
    # -------------------------
    def handle_fabrik_command(self, text: str) -> str:
        parts = text.split(" ", 1)
        if len(parts) < 2:
            return "❌ Bitte nutze: fabrik <Thema>"

        thema = parts[1].strip()
        paths_social = self.create_page(thema, "social")
        paths_seo = self.create_page(thema, "seo")

        return (
            f"🏭 Fabrik-Seiten erstellt für: {thema}\n"
            f"• Social (C1):\n"
            f"  - {paths_social['html']}\n"
            f"  - {paths_social['json']}\n"
            f"  - {paths_social['md']}\n"
            f"• SEO (C2):\n"
            f"  - {paths_seo['html']}\n"
            f"  - {paths_seo['json']}\n"
            f"  - {paths_seo['md']}"
        )
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
# Scheduler-Konfiguration
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


# ---------------------------------------------------------------------------
# Scheduler-State
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Pipeline-Engine (F3 – Daily + Weekly Pipelines)
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
        cid_social = f"page_social_{slug}"
        cid_seo = f"page_seo_{slug}"
        cid_reel = f"reel_{slug}"

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

        # 4) Analytics (produced)
        log_event(cid_social, "fabrik", {"produced": 1}, {"thema": thema})
        log_event(cid_seo, "fabrik", {"produced": 1}, {"thema": thema})
        log_event(cid_reel, "reel", {"produced": 1}, {"thema": thema})

        log_worker(f"Pipeline abgeschlossen für Thema: {thema}")


# ---------------------------------------------------------------------------
# Scheduler-Engine
# ---------------------------------------------------------------------------

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

        msg = f"🔁 Evergreen-Pipeline ausgeführt für: {thema}"
        log_worker(msg)
        return msg

    # -------------------------
    # Tick (optional)
    # -------------------------
    def tick(self) -> None:
        state = self.state_manager.load()
        if state.get("paused"):
            return

        now = datetime.now()
        today = now.date().isoformat()
        current_time = now.time()

        last_daily = state.get("last_daily_date")
        last_weekly = state.get("last_weekly_date")
        weekday = now.weekday()

        if current_time >= DAILY_TIME and last_daily != today:
            self.run_daily(state)

        if current_time >= DAILY_TIME and last_weekly != today and weekday in WEEKLY_TOPICS:
            self.run_weekly(state)

    # -------------------------
    # Status
    # -------------------------
    def status_text(self) -> str:
        state = self.state_manager.load()
        idx = state.get("evergreen_index", 0)
        next_ev = EVERGREEN_TOPICS[idx % len(EVERGREEN_TOPICS)]

        return (
            "🧠 Scheduler-Status:\n"
            f"• Paused: {state.get('paused')}\n"
            f"• Letzter Daily-Run: {state.get('last_daily_date')}\n"
            f"• Letzter Weekly-Run: {state.get('last_weekly_date')}\n"
            f"• Daily-Time: {DAILY_TIME_STR}\n"
            f"• Nächster Evergreen-Index: {idx}\n"
            f"• Nächstes Evergreen-Thema: {next_ev}"
        )

    def pause(self) -> str:
        state = self.state_manager.load()
        state["paused"] = True
        self.state_manager.save(state)
        return "⏸ Scheduler pausiert."

    def resume(self) -> str:
        state = self.state_manager.load()
        state["paused"] = False
        self.state_manager.save(state)
        return "▶ Scheduler wieder aktiviert."
# ---------------------------------------------------------------------------
# Scheduler Command Engine
# ---------------------------------------------------------------------------

DAY_MAPPING: Dict[str, int] = {
    "montag": 0, "mo": 0, "monday": 0, "mon": 0,
    "dienstag": 1, "di": 1, "tuesday": 1, "tue": 1,
    "mittwoch": 2, "mi": 2, "wednesday": 2, "wed": 2,
    "donnerstag": 3, "do": 3, "thursday": 3, "thu": 3,
    "freitag": 4, "fr": 4, "friday": 4, "fri": 4,
    "samstag": 5, "sa": 5, "saturday": 5, "sat": 5,
    "sonntag": 6, "so": 6, "sunday": 6, "sun": 6,
}


class SchedulerCommandEngine:
    def __init__(self, scheduler: SchedulerEngine) -> None:
        self.scheduler = scheduler

    # -------------------------
    # Helper
    # -------------------------
    def _list_weekly(self) -> str:
        lines = ["📅 Weekly-Themen:"]
        for day, thema in sorted(WEEKLY_TOPICS.items(), key=lambda x: x[0]):
            lines.append(f"- {day}: {thema}")
        return "\n".join(lines)

    def _list_evergreen(self) -> str:
        lines = ["🌲 Evergreen-Themen:"]
        for i, thema in enumerate(EVERGREEN_TOPICS):
            lines.append(f"{i}: {thema}")
        return "\n".join(lines)

    def _set_daily_time(self, new_time_str: str) -> str:
        global DAILY_TIME_STR, DAILY_TIME
        try:
            DAILY_TIME = dtime.fromisoformat(new_time_str)
            DAILY_TIME_STR = new_time_str
            return f"⏰ Daily-Zeit gesetzt auf {new_time_str}"
        except:
            return "❌ Ungültiges Zeitformat. Nutze HH:MM"

    def _set_weekly(self, day_str: str, thema: str) -> str:
        day = day_str.lower().strip()
        if day not in DAY_MAPPING:
            return "❌ Ungültiger Tag."
        WEEKLY_TOPICS[DAY_MAPPING[day]] = thema
        return f"📅 Weekly-Thema für {day_str} gesetzt auf: {thema}"

    def _add_evergreen(self, thema: str) -> str:
        EVERGREEN_TOPICS.append(thema)
        return f"🌲 Evergreen-Thema hinzugefügt: {thema}"

    def _remove_evergreen(self, index_str: str) -> str:
        try:
            idx = int(index_str)
            thema = EVERGREEN_TOPICS.pop(idx)
            return f"🗑 Evergreen-Thema entfernt: {thema}"
        except:
            return "❌ Ungültiger Index."

    def _help_text(self) -> str:
        return (
            "📆 Scheduler-Commands:\n"
            "· scheduler status\n"
            "· scheduler pause\n"
            "· scheduler resume\n"
            "· scheduler run daily\n"
            "· scheduler run weekly\n"
            "· scheduler run evergreen\n"
            "· scheduler list weekly\n"
            "· scheduler list evergreen\n"
            "· scheduler set daily <HH:MM>\n"
            "· scheduler set weekly <Tag> <Thema>\n"
            "· scheduler add evergreen <Thema>\n"
            "· scheduler remove evergreen <Index>\n"
            "· scheduler analytics [evergreen|weekly]\n"
        )

    # -------------------------
    # Command Handler
    # -------------------------
    def handle_command(self, text: str) -> str:
        parts = text.strip().split(" ")

        if len(parts) < 2:
            return self._help_text()

        if parts[0].lower() != "scheduler":
            return "❌ Bitte nutze: scheduler <command>"

        cmd = parts[1].lower()

        # STATUS
        if cmd == "status":
            return self.scheduler.status_text()

        # PAUSE / RESUME
        if cmd == "pause":
            return self.scheduler.pause()
        if cmd == "resume":
            return self.scheduler.resume()

        # RUN
        if cmd == "run":
            if len(parts) < 3:
                return "❌ Nutze: scheduler run daily|weekly|evergreen"
            mode = parts[2].lower()
            if mode == "daily":
                return self.scheduler.run_daily()
            if mode == "weekly":
                return self.scheduler.run_weekly()
            if mode == "evergreen":
                return self.scheduler.run_evergreen()
            return "❌ Unbekannter Run-Modus."

        # LIST
        if cmd == "list":
            if len(parts) < 3:
                return "❌ Nutze: scheduler list weekly|evergreen"
            mode = parts[2].lower()
            if mode == "weekly":
                return self._list_weekly()
            if mode == "evergreen":
                return self._list_evergreen()
            return "❌ Unbekannte Liste."

        # SET
        if cmd == "set":
            if len(parts) < 4:
                return "❌ Nutze: scheduler set daily <HH:MM> ODER scheduler set weekly <Tag> <Thema>"
            mode = parts[2].lower()
            if mode == "daily":
                return self._set_daily_time(parts[3])
            if mode == "weekly":
                if len(parts) < 5:
                    return "❌ Nutze: scheduler set weekly <Tag> <Thema>"
                day = parts[3]
                thema = " ".join(parts[4:])
                return self._set_weekly(day, thema)
            return "❌ Unbekannter Set-Modus."

        # ADD EVERGREEN
        if cmd == "add":
            if len(parts) < 4 or parts[2].lower() != "evergreen":
                return "❌ Nutze: scheduler add evergreen <Thema>"
            thema = " ".join(parts[3:])
            return self._add_evergreen(thema)

        # REMOVE EVERGREEN
        if cmd == "remove":
            if len(parts) < 4 or parts[2].lower() != "evergreen":
                return "❌ Nutze: scheduler remove evergreen <Index>"
            return self._remove_evergreen(parts[3])

        # ANALYTICS
        if cmd == "analytics":
            if len(parts) == 2:
                ev = build_evergreen_ranking()
                wk = build_weekly_ranking()
                return ev + "\n\n" + wk
            mode = parts[2].lower()
            if mode == "evergreen":
                return build_evergreen_ranking()
            if mode == "weekly":
                return build_weekly_ranking()
            return "❌ Nutze: scheduler analytics [evergreen|weekly]"

        return self._help_text()


# ---------------------------------------------------------------------------
# KI-Router
# ---------------------------------------------------------------------------

class KIRouter:
    def __init__(
        self,
        scheduler_cmd_engine: SchedulerCommandEngine,
        posting_engine: PostingEngine,
        reel_engine: ReelEngine,
        fabrik_engine: FabrikEngine,
        cluster_engine: ClusterEngine,
    ) -> None:
        self.scheduler_cmd_engine = scheduler_cmd_engine
        self.posting_engine = posting_engine
        self.reel_engine = reel_engine
        self.fabrik_engine = fabrik_engine
        self.cluster_engine = cluster_engine

    def handle_message(self, text: str) -> str:
        t = text.strip().lower()

        if t.startswith("scheduler"):
            return self.scheduler_cmd_engine.handle_command(text)
        if t.startswith("post"):
            return self.posting_engine.handle_post_command(text)
        if t.startswith("reel"):
            return self.reel_engine.handle_reel_command(text)
        if t.startswith("fabrik"):
            return self.fabrik_engine.handle_fabrik_command(text)
        if t.startswith("cluster"):
            return self.cluster_engine.handle_cluster_command(text)

        return (
            "❌ Unbekannter Befehl.\n"
            "Verfügbare Prefixe:\n"
            "· scheduler ...\n"
            "· post ...\n"
            "· reel ...\n"
            "· fabrik ...\n"
            "· cluster ..."
        )


# ---------------------------------------------------------------------------
# CashBotContext (Singleton)
# ---------------------------------------------------------------------------

class CashBotContext:
    def __init__(self) -> None:
        self.posting_queue = PostingQueue(POSTING_QUEUE_FILE)
        self.posting_engine = PostingEngine(self.posting_queue)
        self.reel_engine = ReelEngine(self.posting_queue)
        self.fabrik_engine = FabrikEngine()
        self.cluster_engine = ClusterEngine(self.fabrik_engine)

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
        self.scheduler_cmd_engine = SchedulerCommandEngine(self.scheduler_engine)

        self.ki_router = KIRouter(
            self.scheduler_cmd_engine,
            self.posting_engine,
            self.reel_engine,
            self.fabrik_engine,
            self.cluster_engine,
        )


_CTX: Optional[CashBotContext] = None


def _get_context() -> CashBotContext:
    global _CTX
    if _CTX is None:
        log_worker("Initialisiere CashBotContext (Logik.py – Agentur-Level, Pipelines + Analytics)...")
        _CTX = CashBotContext()
    return _CTX


# ---------------------------------------------------------------------------
# Öffentliche API
# ---------------------------------------------------------------------------

def process_ki_anfrage(text: str) -> str:
    try:
        ctx = _get_context()
        return ctx.ki_router.handle_message(text)
    except Exception as e:
        error_worker(f"Fehler in process_ki_anfrage: {e}")
        return f"❌ Fehler in process_ki_anfrage: {e}"


def auto_posting_tick() -> None:
    try:
        ctx = _get_context()
        ctx.posting_engine.auto_posting_tick()
        # Optional: Scheduler automatisch mitlaufen lassen
        # ctx.scheduler_engine.tick()
    except Exception as e:
        error_worker(f"Fehler in auto_posting_tick: {e}")
