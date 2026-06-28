import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { mockKpis } from "@/lib/mock-data";

const execFileAsync = promisify(execFile);

const moduleMap = {
  orchestrator: "Modul_MasterOrchestrator",
  revenue: "Modul_RevenueTracker",
  monetization: "Modul_MonetizationController",
  eventBus: "Event Bus",
};

const runPythonAdapter = async (command: string) => {
  const scriptPath = "..\\Cash_Bot\\module_adapter.py";
  try {
    const { stdout } = await execFileAsync("python", [scriptPath, command], {
      cwd: process.cwd(),
      timeout: 2500,
    });
    return JSON.parse(stdout);
  } catch {
    return null;
  }
};

export const getKpisFromModules = async () => {
  const data = await runPythonAdapter("kpis");
  if (Array.isArray(data)) {
    return data;
  }
  return mockKpis;
};

export const getModuleHealth = async () => ({
  status: "ok",
  modules: moduleMap,
  info: "Adapter-Schicht aktiv. Bei vorhandenen Python-Adaptern werden Live-Daten gelesen, sonst Testdaten.",
});
