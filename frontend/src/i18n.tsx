import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { readPreference, writePreference } from "./lib";
import thai from "./locales/th.json";

export type Locale = "en" | "th";
type Translator = (text: string, values?: Record<string, string | number>) => string;
const Context = createContext<{ locale: Locale; setLocale: (locale: Locale) => void; t: Translator } | null>(null);
const catalogue: Record<string, string> = thai;

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState<Locale>(() => readPreference("curaloop-language") === "th" ? "th" : "en");
  useEffect(() => {
    document.documentElement.lang = locale;
    writePreference("curaloop-language", locale);
  }, [locale]);
  const t = useCallback<Translator>((text, values) => {
    const key = text.trim().replace(/\s+/g, " ");
    const translated = locale === "th" && catalogue[key] ? catalogue[key] : key;
    const spaced = (text.match(/^\s*/)?.[0] ?? "") + translated + (text.match(/\s*$/)?.[0] ?? "");
    return spaced.replace(/\{(\w+)\}/g, (token, name: string) => String(values?.[name] ?? token));
  }, [locale]);
  return <Context.Provider value={{ locale, setLocale, t }}>{children}</Context.Provider>;
}
export function useI18n() {
  const context = useContext(Context);
  if (!context) throw new Error("I18nProvider required");
  return context;
}

export function LanguageSwitch() {
  const { locale, setLocale } = useI18n();
  return <div className="language-switch" role="group" aria-label={locale === "en" ? "Interface language" : "ภาษาของหน้าจอ"}>
    <button type="button" lang="en" aria-pressed={locale === "en"} onClick={() => setLocale("en")}>EN</button>
    <button type="button" lang="th" aria-pressed={locale === "th"} onClick={() => setLocale("th")}>ไทย</button>
  </div>;
}
