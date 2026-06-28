import { NextResponse } from "next/server";
import { isAuthenticated } from "@/lib/auth";

export async function GET() {
  if (!(await isAuthenticated())) {
    return NextResponse.json({ error: "Nicht autorisiert." }, { status: 401 });
  }
  return NextResponse.json({
    items: [
      { id: "re-1", thema: "KI-Automation DACH", score: 92 },
      { id: "re-2", thema: "Agentic Workflows", score: 88 },
    ],
  });
}
