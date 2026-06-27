import { NextResponse } from "next/server";
import { isAuthenticated } from "@/lib/auth";

export async function GET() {
  if (!(await isAuthenticated())) {
    return NextResponse.json({ error: "Nicht autorisiert." }, { status: 401 });
  }
  return NextResponse.json({
    items: [
      { id: "id-1", titel: "CEO-Shorts-Serie", prioritaet: "hoch" },
      { id: "id-2", titel: "Offer-Test Pipeline 2", prioritaet: "mittel" },
    ],
  });
}
