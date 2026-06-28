# Cash Bot Sites - Automation & Monetization Stack

Dieses Repository bündelt zwei Bereiche:

1. **Website-/Landing-Assets** im Projekt-Root
2. **`Cash_Bot/` Backend-Orchestrierung** für Content, Publishing, Tracking und Monetization

## Projektstruktur

```text
.
├── module/                     # Content/Monetization Python-Module
├── Cash_Bot/                   # AEGIS/Cash_Bot Runtime
│   ├── core/                   # Core Agents
│   ├── modules/                # Erweiterungs-Module + Engines
│   ├── doctor_core/            # Doctor Runtime Services
│   ├── config/                 # Laufzeit-Konfiguration
│   ├── docs/                   # Auto-Doku-Ausgabe
│   └── generated_content/      # Laufzeit-Artefakte
├── generated_content/          # Pipeline-Artefakte (Root-Module)
├── dashboard.html
├── revenue_dashboard.html
└── biolink_cashbot.html
```

## Schnellstart

```bash
python -m pip install -r requirements.txt
python module/Modul_MasterOrchestrator.py
```

Optional (Monetization):

```bash
python module/Modul_MonetizationController.py
```

## Konfiguration

- Root-Monetization-Defaults: `monetization_config.json`
- Cash_Bot-Config: `Cash_Bot/config/cashbot_config.json`
- Secrets ausschließlich via Umgebungsvariablen (siehe `Cash_Bot/.env.example`)

## Tests

```bash
python Cash_Bot/test_core_systems.py
python -m unittest discover -s tests -p "test_*.py"
```
