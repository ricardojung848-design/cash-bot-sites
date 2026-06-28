import { NextResponse } from "next/server";
import { isAuthenticated } from "@/lib/auth";

export async function GET(request: Request) {
  if (!(await isAuthenticated())) {
    return NextResponse.json({ error: "Nicht autorisiert." }, { status: 401 });
  }
  const url = new URL(request.url);
  const proto = url.protocol === "https:" ? "wss" : "ws";
  return NextResponse.json({ url: `${proto}://${url.host}/api/v1/events/ws` });
}
