"""
Flask API Backend für Affiliate & SEO Engine
REST API für Web-UI
"""
from flask import Flask, jsonify, request, render_template, send_file
from flask_cors import CORS
import os
import json
from datetime import datetime
from affiliate_engine.config import WEB_CONFIG
from affiliate_engine.db.database import AffiliateDatabase
from affiliate_engine.api_wrappers.affiliate_apis import AffiliateAPIManager
from affiliate_engine.generators.program_selector import ProgramSelector
from affiliate_engine.generators.content_generator import ContentGenerator
from affiliate_engine.generators.tracking_manager import TrackingLinkManager
from affiliate_engine.scheduler.job_scheduler import SchedulerManager

# Initialize Flask
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = WEB_CONFIG["secret_key"]
CORS(app)

# Initialize components
db = AffiliateDatabase()
api_manager = AffiliateAPIManager()
program_selector = ProgramSelector()
content_gen = ContentGenerator()
tracking_manager = TrackingLinkManager()
scheduler_manager = SchedulerManager()

# ============================================================================
# HEALTH CHECK & INFO
# ============================================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health Check"""
    return jsonify({
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
    }), 200

@app.route("/api/info", methods=["GET"])
def system_info():
    """Systeminfos"""
    return jsonify({
        "name": "Affiliate & SEO Engine",
        "version": "1.0.0",
        "components": {
            "database": "sqlite3",
            "scheduler": "apscheduler",
            "content_engine": "LM Studio / OpenAI",
        },
        "networks": api_manager.get_available_networks(),
        "timestamp": datetime.now().isoformat(),
    }), 200

# ============================================================================
# AFFILIATE PROGRAMME
# ============================================================================

@app.route("/api/programs", methods=["GET"])
def get_programs():
    """Hole alle Affiliate-Programme"""
    programs = db.get_all_programs()
    return jsonify({
        "total": len(programs),
        "programs": programs,
    }), 200

@app.route("/api/programs/available", methods=["GET"])
def get_available_networks():
    """Hole verfügbare Netzwerke"""
    networks = api_manager.get_available_networks()
    return jsonify(networks), 200

@app.route("/api/programs/add", methods=["POST"])
def add_program():
    """Füge Affiliate-Programm hinzu"""
    data = request.json
    try:
        program_id = db.add_program(
            name=data["name"],
            network=data["network"],
            api_endpoint=data.get("api_endpoint"),
            commission_rate=data.get("commission_rate"),
            categories=data.get("categories"),
        )
        return jsonify({
            "status": "success",
            "program_id": program_id,
        }), 201
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 400

# ============================================================================
# LANDING PAGES
# ============================================================================

@app.route("/api/landing-pages", methods=["GET"])
def get_landing_pages():
    """Hole alle Landing Pages"""
    status = request.args.get("status")
    pages = db.get_landing_pages(status=status)
    return jsonify({
        "total": len(pages),
        "pages": pages,
    }), 200

@app.route("/api/landing-pages/<int:lp_id>", methods=["GET"])
def get_landing_page(lp_id):
    """Hole einzelne Landing Page"""
    pages = db.get_landing_pages()
    page = next((p for p in pages if p["id"] == lp_id), None)
    if page:
        return jsonify(page), 200
    return jsonify({"error": "Nicht gefunden"}), 404

# ============================================================================
# CONTENT GENERATION
# ============================================================================

@app.route("/api/generate/article", methods=["POST"])
def generate_article():
    """Generiere Article"""
    data = request.json
    
    try:
        result = content_gen.generate_article(
            topic=data.get("topic", "Untitled"),
            main_keyword=data.get("main_keyword", ""),
            keywords=data.get("keywords", []),
            programs=data.get("programs", []),
        )
        
        return jsonify(result), 200 if result["status"] == "success" else 400
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
        }), 500

@app.route("/api/generate/landing-page", methods=["POST"])
def generate_landing_page():
    """Generiere komplette Landing Page"""
    data = request.json
    
    try:
        topic = data.get("topic")
        keywords = data.get("keywords", [])
        
        # 1. Wähle Programme
        programs = program_selector.select_programs_for_topic(
            topic=topic,
            keywords=keywords,
        )
        
        # 2. Generiere Content
        content_result = content_gen.generate_article(
            topic=topic,
            main_keyword=keywords[0] if keywords else topic,
            keywords=keywords,
            programs=programs,
        )
        
        if content_result["status"] != "success":
            return jsonify(content_result), 400
        
        # 3. Generiere HTML
        html = content_gen.generate_landing_page(
            topic=topic,
            article_content=content_result["content"],
            programs=programs,
        )
        
        # 4. Speichere in DB
        slug = topic.lower().replace(" ", "-")
        lp_id = db.add_landing_page(
            title=topic,
            slug=slug,
            topic=topic,
            content=content_result["content"],
            affiliate_programs=programs,
            seo_keywords=keywords,
            main_keyword=keywords[0] if keywords else topic,
            meta_description=content_result.get("meta_description", ""),
            h1_title=content_result.get("h1_title", ""),
            status="draft",
        )
        
        return jsonify({
            "status": "success",
            "lp_id": lp_id,
            "title": topic,
            "slug": slug,
            "word_count": content_result.get("word_count"),
            "programs": programs,
        }), 201
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
        }), 500

