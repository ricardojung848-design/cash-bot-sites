import type { InboxEntry } from "@/types/cashbot";
import { initialInboxEntries } from "@/lib/mock-data";

const globalForStore = globalThis as unknown as {
  cashbotInboxStore?: InboxEntry[];
};

if (!globalForStore.cashbotInboxStore) {
  globalForStore.cashbotInboxStore = [...initialInboxEntries];
}

export const inboxStore = globalForStore.cashbotInboxStore;

export const updateInboxStatus = (id: string, status: InboxEntry["status"]): InboxEntry | null => {
  const item = inboxStore.find((entry) => entry.id === id);
  if (!item) {
    return null;
  }
  item.status = status;
  return item;
};
