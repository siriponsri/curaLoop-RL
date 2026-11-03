import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
export function number(value: number | null | undefined, digits = 0) {
  return value == null
    ? "—"
    : new Intl.NumberFormat("en-US", { maximumFractionDigits: digits }).format(
        value,
      );
}
export function short(value: string, length = 10) {
  return value.length > length ? value.slice(0, length) + "…" : value;
}
// Browser preferences are conveniences; blocked/full storage must not prevent
// access to the durable local server or portable JSON recovery.
export function readPreference(key: string): string | null {
  try { return localStorage.getItem(key); } catch { return null; }
}
export function writePreference(key: string, value: string): void {
  try { localStorage.setItem(key, value); } catch { /* Server state remains durable. */ }
}
export function removePreference(key: string): void {
  try { localStorage.removeItem(key); } catch { /* Browser persistence is optional. */ }
}
