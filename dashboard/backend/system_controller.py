import asyncio
import json
import os
import sqlite3
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import psutil  # type: ignore
except Exception:
    psutil = None


class SystemController:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.dashboard_root = repo_root / "dashboard"
        self.system_root = self.dashboard_root / "system"
        self.logs_dir = self.system_root / "logs"
        self.config_dir = self.system_root / "config"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.registry_file = self.config_dir / "module_registry.json"
        self.settings_file = self.config_dir / "settings.json"
        self.audit_file = self.logs_dir / "audit.log"
        self._lock = threading.Lock()
        self._processes: Dict[str, Dict[str, Any]] = {}

        self._ensure_default_files()

    def _ensure_default_files(self) -> None:
        if not self.registry_file.exists():
            default_registry = {
                "modules": [
                    {
                        "id": "agent_worker",
                        "name": "Agent Worker",
                        "path": "Cash_Bot/core/Agent_Worker.py",
                        "cwd": "Cash_Bot",
                        "type": "service",
                        "internet_required": False,
                    },
                    {
                        "id": "agent_doctor",
                        "name": "Agent Doctor",
                        "path": "Cash_Bot/modules/Agent_Doctor.py",
                        "cwd": "Cash_Bot",
                        "type": "service",
                        "internet_required": False,
                    },
                    {
                        "id": "agent_scout",
                        "name": "Agent Scout",
                        "path": "Cash_Bot/modules/Agent_Scout.py",
                        "cwd": "Cash_Bot",
                        "type": "service",
                        "internet_required": True,
                    },
                    {
                        "id": "agent_wallet",
                        "name": "Agent Wallet",
                        "path": "Cash_Bot/modules/Agent_Wallet.py",
                        "cwd": "Cash_Bot",
                        "type": "service",
                        "internet_required": False,
                    },
                    {
                        "id": "agent_telegram",
                        "name": "Agent Telegram",
                        "path": "Cash_Bot/core/Agent_Telegram.py",
                        "cwd": "Cash_Bot",
                        "type": "service",
                        "internet_required": True,
                    },
                    {
                        "id": "content_orchestrator",
                        "name": "Content Orchestrator",
                        "path": "module/Modul_MasterOrchestrator.py",
                        "cwd": ".",
                        "type": "job",
                        "internet_required": True,
                    },
                    {
                        "id": "monetization_controller",
                        "name": "Monetization Controller",
                        "path": "module/Modul_MonetizationController.py",
                        "cwd": ".",
                        "type": "job",
                        "internet_required": True,
                    },
                ]
            }
            self.registry_file.write_text(json.dumps(default_registry, indent=2), encoding="utf-8")

        if not self.settings_file.exists():
            default_settings = {
                "theme": "dark-neon",
                "language": "de",
                "personality_mode": "strategic",
                "offline_only": True,
                "security": {"sandbox_enabled": True, "require_admin_for_stop_all": True},
                "roles": ["admin", "operator", "viewer"],
            }
            self.settings_file.write_text(json.dumps(default_settings, indent=2), encoding="utf-8")

    def _audit(self, action: str, details: str) -> None:
        timestamp = datetime.now().isoformat(timespec="seconds")
        with self.audit_file.open("a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {action}: {details}\n")

    def _read_registry(self) -> List[Dict[str, Any]]:
        data = json.loads(self.registry_file.read_text(encoding="utf-8"))
        return data.get("modules", [])

    def get_modules(self) -> List[Dict[str, Any]]:
        modules = self._read_registry()
        now = datetime.now().isoformat(timespec="seconds")
        result = []
        for module in modules:
            status = self._status_for_module(module["id"])
            result.append({**module, "status": status, "last_checked": now})
        return result

    def _status_for_module(self, module_id: str) -> str:
        with self._lock:
            proc_info = self._processes.get(module_id)
            if not proc_info:
                return "inactive"
            proc: subprocess.Popen = proc_info["proc"]
            code = proc.poll()
            if code is None:
                return "active"
            return "failed" if code != 0 else "completed"

    def start_module(self, module_id: str) -> Dict[str, Any]:
        modules = {m["id"]: m for m in self._read_registry()}
        module = modules.get(module_id)
        if not module:
            return {"ok": False, "message": f"Modul '{module_id}' nicht gefunden."}

        settings = self.get_settings()
        if settings.get("offline_only", True) and module.get("internet_required", False):
            return {
                "ok": False,
                "message": f"{module['name']} ist im Offline-Only Modus gesperrt (internet_required=true).",
            }

        with self._lock:
            existing = self._processes.get(module_id)
            if existing and existing["proc"].poll() is None:
                return {"ok": False, "message": f"{module['name']} läuft bereits."}

        script_path = (self.repo_root / module["path"]).resolve()
        if not script_path.exists():
            return {"ok": False, "message": f"Datei nicht gefunden: {module['path']}"}

        cwd = (self.repo_root / module.get("cwd", ".")).resolve()
        log_path = self.logs_dir / f"{module_id}.log"
        log_handle = log_path.open("a", encoding="utf-8")

        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONPATH"] = str(self.repo_root) + os.pathsep + env.get("PYTHONPATH", "")

        proc = subprocess.Popen(
            [os.environ.get("PYTHON_EXECUTABLE", os.sys.executable), str(script_path)],
            cwd=str(cwd),
            env=env,
            stdout=log_handle,
            stderr=log_handle,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )

        with self._lock:
            self._processes[module_id] = {"proc": proc, "log": str(log_path), "started_at": time.time()}

        self._audit("START_MODULE", f"{module['name']} ({module_id})")
        return {"ok": True, "message": f"{module['name']} wurde gestartet."}

    def stop_module(self, module_id: str) -> Dict[str, Any]:
        with self._lock:
            info = self._processes.get(module_id)
            if not info:
                return {"ok": False, "message": "Modul läuft nicht."}
            proc: subprocess.Popen = info["proc"]
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
            self._processes.pop(module_id, None)
        self._audit("STOP_MODULE", module_id)
        return {"ok": True, "message": f"{module_id} gestoppt."}

    def start_all(self) -> Dict[str, Any]:
        results = [self.start_module(m["id"]) for m in self._read_registry()]
        return {"ok": True, "results": results}

    def stop_all(self) -> Dict[str, Any]:
        for m in self._read_registry():
            self.stop_module(m["id"])
        self._audit("STOP_ALL", "all modules")
        return {"ok": True, "message": "Alle Module wurden gestoppt."}

    def read_module_log(self, module_id: str, lines: int = 200) -> Dict[str, Any]:
        log_path = self.logs_dir / f"{module_id}.log"
        if not log_path.exists():
            return {"ok": True, "module_id": module_id, "content": ""}
        content = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        return {"ok": True, "module_id": module_id, "content": "\n".join(content[-lines:])}

    def get_tasks(self) -> Dict[str, Any]:
        tasks_file = self.repo_root / "Cash_Bot" / "aufgaben.json"
        running = []
        if tasks_file.exists():
            try:
                data = json.loads(tasks_file.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    running = data[-50:]
            except Exception:
                running = []

        scheduled = []
        db_path = self.repo_root / "Cash_Bot" / "core" / "aegis_storage.db"
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            try:
                rows = conn.execute("SELECT id, title, status, created_at FROM tasks ORDER BY id DESC LIMIT 50").fetchall()
                scheduled = [
                    {"id": r[0], "title": r[1], "status": r[2], "created_at": r[3]}
                    for r in rows
                ]
            finally:
                conn.close()

        return {"running": running, "scheduled": scheduled, "history": scheduled[:20], "errors": self._recent_errors()}

    def _recent_errors(self) -> List[str]:
        out = []
        for p in (self.repo_root / "Cash_Bot" / "logs").glob("*error*.log"):
            try:
                text = p.read_text(encoding="utf-8", errors="ignore").strip()
                if text:
                    out.append(f"{p.name}: {text.splitlines()[-1]}")
            except Exception:
                continue
        return out[:20]

    def get_memory(self) -> Dict[str, Any]:
        db_path = self.repo_root / "Cash_Bot" / "config" / "doctor_memory.sqlite"
        short_memory: List[Dict[str, Any]] = []
        long_memory: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            try:
                rows = conn.execute(
                    "SELECT key, data, last_update FROM system_states ORDER BY last_update DESC LIMIT 30"
                ).fetchall()
                short_memory = [dict(r) for r in rows]
                long_memory = short_memory
                erows = conn.execute(
                    "SELECT module_name, error_message, timestamp FROM error_history ORDER BY id DESC LIMIT 20"
                ).fetchall()
                errors = [dict(r) for r in erows]
            finally:
                conn.close()

        docs_dir = self.repo_root / "Cash_Bot" / "docs"
        docs = [p.name for p in docs_dir.glob("*.md")] if docs_dir.exists() else []
        return {
            "short_term": short_memory,
            "long_term": long_memory,
            "documents": docs,
            "feedback_history": errors,
            "personal_data": {"personality_mode": self.get_settings().get("personality_mode", "strategic")},
        }

    def get_monitor(self) -> Dict[str, Any]:
        if psutil is None:
            return {
                "cpu_percent": 0,
                "ram_percent": 0,
                "gpu_percent": None,
                "network": {"sent_mb": 0, "recv_mb": 0},
                "processes": self._list_processes(),
                "temperature": None,
                "background_services": self._active_modules(),
            }

        vm = psutil.virtual_memory()
        net = psutil.net_io_counters()
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "ram_percent": vm.percent,
            "gpu_percent": None,
            "network": {"sent_mb": round(net.bytes_sent / 1024 / 1024, 2), "recv_mb": round(net.bytes_recv / 1024 / 1024, 2)},
            "processes": self._list_processes(),
            "temperature": None,
            "background_services": self._active_modules(),
        }

    def _list_processes(self) -> List[Dict[str, Any]]:
        procs = []
        with self._lock:
            for module_id, info in self._processes.items():
                proc: subprocess.Popen = info["proc"]
                procs.append(
                    {
                        "module_id": module_id,
                        "pid": proc.pid,
                        "status": "active" if proc.poll() is None else "stopped",
                    }
                )
        return procs

    def _active_modules(self) -> List[str]:
        with self._lock:
            return [k for k, v in self._processes.items() if v["proc"].poll() is None]

    def get_settings(self) -> Dict[str, Any]:
        return json.loads(self.settings_file.read_text(encoding="utf-8"))

    def update_settings(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        current = self.get_settings()
        current.update(payload)
        self.settings_file.write_text(json.dumps(current, indent=2), encoding="utf-8")
        self._audit("UPDATE_SETTINGS", json.dumps(payload, ensure_ascii=False))
        return current

    def get_home(self) -> Dict[str, Any]:
        modules = self.get_modules()
        monitor = self.get_monitor()
        warnings = self._recent_errors()
        recent_actions = []
        if self.audit_file.exists():
            lines = self.audit_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            recent_actions = lines[-20:]
        return {
            "system_status": "online",
            "active_modules": [m for m in modules if m["status"] == "active"],
            "recent_actions": recent_actions,
            "warnings": warnings,
            "personality_mode": self.get_settings().get("personality_mode", "strategic"),
            "quick_actions": ["start_all", "stop_all", "refresh_monitor", "open_logs"],
            "monitor": monitor,
        }

    async def ws_snapshot(self) -> Dict[str, Any]:
        return {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "home": self.get_home(),
            "modules": self.get_modules(),
            "monitor": self.get_monitor(),
        }

    async def periodic_snapshots(self):
        while True:
            yield await self.ws_snapshot()
            await asyncio.sleep(2)
