import { NextResponse } from "next/server";
import { isAuthenticated } from "@/lib/auth";

export async function GET() {
  if (!(await isAuthenticated())) {
    return NextResponse.json({ error: "Nicht autorisiert." }, { status: 401 });
  }
  return NextResponse.json({
    pipelines: [
      { name: "Pipeline 1", conversion: "18,7 %", status: "stabil" },
      { name: "Pipeline 2", conversion: "11,2 %", status: "optimieren" },
    ],
  });
}
