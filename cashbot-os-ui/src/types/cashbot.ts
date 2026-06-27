export type InboxTyp = "Idee" | "Research" | "Content" | "Monetization" | "Repair";
export type InboxStatus = "Wartend" | "In Prüfung" | "Kritisch" | "Freigegeben" | "Abgelehnt" | "Sandbox";

export type InboxEventType =
  | "idea.created"
  | "research.result"
  | "content.draft"
  | "monetization.suggestion"
  | "repair.patch";

export interface KpiItem {
  key: string;
  titel: string;
  wert: string;
  trend: string;
  trendRichtung: "steigend" | "fallend";
}

export interface InboxEntry {
  id: string;
  titel: string;
  typ: InboxTyp;
  eventType: InboxEventType;
  beschreibung: string;
  status: InboxStatus;
  timestamp: string;
}

export interface LiveEvent {
  type: string;
  timestamp: string;
  message: string;
}
