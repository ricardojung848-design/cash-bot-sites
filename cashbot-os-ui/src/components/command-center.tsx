"use client";

import { useEffect, useMemo, useState, type ReactNode } from "react";
import type { InboxEntry, KpiItem, LiveEvent } from "@/types/cashbot";
import { de } from "@/config/de";

const navItems = [
  { key: "dashboard", label: "Dashboard" },
  { key: "inbox", label: "Inbox & Freigaben" },
  { key: "ideen", label: "Ideen-Ordner" },
  { key: "research", label: "Research Engine" },
  { key: "factory", label: "Content Factory" },
  { key: "publisher", label: "Publisher" },
  { key: "monetarisierung", label: "Monetarisierung" },
  { key: "revenue", label: "Revenue Tracker" },
  { key: "eventmonitor", label: "Event-Monitor" },
  { key: "audit", label: "Audit Log" },
  { key: "memory", label: "Memory & Reflexion" },
  { key: "doktor", label: "System-Doktor" },
  { key: "settings", label: "Einstellungen / Sandbox / Kill-Switch" },
] as const;

const currentGreeting = () => {
  const hour = new Date().getHours();
  return hour >= 18 || hour < 5 ? "Guten Abend, Rico." : "Hallo Rico.";
};

const formatTimestamp = (iso: string) => new Date(iso).toLocaleString("de-DE", { dateStyle: "short", timeStyle: "short" });

type DecisionAction = "approve" | "reject" | "sandbox";

interface CommandCenterProps {
  initialKpis: KpiItem[];
  initialInboxItems: InboxEntry[];
  initialEvents: LiveEvent[];
  moduleInfo: string;
}

