import { NextResponse } from "next/server";
import { getSystemState, isAuthenticated, OWNER, OWNER_PRIORITY } from "@/lib/auth";

export async function GET() {
  const state = await getSystemState();
  const authed = await isAuthenticated();
  if (!authed) {
    return NextResponse.json({ authenticated: false, state, owner: "Rico" }, { status: 401 });
  }
  return NextResponse.json({ authenticated: true, owner: "Rico", ownerFlag: OWNER, ownerPriority: OWNER_PRIORITY, state });
}
