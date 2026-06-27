import { cookies } from "next/headers";

export const AUTH_COOKIE = "cashbot_rico_session";
const RICO_USER = "rico";
const RICO_PASS = "cashbot-rico-2026";

export const loginValid = (username: string, password: string) => {
  return username.trim().toLowerCase() === RICO_USER && password === RICO_PASS;
};

export const isAuthenticated = async () => {
  const cookieStore = await cookies();
  return cookieStore.get(AUTH_COOKIE)?.value === "ok";
};
