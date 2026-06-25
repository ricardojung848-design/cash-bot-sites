import time
from pathlib import Path

# Core-Komponenten importieren
from doctor_core.logging import log_doctor
from doctor_core.state import DoctorState
from doctor_core.engine_manager import EngineManager
from doctor_core.background import BackgroundMonitor
from doctor_core.system_check import SystemChecker
from doctor_core.auto_fix_engine import AutoFixEngine
from doctor_core.log_analysis import LogAnalyzer
from doctor_core.worker_optimizer import WorkerOptimizer
from doctor_core.voice_engine import VoiceEngine
from doctor_core.brain import Phase5Brain
from doctor_core.module_extender import ModuleExtender
from doctor_core.module_builder import ModuleBuilder
from doctor_core.simulation import Phase6Simulation


def main():
    log_doctor("=== SYSTEMSTART: AGENT DOCTOR ECOSYSTEM ===")

    # 1. Zentralen Engine-Manager (Service Locator) instanziieren
    engines = EngineManager()

    # 2. State-Manager (SQLite-Langzeitgedächtnis) initialisieren & registrieren
    state = DoctorState()
    engines.register("state", state)

    # 3. Infrastruktur & Kern-Engines initialisieren
    checker = SystemChecker(engine_manager=engines)
    engines.register("checker", checker)

    fix_engine = AutoFixEngine(engine_manager=engines)
    engines.register("fix", fix_engine)

    analyzer = LogAnalyzer(engine_manager=engines)
    engines.register("analyzer", analyzer)

    optimizer = WorkerOptimizer(engine_manager=engines)
    engines.register("optimizer", optimizer)

    voice = VoiceEngine(engine_manager=engines)
    engines.register("voice", voice)

    brain = Phase5Brain(engine_manager=engines)
    engines.register("brain", brain)

    extender = ModuleExtender(engine_manager=engines)
    engines.register("extender", extender)

    builder = ModuleBuilder(engine_manager=engines)
    engines.register("builder", builder)

    # 4. Systemintegrität VOR dem Start der Loops prüfen
    if not checker.run():
        log_doctor("CRITICAL: System-Check fehlgeschlagen. Start abgebrochen!")
        return

    # 5. Event-Hooks verknüpfen (Asynchroner Pub/Sub-Zirkel)
    # Die AutoFixEngine lauscht ab jetzt vollautomatisch auf jeden neuen Error!
    engines.subscribe("new_error", fix_engine.handle_error_event)

    # 6. Background-Scheduler aufsetzen und periodische Tasks buchen
    monitor = BackgroundMonitor(engine_manager=engines)
    
    # Task 1: Log-Analyzer läuft alle 10 Sekunden
    monitor.register_task("log_analyzer", analyzer.run, interval_seconds=10)
    
    # Task 2: Worker-Optimizer läuft alle 30 Sekunden
    monitor.register_task("worker_optimizer", optimizer.run_optimization_cycle, interval_seconds=30)
    
    # Task 3: Kognitives Brain-Update läuft alle 15 Sekunden
    monitor.register_task("brain_update", brain.update, interval_seconds=15)

    # Scheduler-Thread starten
    monitor.start()

    # 7. Akustische Begrüßung abfeuern (Thread-sicher über Audio-Queue)
    voice.startup_greeting()

    # 8. Start der Simulation (Phase 6) zur Kontrolle der geladenen Daten
    simulation = Phase6Simulation(engine_manager=engines, state=state)
    simulation.run()

    log_doctor("System ist betriebsbereit und läuft autonom im Hintergrund.")
    
    # Haupt-Thread am Leben erhalten
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log_doctor("System wird durch Benutzer (STRG+C) sauber heruntergefahren.")
        monitor.stop()
        log_doctor("=== SYSTEMBEENDET ===")


if __name__ == "__main__":
    main()