import { NextResponse } from "next/server";
import { isAuthenticated } from "@/lib/auth";
import { mockLiveEvents } from "@/lib/mock-data";

export async function GET() {
  if (!(await isAuthenticated())) {
    return NextResponse.json({ error: "Nicht autorisiert." }, { status: 401 });
  }
  return NextResponse.json({ events: mockLiveEvents });
}
