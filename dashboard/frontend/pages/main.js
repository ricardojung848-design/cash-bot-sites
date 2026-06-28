const state = {
  modules: [],
  currentTab: "home",
  ws: null,
};

function json(v) {
  return JSON.stringify(v, null, 2);
}

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(txt || `HTTP ${res.status}`);
  }
  return res.json();
}

function setTab(tab) {
  state.currentTab = tab;
  document.querySelectorAll("[data-tab]").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.tab === tab);
  });
  document.querySelectorAll("main section").forEach((sec) => sec.classList.add("hidden"));
  document.getElementById(`tab-${tab}`).classList.remove("hidden");
  const titles = {
    home: "Hauptübersicht",
    modules: "Module-Center",
    tasks: "Task-Manager",
    memory: "Memory-Center",
    monitor: "System-Monitor",
    settings: "Einstellungen",
  };
  document.getElementById("page-title").textContent = titles[tab];
}

function statusClass(status) {
  return {
    active: "status-active",
    inactive: "status-inactive",
    failed: "status-failed",
    completed: "status-completed",
  }[status] || "status-inactive";
}

async function loadHome() {
  const d = await api("/api/home");
  document.getElementById("home-status").textContent = d.system_status;
  document.getElementById("home-active-count").textContent = d.active_modules.length;
  document.getElementById("home-warning-count").textContent = d.warnings.length;
  document.getElementById("home-personality").textContent = d.personality_mode;
  document.getElementById("home-actions").textContent = d.recent_actions.join("\n") || "Keine Aktionen";
  document.getElementById("home-warnings").textContent = d.warnings.join("\n") || "Keine Warnungen";
}

async function loadModules() {
  const d = await api("/api/modules");
  state.modules = d.items;
  const tbody = document.getElementById("modules-body");
  tbody.innerHTML = "";
  d.items.forEach((m) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${m.name}</td>
      <td>${m.type}</td>
      <td class="${statusClass(m.status)}">${m.status}</td>
      <td>
        <button class="btn" data-start="${m.id}">Start</button>
        <button class="btn btn-danger" data-stop="${m.id}">Stop</button>
      </td>
      <td><button class="btn" data-log="${m.id}">Log</button></td>
    `;
    tbody.appendChild(tr);
  });
}

async function loadTasks() {
  const d = await api("/api/tasks");
  document.getElementById("tasks-running").textContent = json(d.running);
  document.getElementById("tasks-scheduled").textContent = json(d.scheduled);
  document.getElementById("tasks-history").textContent = json(d.history);
  document.getElementById("tasks-errors").textContent = json(d.errors);
}

async function loadMemory() {
  const d = await api("/api/memory");
  document.getElementById("memory-short").textContent = json(d.short_term);
  document.getElementById("memory-long").textContent = json(d.long_term);
  document.getElementById("memory-docs").textContent = json(d.documents);
  document.getElementById("memory-feedback").textContent = json(d.feedback_history);
}

async function loadMonitor() {
  const d = await api("/api/monitor");
  document.getElementById("mon-cpu").textContent = `${d.cpu_percent}%`;
  document.getElementById("mon-ram").textContent = `${d.ram_percent}%`;
  document.getElementById("mon-sent").textContent = `${d.network.sent_mb} MB`;
  document.getElementById("mon-recv").textContent = `${d.network.recv_mb} MB`;
  document.getElementById("mon-procs").textContent = json(d.processes);
  document.getElementById("mon-bg").textContent = json(d.background_services);
}

async function loadSettings() {
  const d = await api("/api/settings");
  document.getElementById("settings-json").textContent = json(d);
}

async function refreshAll() {
  await Promise.all([loadHome(), loadModules(), loadTasks(), loadMemory(), loadMonitor(), loadSettings()]);
}

function connectWs() {
  const protocol = location.protocol === "https:" ? "wss" : "ws";
  state.ws = new WebSocket(`${protocol}://${location.host}/ws/status`);
  state.ws.onopen = () => {
    document.getElementById("live-badge").textContent = "Live: verbunden";
  };
  state.ws.onclose = () => {
    document.getElementById("live-badge").textContent = "Live: getrennt";
    setTimeout(connectWs, 1200);
  };
  state.ws.onmessage = (ev) => {
    const d = JSON.parse(ev.data);
    document.getElementById("home-active-count").textContent = d.home.active_modules.length;
    document.getElementById("home-warning-count").textContent = d.home.warnings.length;
    document.getElementById("mon-cpu").textContent = `${d.monitor.cpu_percent}%`;
    document.getElementById("mon-ram").textContent = `${d.monitor.ram_percent}%`;
  };
}

document.addEventListener("click", async (ev) => {
  const t = ev.target;
  if (t.dataset.tab) setTab(t.dataset.tab);
  if (t.dataset.start) {
    await api(`/api/modules/${t.dataset.start}/start`, { method: "POST" });
    await loadModules();
  }
  if (t.dataset.stop) {
    await api(`/api/modules/${t.dataset.stop}/stop`, { method: "POST" });
    await loadModules();
  }
  if (t.dataset.log) {
    const d = await api(`/api/modules/${t.dataset.log}/logs`);
    alert(d.content || "Kein Log vorhanden.");
  }
});

document.getElementById("btn-start-all").addEventListener("click", async () => {
  await api("/api/modules/start-all", { method: "POST" });
  await loadModules();
});

document.getElementById("btn-stop-all").addEventListener("click", async () => {
  await api("/api/modules/stop-all", { method: "POST" });
  await loadModules();
});

document.getElementById("btn-refresh-home").addEventListener("click", refreshAll);

document.getElementById("btn-settings-save").addEventListener("click", async () => {
  await api("/api/settings", {
    method: "PATCH",
    body: JSON.stringify({ theme: "dark-neon", language: "de" }),
  });
  await loadSettings();
});

(async () => {
  setTab("home");
  await refreshAll();
  connectWs();
})();
