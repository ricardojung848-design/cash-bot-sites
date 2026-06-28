import { NextResponse } from "next/server";
import { isAuthenticated } from "@/lib/auth";
import { getKpisFromModules, getModuleHealth } from "@/lib/module-adapters";

export const dynamic = "force-dynamic";

export async function GET() {
  if (!(await isAuthenticated())) {
    return NextResponse.json({ error: "Nicht autorisiert." }, { status: 401 });
  }

  const [kpis, moduleHealth] = await Promise.all([getKpisFromModules(), getModuleHealth()]);
  return NextResponse.json({ kpis, moduleHealth });
}
