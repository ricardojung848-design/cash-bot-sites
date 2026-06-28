import { createHash, timingSafeEqual } from "node:crypto";
import { cookies } from "next/headers";
import { NextResponse } from "next/server";

export const OWNER = "RICO" as const;
export const OWNER_PRIORITY = "MAX" as const;
export const SYSTEM_STATE_LOCKED = "LOCKED" as const;
export const SYSTEM_STATE_UNLOCKED = "UNLOCKED" as const;
export const START_CODE_HASH = "318aee3fed8c9d040d35a7fc1fa776fb31303833aa2de885354ddf3d44d8fb69";

export const AUTH_COOKIE = "cashbot_owner_session";

const AUTH_COOKIE_VALUE = `${OWNER}:${SYSTEM_STATE_UNLOCKED}`;
const LOCKOUT_THRESHOLD = 3;
const LOCKOUT_DURATION_MS = 10 * 60 * 1000;
const SESSION_MAX_AGE_SECONDS = 60 * 60 * 8;

type SystemState = typeof SYSTEM_STATE_LOCKED | typeof SYSTEM_STATE_UNLOCKED;

interface GateState {
  failedAttempts: number;
  lockUntil: number | null;
}

interface StartCodeValidationResult {
  ok: boolean;
  state: SystemState;
  message?: string;
  lockUntil?: number | null;
}

const gateState: GateState = {
  failedAttempts: 0,
  lockUntil: null,
};

const hashStartCode = (startCode: string) => createHash("sha256").update(startCode, "utf8").digest("hex");

const safeHashCompare = (hashA: string, hashB: string) => {
  if (hashA.length !== hashB.length) {
    return false;
  }
  return timingSafeEqual(Buffer.from(hashA, "hex"), Buffer.from(hashB, "hex"));
};

const isLockedNow = () => {
  if (!gateState.lockUntil) {
    return false;
  }
  if (Date.now() >= gateState.lockUntil) {
    gateState.lockUntil = null;
    gateState.failedAttempts = 0;
    return false;
  }
  return true;
};

export const verifyStartCode = (startCode: string): StartCodeValidationResult => {
  if (isLockedNow()) {
    return {
      ok: false,
      state: SYSTEM_STATE_LOCKED,
      message: "System gesperrt.\nBitte später erneut versuchen.",
      lockUntil: gateState.lockUntil,
    };
  }

  const incomingHash = hashStartCode(startCode);
  const valid = safeHashCompare(incomingHash, START_CODE_HASH);

  if (valid) {
    gateState.failedAttempts = 0;
    gateState.lockUntil = null;
    return { ok: true, state: SYSTEM_STATE_UNLOCKED };
  }

  gateState.failedAttempts += 1;
  if (gateState.failedAttempts >= LOCKOUT_THRESHOLD) {
    gateState.lockUntil = Date.now() + LOCKOUT_DURATION_MS;
    return {
      ok: false,
      state: SYSTEM_STATE_LOCKED,
      message: "System gesperrt.\nBitte später erneut versuchen.",
      lockUntil: gateState.lockUntil,
    };
  }

  return { ok: false, state: SYSTEM_STATE_LOCKED, message: "Start-Code ungültig." };
};

export const setUnlockedSessionCookie = (response: NextResponse) => {
  response.cookies.set(AUTH_COOKIE, AUTH_COOKIE_VALUE, {
    httpOnly: true,
    secure: false,
    sameSite: "lax",
    path: "/",
    maxAge: SESSION_MAX_AGE_SECONDS,
  });
};

export const getSystemState = async (): Promise<SystemState> => {
  const cookieStore = await cookies();
  return cookieStore.get(AUTH_COOKIE)?.value === AUTH_COOKIE_VALUE ? SYSTEM_STATE_UNLOCKED : SYSTEM_STATE_LOCKED;
};

export const isAuthenticated = async () => {
  return (await getSystemState()) === SYSTEM_STATE_UNLOCKED;
};
