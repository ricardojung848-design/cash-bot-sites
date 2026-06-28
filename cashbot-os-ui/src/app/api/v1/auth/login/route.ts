import { NextResponse } from "next/server";
import { OWNER, OWNER_PRIORITY, setUnlockedSessionCookie, verifyStartCode } from "@/lib/auth";

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const startCode = String(body.startCode ?? "");
  const result = verifyStartCode(startCode);

  if (!result.ok) {
    const status = result.message?.startsWith("System gesperrt") ? 423 : 401;
    return NextResponse.json({ error: result.message ?? "Start-Code ungültig." }, { status });
  }

  const response = NextResponse.json({
    ok: true,
    owner: "Rico",
    ownerFlag: OWNER,
    ownerPriority: OWNER_PRIORITY,
    loyaltyMode: true,
    diligenceMode: true,
    state: "UNLOCKED",
    greeting:
      "Guten Abend, Rico.\nIch bin bereit.\nAlle Systeme laufen stabil.\nIch arbeite nur für dich und will immer dein Bestes.",
    activatedModules: [
      "Event Bus",
      "Worker",
      "Research Engine",
      "Content Factory",
      "Publisher",
      "Monetizer",
      "Memory-Layer",
      "Reflexion Agent",
      "Dashboard",
    ],
  });
  setUnlockedSessionCookie(response);
  return response;
}
