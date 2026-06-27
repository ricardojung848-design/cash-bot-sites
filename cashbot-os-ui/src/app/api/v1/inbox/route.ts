import { NextResponse } from "next/server";
import { isAuthenticated } from "@/lib/auth";
import { inboxStore } from "@/lib/store";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  if (!(await isAuthenticated())) {
    return NextResponse.json({ error: "Nicht autorisiert." }, { status: 401 });
  }

  const { searchParams } = new URL(request.url);
  const type = searchParams.get("type");
  const status = searchParams.get("status");
  const from = searchParams.get("from");

  const filtered = inboxStore.filter((entry) => {
    const typePass = !type || type === "alle" || entry.typ === type;
    const statusPass = !status || status === "alle" || entry.status === status;
    const datePass = !from || entry.timestamp >= `${from}T00:00:00.000Z`;
    return typePass && statusPass && datePass;
  });

  return NextResponse.json({ items: filtered });
}