# ============================================================================
# TRACKING LINKS
# ============================================================================

@app.route("/api/tracking-links", methods=["GET"])
def get_tracking_links():
    """Hole Tracking-Links"""
    lp_id = request.args.get("lp_id", type=int)
    if lp_id:
        links = db.get_tracking_links(lp_id)
        return jsonify({"links": links}), 200
    return jsonify({"error": "lp_id erforderlich"}), 400

@app.route("/api/tracking-links/create", methods=["POST"])
def create_tracking_link():
    """Erstelle Tracking-Link"""
    data = request.json
    
    try:
        result = tracking_manager.create_tracking_link(
            landing_page_id=data["lp_id"],
            program_id=data.get("program_id", 0),
            original_url=data["original_url"],
            campaign_name=data.get("campaign_name", ""),
        )
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/tracking-links/<int:link_id>/stats", methods=["GET"])
def get_link_stats(link_id):
    """Hole Stats für Link"""
    stats = tracking_manager.get_link_stats(link_id)
    return jsonify(stats), 200

# ============================================================================
# SCHEDULER
# ============================================================================

@app.route("/api/scheduler/status", methods=["GET"])
def scheduler_status():
    """Hole Scheduler-Status"""
    status = scheduler_manager.get_job_status()
    return jsonify(status), 200

@app.route("/api/scheduler/start", methods=["POST"])
def start_scheduler():
    """Starten Sie den Scheduler"""
    try:
        scheduler_manager.start()
        scheduler_manager.schedule_daily_generation()
        return jsonify({
            "status": "started",
            "message": "Scheduler läuft",
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/scheduler/stop", methods=["POST"])
def stop_scheduler():
    """Stoppe Scheduler"""
    try:
        scheduler_manager.stop()
        return jsonify({
            "status": "stopped",
            "message": "Scheduler gestoppt",
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/scheduler/test-generation", methods=["POST"])
def test_generation():
    """Test Content-Generierung"""
    try:
        scheduler_manager.test_generation()
        return jsonify({
            "status": "generating",
            "message": "Test-Generierung gestartet",
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# ANALYTICS
# ============================================================================

@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    """Hole Analytics"""
    days = request.args.get("days", 30, type=int)
    analytics = tracking_manager.get_analytics(days=days)
    return jsonify(analytics), 200

# ============================================================================
# KEYWORDS
# ============================================================================

@app.route("/api/keywords", methods=["GET"])
def get_keywords():
    """Hole Keywords"""
    keywords = db.get_keywords()
    return jsonify({"keywords": keywords}), 200

@app.route("/api/keywords/add", methods=["POST"])
def add_keyword():
    """Füge Keyword hinzu"""
    data = request.json
    try:
        db.add_keyword(
            keyword=data["keyword"],
            search_volume=data.get("search_volume", 0),
            difficulty=data.get("difficulty", 0),
        )
        return jsonify({"status": "success"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ============================================================================
# WEB UI PAGES
# ============================================================================

@app.route("/", methods=["GET"])
def dashboard():
    """Haupt-Dashboard"""
    try:
        return render_template("dashboard.html")
    except:
        return send_file("static/index.html")

@app.route("/pages/<path:filename>", methods=["GET"])
def serve_generated_page(filename):
    """Serviere generierte Landing Page"""
    try:
        filepath = f"pages/{filename}"
        return send_file(filepath)
    except:
        return jsonify({"error": "Seite nicht gefunden"}), 404

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Server Error"}), 500

if __name__ == "__main__":
    print("[*] Starte Affiliate & SEO Engine API...")
    print(f"[*] Host: {WEB_CONFIG['host']}:{WEB_CONFIG['port']}")
    print(f"[*] Debug: {WEB_CONFIG['debug']}")
    
    app.run(
        host=WEB_CONFIG["host"],
        port=WEB_CONFIG["port"],
        debug=WEB_CONFIG["debug"],
        use_reloader=False,
    )
