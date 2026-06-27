import { NextResponse } from "next/server";
import { AUTH_COOKIE, loginValid } from "@/lib/auth";

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const username = String(body.username ?? "");
  const password = String(body.password ?? "");

  if (!loginValid(username, password)) {
    return NextResponse.json({ error: "Ungültige Zugangsdaten." }, { status: 401 });
  }

  const response = NextResponse.json({ ok: true, name: "Rico" });
  response.cookies.set(AUTH_COOKIE, "ok", {
    httpOnly: true,
    secure: false,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 8,
  });
  return response;
}
