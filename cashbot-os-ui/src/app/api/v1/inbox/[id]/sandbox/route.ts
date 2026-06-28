import { NextResponse } from "next/server";
import { isAuthenticated } from "@/lib/auth";
import { updateInboxStatus } from "@/lib/store";

export async function POST(_: Request, context: { params: Promise<{ id: string }> }) {
  if (!(await isAuthenticated())) {
    return NextResponse.json({ error: "Nicht autorisiert." }, { status: 401 });
  }
  const { id } = await context.params;
  const item = updateInboxStatus(id, "Sandbox");
  if (!item) {
    return NextResponse.json({ error: "Eintrag nicht gefunden." }, { status: 404 });
  }
  return NextResponse.json({ ok: true, item });
}
