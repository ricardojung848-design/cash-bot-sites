from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .system_controller import SystemController


REPO_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = REPO_ROOT / "dashboard" / "frontend"
PAGES_DIR = FRONTEND_DIR / "pages"

app = FastAPI(title="CashBot Unified Command Center", version="1.0.0")
controller = SystemController(REPO_ROOT)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8088", "http://localhost:8088"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")


@app.get("/")
def index():
    return FileResponse(str(PAGES_DIR / "index.html"))


@app.get("/api/health")
def health():
    return {"ok": True, "service": "unified-command-center"}


@app.get("/api/home")
def home():
    return controller.get_home()


@app.get("/api/modules")
def modules():
    return {"items": controller.get_modules()}


@app.post("/api/modules/{module_id}/start")
def start_module(module_id: str):
    result = controller.start_module(module_id)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/api/modules/{module_id}/stop")
def stop_module(module_id: str):
    result = controller.stop_module(module_id)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/api/modules/start-all")
def start_all():
    return controller.start_all()


@app.post("/api/modules/stop-all")
def stop_all():
    return controller.stop_all()


@app.get("/api/modules/{module_id}/logs")
def module_logs(module_id: str, lines: int = 200):
    return controller.read_module_log(module_id, lines=lines)


@app.get("/api/tasks")
def tasks():
    return controller.get_tasks()


@app.get("/api/memory")
def memory():
    return controller.get_memory()


@app.get("/api/monitor")
def monitor():
    return controller.get_monitor()


@app.get("/api/settings")
def settings():
    return controller.get_settings()


@app.patch("/api/settings")
def update_settings(payload: Dict[str, Any]):
    return controller.update_settings(payload)


@app.websocket("/ws/status")
async def ws_status(websocket: WebSocket):
    await websocket.accept()
    try:
        async for snapshot in controller.periodic_snapshots():
            await websocket.send_json(snapshot)
    except WebSocketDisconnect:
        return
