from pathlib import Path
import time
from typing import Any, Dict, List
from doctor_core.logging import log_doctor


class WorkerOptimizer:
    """
    MEGA-PRO-Version:
    - Steuert und optimiert die Task-Verteilung aller Worker
    - Überwacht API-Durchsatz und Latenzen (speziell für Telegram/Social-Module)
    - Speichert Optimierungs-Metriken im SQLite-Langzeitgedächtnis
    - Passt Worker-Intervalle dynamisch an die Systemlast an
    """

    def __init__(self, engine_manager: Any = None):
        self.engines = engine_manager
        self.base_dir = Path(__file__).resolve().parent.parent
        
        # Performance-Metriken im RAM halten, bevor sie persistiert werden
        self.metrics_cache: Dict[str, List[float]] = {
            "telegram_response_time": [],
            "pipeline_execution_time": []
        }

    def run_optimization_cycle(self) -> bool:
        """Der zentrale Optimierungs-Lauf, der vom BackgroundMonitor aufgerufen wird."""
        log_doctor("WorkerOptimizer: Starte autonomen Optimierungs- und Analysezyklus.")
        
        # 1. Analysiere bestehende Fehler aus der Memory-Engine
        has_critical_load = self._analyze_system_load()
        
        # 2. Telegram-Bot-spezifische Struktur optimieren
        telegram_ok = self.optimize_telegram_pipeline(has_critical_load)
        
        return telegram_ok

    def log_metric(self, metric_key: str, value: float):
        """Erlaubt es anderen Modulen (z.B. telegram_bot.py), Latenzen zu loggen."""
        if metric_key in self.metrics_cache:
            self.metrics_cache[metric_key].append(value)
            if len(self.metrics_cache[metric_key]) >= 5: # Alle 5 Messungen in DB schreiben
                self._persist_metrics(metric_key)

    def _analyze_system_load(self) -> bool:
        """Prüft die Fehlerhistorie in der DB, um bei Überlastung Worker zu drosseln."""
        if self.engines and self.engines.has("state"):
            try:
                state = self.engines.get("state")
                unfixed_errors = state.get_unfixed_errors()
                
                # Wenn mehr als 3 ungelöste Fehler vorliegen, gilt das System als überlastet
                if len(unfixed_errors) > 3:
                    log_doctor(f"WorkerOptimizer: Hohe Systemlast erkannt ({len(unfixed_errors)} offene Fehler). Safe-Mode empfohlen.")
                    return True
            except Exception as e:
                log_doctor(f"WorkerOptimizer: Fehler beim Lesen der Systemlast: {e}")
        return False

    def optimize_telegram_pipeline(self, reduce_load: bool) -> bool:
        """
        Analysiert die Queue und passt das Verhalten der Telegram-Engines an.
        Verhindert aktiv '429 Too Many Requests' Fehler von der Telegram API.
        """
        log_doctor("WorkerOptimizer: Analysiere Telegram-Bot-Schnittstellen...")
        
        avg_latency = 0.0
        times = self.metrics_cache["telegram_response_time"]
        if times:
            avg_latency = sum(times) / len(times)
            log_doctor(f"WorkerOptimizer: Mittlere Telegram-Latenz beträgt {avg_latency:.2f}s.")

        # Dynamische Anpassung des Intervalls im Scheduler, falls verfügbar
        if self.engines and self.engines.has("state"):
            try:
                state = self.engines.get("state")
                old_metrics = state.get_state("optimizer_plan", {})
                
                # Zielwert-Berechnung für den nächsten Interval-Schritt
                suggested_delay = 2.0 if reduce_load or avg_latency > 1.5 else 0.5
                
                optimization_entry = {
                    "last_update": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "telegram_target_delay": suggested_delay,
                    "system_status": "DREGULATED" if reduce_load else "STABLE",
                    "average_latency": avg_latency
                }
                
                state.set_state("optimizer_plan", optimization_entry)
                log_doctor(f"WorkerOptimizer: Telegram-Pipeline optimiert. Ziel-Delay gesetzt auf: {suggested_delay}s.")
                
                # Historischen Eintrag in die relationale DB schreiben
                with state._get_connection() as conn:
                    conn.execute("""
                        INSERT INTO optimization_history (module_name, metric_improved, old_value, new_value, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                    """, ("telegram_bot", "target_delay", old_metrics.get("telegram_target_delay", 0.0), suggested_delay, time.strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()

            except Exception as e:
                log_doctor(f"WorkerOptimizer: Fehler beim Speichern des Optimierungsplans: {e}")
                return False

        return True

    def _persist_metrics(self, metric_key: str):
        """Schreibt gesammelte RAM-Metriken komprimiert in die SQLite-Statistiktabelle."""
        if not self.engines or not self.engines.has("state"):
            return
            
        times = self.metrics_cache[metric_key]
        if not times:
            return
            
        avg_value = sum(times) / len(times)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            state = self.engines.get("state")
            with state._get_connection() as conn:
                conn.execute("""
                    INSERT INTO social_stats (platform, metric_key, metric_value, timestamp)
                    VALUES (?, ?, ?, ?)
                """, ("telegram", metric_key, avg_value, timestamp))
                conn.commit()
            
            # Cache leeren
            self.metrics_cache[metric_key] = []
            log_doctor(f"WorkerOptimizer: Metrik '{metric_key}' erfolgreich in Langzeit-DB persistiert (Schnittwert: {avg_value:.4f}).")
        except Exception as e:
            log_doctor(f"WorkerOptimizer: Fehler beim Schreiben der Metrik in DB: {e}")