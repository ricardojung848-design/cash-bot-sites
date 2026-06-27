import { redirect } from "next/navigation";
import { isAuthenticated } from "@/lib/auth";
import { CommandCenter } from "@/components/command-center";
import { getKpisFromModules, getModuleHealth } from "@/lib/module-adapters";
import { inboxStore } from "@/lib/store";
import { mockLiveEvents } from "@/lib/mock-data";

export default async function Home() {
  if (!(await isAuthenticated())) {
    redirect("/login");
  }

  const [kpis, moduleHealth] = await Promise.all([getKpisFromModules(), getModuleHealth()]);

  return (
    <CommandCenter
      initialKpis={kpis}
      initialInboxItems={[...inboxStore]}
      initialEvents={[...mockLiveEvents]}
      moduleInfo={moduleHealth.info}
    />
  );
}
