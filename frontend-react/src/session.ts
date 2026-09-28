import type { Session } from "./types";
const KEY = "vetai.session.v3";
export const loadSession = (): Session | null => {
  try {
    return JSON.parse(sessionStorage.getItem(KEY) || "null");
  } catch {
    return null;
  }
};
export const saveSession = (value: Session | null) =>
  value
    ? sessionStorage.setItem(KEY, JSON.stringify(value))
    : sessionStorage.removeItem(KEY);