export function CommandCenter({ initialKpis, initialInboxItems, initialEvents, moduleInfo }: CommandCenterProps) {
  const [active, setActive] = useState<(typeof navItems)[number]["key"]>("dashboard");
  const [kpis] = useState<KpiItem[]>(initialKpis);
  const [inboxItems, setInboxItems] = useState<InboxEntry[]>(initialInboxItems);
  const [events, setEvents] = useState<LiveEvent[]>(initialEvents);
  const [filterType, setFilterType] = useState("alle");
  const [filterStatus, setFilterStatus] = useState("alle");
  const [filterDate, setFilterDate] = useState("");
  const statusInfo = `Rico, alle Systeme laufen stabil. Ich arbeite nur für dich. Was möchtest du heute erreichen? (${moduleInfo})`;
  const startupGreeting =
    "Guten Abend, Rico.\nIch bin bereit.\nAlle Systeme laufen stabil.\nIch arbeite nur für dich und will immer dein Bestes.";

  useEffect(() => {
    let socket: WebSocket | null = null;
    const connect = async () => {
      const info = await fetch("/api/v1/events/ws-info", { cache: "no-store" }).then((r) => r.json()).catch(() => null);
      if (!info?.url) return;
      socket = new WebSocket(info.url);
      socket.onmessage = (event) => {
        const payload = JSON.parse(event.data) as LiveEvent;
        setEvents((prev) => [payload, ...prev].slice(0, 20));
      };
    };
    connect();
    return () => socket?.close();
  }, []);

  const doDecision = async (id: string, action: DecisionAction) => {
    const response = await fetch(`/api/v1/inbox/${id}/${action}`, { method: "POST" });
    if (response.ok) {
      const body = await response.json().catch(() => null);
      if (body?.item) {
        setInboxItems((prev) => prev.map((entry) => (entry.id === id ? body.item : entry)));
      }
    }
  };

  const filteredInboxItems = useMemo(() => {
    return inboxItems.filter((entry) => {
      const byType = filterType === "alle" || entry.typ === filterType;
      const byStatus = filterStatus === "alle" || entry.status === filterStatus;
      const byDate = !filterDate || entry.timestamp >= `${filterDate}T00:00:00.000Z`;
      return byType && byStatus && byDate;
    });
  }, [filterDate, filterStatus, filterType, inboxItems]);

  const dashboard = (
    <section className="cb-panel p-5 cb-card-enter">
      <div className="cb-soft-panel p-4 mb-4">
        <p className="text-sm whitespace-pre-line text-cyan-100">{startupGreeting}</p>
      </div>
      <h2 className="text-xl font-semibold mb-2">Dashboard</h2>
      <p className="text-sm text-[var(--muted)] mb-5">{de.untertitel}</p>
      <div className="grid grid-cols-1 xl:grid-cols-[1.8fr_0.9fr] gap-4">
        <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-3">
          {kpis.map((kpi) => (
            <article key={kpi.key} className="cb-soft-panel cb-card-enter p-4">
              <p className="text-sm text-[var(--muted)]">{kpi.titel}</p>
              <p className="text-2xl font-semibold mt-2">{kpi.wert}</p>
              <p className={`text-sm mt-2 ${kpi.trendRichtung === "steigend" ? "text-emerald-300" : "text-rose-300"}`}>
                {kpi.trendRichtung === "steigend" ? "↑" : "↓"} {kpi.trend}
              </p>
            </article>
          ))}
        </div>
        <aside className="cb-soft-panel cb-card-enter p-4">
          <h3 className="font-medium mb-3">Live-Event-Stream</h3>
          <ul className="space-y-2">
            {events.slice(0, 8).map((event, idx) => (
              <li key={`${event.type}-${event.timestamp}-${idx}`} className="border border-[var(--line)] rounded-lg p-2 bg-black/30">
                <code className="text-cyan-200 text-xs">{event.type}</code>
                <p className="text-[11px] text-[var(--muted)]">{formatTimestamp(event.timestamp)}</p>
              </li>
            ))}
          </ul>
        </aside>
      </div>
    </section>
  );

  const inbox = (
    <section className="cb-panel p-5 cb-card-enter">
      <h2 className="text-xl font-semibold mb-2">Inbox & Freigaben</h2>
      <p className="text-[15px] text-cyan-100 mb-4">Rico, diese Aktionen warten auf deine Entscheidung.</p>
      <div className="cb-soft-panel p-3 mb-4 grid sm:grid-cols-2 xl:grid-cols-4 gap-2">
        <select className="rounded-md border border-[var(--line)] bg-black/40 p-2 text-sm" value={filterType} onChange={(e) => setFilterType(e.target.value)}>
          <option value="alle">Typ: Alle</option>
          <option value="Idee">Idee</option>
          <option value="Research">Research</option>
          <option value="Content">Content</option>
          <option value="Monetization">Monetization</option>
          <option value="Repair">Repair</option>
        </select>
        <select className="rounded-md border border-[var(--line)] bg-black/40 p-2 text-sm" value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
          <option value="alle">Status: Alle</option>
          <option value="Wartend">Wartend</option>
          <option value="In Prüfung">In Prüfung</option>
          <option value="Kritisch">Kritisch</option>
          <option value="Freigegeben">Freigegeben</option>
          <option value="Abgelehnt">Abgelehnt</option>
          <option value="Sandbox">Sandbox</option>
        </select>
        <input type="date" className="rounded-md border border-[var(--line)] bg-black/40 p-2 text-sm" value={filterDate} onChange={(e) => setFilterDate(e.target.value)} />
        <button
          className="cb-btn"
          onClick={() => {
            setFilterType("alle");
            setFilterStatus("alle");
            setFilterDate("");
          }}
        >
          Filter zurücksetzen
        </button>
      </div>

      <div className="space-y-3">
        {filteredInboxItems.map((item) => (
          <article key={item.id} className="cb-soft-panel p-4 cb-card-enter">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
              <h3 className="font-medium">{item.titel}</h3>
              <span className="cb-badge">{item.eventType}</span>
            </div>
            <div className="flex flex-wrap gap-2 mt-2">
              <span className="cb-badge">Typ: {item.typ}</span>
              <span className="cb-badge">Status: {item.status}</span>
              <span className="cb-badge">Zeit: {formatTimestamp(item.timestamp)}</span>
            </div>
            <p className="text-sm text-[var(--muted)] mt-2">{item.beschreibung}</p>
            <div className="flex flex-wrap gap-2 mt-3">
              <button className="cb-btn cb-btn-primary" onClick={() => doDecision(item.id, "approve")}>
                Freigeben
              </button>
              <button className="cb-btn" onClick={() => doDecision(item.id, "reject")}>
                Ablehnen
              </button>
              <button className="cb-btn" onClick={() => doDecision(item.id, "sandbox")}>
                In Sandbox testen
              </button>
              <button className="cb-btn">Details anzeigen</button>
            </div>
          </article>
        ))}
        {filteredInboxItems.length === 0 ? <p className="text-sm text-[var(--muted)]">Keine Einträge für die gewählten Filter gefunden.</p> : null}
      </div>
    </section>
  );

  const placeholders = useMemo(
    () =>
      navItems
        .filter((item) => !["dashboard", "inbox"].includes(item.key))
        .reduce<Record<string, ReactNode>>((acc, item) => {
          acc[item.key] = (
            <section className="cb-panel p-5 cb-card-enter" key={item.key}>
              <h2 className="text-xl font-semibold mb-2">{item.label}</h2>
              <p className="text-sm text-[var(--muted)]">
                Dieser Bereich ist im Next.js-Stack angebunden. Datenquellen laufen über `/api/v1/{item.key}` und die Adapter-Schicht zum
                Orchestrator/Event-Bus.
              </p>
            </section>
          );
          return acc;
        }, {}),
    [],
  );

  return (
    <div className="grid min-h-screen lg:grid-cols-[300px_1fr]">
      <aside className="border-r border-[var(--line)] bg-black/35 backdrop-blur-md p-4">
        <h2 className="text-xl font-semibold mb-4">
          CashBot OS <span className="text-violet-300">Rico Edition</span>
        </h2>
        <nav className="flex flex-col gap-2">
          {navItems.map((item) => (
            <button
              key={item.key}
              onClick={() => setActive(item.key)}
              className={`text-left rounded-lg px-3 py-2 border transition ${
                active === item.key
                  ? "border-cyan-300/50 bg-gradient-to-r from-cyan-400/20 to-violet-400/20 cb-glow-cyan"
                  : "border-transparent hover:border-cyan-300/30 hover:bg-cyan-300/10"
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </aside>
      <main className="p-5 lg:p-8">
        <header className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-2 mb-5">
          <div>
            <h1 className="text-4xl font-semibold tracking-tight">{currentGreeting()}</h1>
            <p className="text-sm text-[var(--muted)] mt-1">{de.untertitel}</p>
          </div>
          <p className="text-sm text-cyan-100 lg:max-w-xl">{statusInfo}</p>
        </header>
        {active === "dashboard" ? dashboard : null}
        {active === "inbox" ? inbox : null}
        {placeholders[active]}
      </main>
    </div>
  );
}
