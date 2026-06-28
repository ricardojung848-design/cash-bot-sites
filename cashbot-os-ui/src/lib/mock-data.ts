import type { InboxEntry, KpiItem, LiveEvent } from "@/types/cashbot";

export const mockKpis: KpiItem[] = [
  { key: "umsatz", titel: "Umsatz heute / Woche / Monat", wert: "3.420 / 19.870 / 87.400 EUR", trend: "+9,8 %", trendRichtung: "steigend" },
  { key: "rpi", titel: "Revenue per Idea", wert: "1.240 EUR", trend: "+6,8 %", trendRichtung: "steigend" },
  { key: "cpt", titel: "Cost per Task", wert: "42 EUR", trend: "-4,2 %", trendRichtung: "fallend" },
  { key: "approval", titel: "Approval Rate", wert: "91,2 %", trend: "+2,7 %", trendRichtung: "steigend" },
  { key: "success", titel: "Task Success Rate", wert: "96,5 %", trend: "+1,9 %", trendRichtung: "steigend" },
  { key: "hallucination", titel: "Hallucination Rate", wert: "1,8 %", trend: "-0,6 %", trendRichtung: "fallend" },
  { key: "ttc", titel: "Time to Completion", wert: "2h 14m", trend: "-7,3 %", trendRichtung: "fallend" },
];

export const initialInboxEntries: InboxEntry[] = [
  {
    id: "in-1",
    titel: "Neue Hook-Idee für LinkedIn-Serie",
    typ: "Idee",
    eventType: "idea.created",
    beschreibung: "Kurzformat-Idee mit hoher Relevanz für CEO-Zielgruppe und direktem CTA zur Terminbuchung.",
    status: "Wartend",
    timestamp: "2026-06-28T00:34:00.000Z",
  },
  {
    id: "in-2",
    titel: "Cluster-Analyse: KI-Automation DACH",
    typ: "Research",
    eventType: "research.result",
    beschreibung: "Research-Ergebnis mit drei priorisierten Chancenclustern und vorgeschlagener Veröffentlichungsreihenfolge.",
    status: "In Prüfung",
    timestamp: "2026-06-27T22:10:00.000Z",
  },
  {
    id: "in-3",
    titel: "Landingpage-Entwurf: Angebot Pipeline 1",
    typ: "Content",
    eventType: "content.draft",
    beschreibung: "Content-Entwurf mit Value Proposition, CTA-Struktur und geprüftem Ton in CEO-Ansprache.",
    status: "Wartend",
    timestamp: "2026-06-27T20:42:00.000Z",
  },
  {
    id: "in-4",
    titel: "Monetarisierungs-Vorschlag für Upsell-Stufe",
    typ: "Monetization",
    eventType: "monetization.suggestion",
    beschreibung: "Vorschlag zur Preisstruktur-Anpassung mit hoher Auswirkung auf Conversion und Durchschnittsumsatz.",
    status: "Kritisch",
    timestamp: "2026-06-26T18:25:00.000Z",
  },
  {
    id: "in-5",
    titel: "Self-Repair-Patch für Publisher-Queue",
    typ: "Repair",
    eventType: "repair.patch",
    beschreibung: "Automatisch generierter Patch zur Stabilisierung der Queue-Reihenfolge bei hoher Last im Publisher.",
    status: "In Prüfung",
    timestamp: "2026-06-28T00:12:00.000Z",
  },
];

export const mockLiveEvents: LiveEvent[] = [
  { type: "idea.created", timestamp: "2026-06-28T00:50:00.000Z", message: "Neue Idee wurde erfasst." },
  { type: "task.assigned", timestamp: "2026-06-28T00:49:00.000Z", message: "Aufgabe einem Worker zugewiesen." },
  { type: "task.completed", timestamp: "2026-06-28T00:47:00.000Z", message: "Aufgabe erfolgreich abgeschlossen." },
  { type: "audit.logged", timestamp: "2026-06-28T00:45:00.000Z", message: "Audit-Eintrag wurde protokolliert." },
];
