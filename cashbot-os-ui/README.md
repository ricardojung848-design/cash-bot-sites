# CashBot OS UI (Next.js)

UI-Umsetzung für **CashBot OS – Rico Edition** mit:

- Next.js (App Router)
- TailwindCSS
- WebSocket-Test-Stream
- API-Routen unter `/api/v1/*`
- Einfache Rico-Authentifizierung

## Start

```bash
npm install
npm run dev
```

Anwendung läuft auf `http://localhost:3000`.

## Start-Code-Schutz

- Beim Start ist das System standardmäßig im Zustand `LOCKED`.
- Die UI zeigt zunächst nur den Start-Code-Eingang.
- Der Start-Code wird serverseitig ausschließlich als SHA-256-Hash geprüft.

## API-Übersicht

- `GET /api/v1/kpis`
- `GET /api/v1/inbox?type=&status=&from=`
- `POST /api/v1/inbox/:id/approve`
- `POST /api/v1/inbox/:id/reject`
- `POST /api/v1/inbox/:id/sandbox`
- `GET /api/v1/ideas`
- `GET /api/v1/research`
- `GET /api/v1/content`
- `GET /api/v1/monetization`
- `GET /api/v1/events`
- `GET /api/v1/events/ws-info`
- WebSocket: `/api/v1/events/ws`

## Modul-Anbindung

Die Adapter-Schicht referenziert:

- `Modul_MasterOrchestrator`
- `Modul_RevenueTracker`
- `Modul_MonetizationController`
- Event Bus

Wenn kein Python-Adapter verfügbar ist, werden automatisch Testdaten verwendet.
