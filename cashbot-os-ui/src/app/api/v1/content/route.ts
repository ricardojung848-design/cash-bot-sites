import { NextResponse } from "next/server";
import { isAuthenticated } from "@/lib/auth";

export async function GET() {
  if (!(await isAuthenticated())) {
    return NextResponse.json({ error: "Nicht autorisiert." }, { status: 401 });
  }
  return NextResponse.json({
    items: [
      { id: "co-1", titel: "Landingpage Pipeline 1", status: "Entwurf" },
      { id: "co-2", titel: "LinkedIn Beitrag #24", status: "Freigabe ausstehend" },
    ],
  });
}
