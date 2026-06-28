"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

export function LoginForm() {
  const router = useRouter();
  const [startCode, setStartCode] = useState("");
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
        body: JSON.stringify({ startCode }),
      });

      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.error || "Start-Code ungültig.");
      }

      router.push("/");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Start-Code ungültig.");
    } finally {
      setPending(false);
    }
  };

  return (
    <form onSubmit={onSubmit} className="cb-panel cb-card-enter w-full max-w-md p-6 space-y-4">
      <h1 className="text-2xl font-semibold tracking-tight">Bitte Start-Code eingeben.</h1>
      <div className="space-y-2">
        <label className="text-sm text-[var(--muted)]" htmlFor="start-code">
          Start-Code
        </label>
        <input
          id="start-code"
          type="password"
          inputMode="numeric"
          className="w-full rounded-md border border-[var(--line)] bg-black/35 px-3 py-2 outline-none focus:border-cyan-300"
          value={startCode}
          onChange={(e) => setStartCode(e.target.value)}
          autoComplete="off"
        />
      </div>
      {error ? <p className="text-sm text-rose-300">{error}</p> : null}
      <button disabled={pending} className="cb-btn cb-btn-primary w-full disabled:opacity-60">
        {pending ? "System startet..." : "System starten"}
      </button>
    </form>
  );
}
