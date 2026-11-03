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
