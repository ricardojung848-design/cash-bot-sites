"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

export function LoginForm() {
  const router = useRouter();
  const [username, setUsername] = useState("rico");
  const [password, setPassword] = useState("cashbot-rico-2026");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setPending(true);
    try {
      const response = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.error || "Login fehlgeschlagen.");
      }

      router.push("/");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login fehlgeschlagen.");
    } finally {
      setPending(false);
    }
  };

  return (
    <form onSubmit={onSubmit} className="cb-panel cb-card-enter w-full max-w-md p-6 space-y-4">
      <h1 className="text-2xl font-semibold tracking-tight">Willkommen, Rico.</h1>
      <p className="text-sm text-[var(--muted)]">Bitte einloggen, um das CashBot Command Center zu öffnen.</p>
      <div className="space-y-2">
        <label className="text-sm text-[var(--muted)]" htmlFor="username">
          Benutzername
        </label>
        <input
          id="username"
          className="w-full rounded-md border border-[var(--line)] bg-black/35 px-3 py-2 outline-none focus:border-cyan-300"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
      </div>
      <div className="space-y-2">
        <label className="text-sm text-[var(--muted)]" htmlFor="password">
          Passwort
        </label>
        <input
          id="password"
          type="password"
          className="w-full rounded-md border border-[var(--line)] bg-black/35 px-3 py-2 outline-none focus:border-cyan-300"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>
      {error ? <p className="text-sm text-rose-300">{error}</p> : null}
      <button disabled={pending} className="cb-btn cb-btn-primary w-full disabled:opacity-60">
        {pending ? "Login läuft..." : "Einloggen"}
      </button>
      <p className="text-xs text-[var(--muted)]">
        Hinweis: Für Testzwecke sind die Rico-Credentials im Frontend vordefiniert.
      </p>
    </form>
  );
}
