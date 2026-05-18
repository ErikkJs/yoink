import { useEffect, useState } from "react";

// SSR-safe localStorage hook. Returns the default on the server and the first
// client render; reads the stored value (if any) in an effect after mount.
// Third return value is `hydrated` so callers can defer effects that would
// otherwise cause a visible flicker.
export function useLocalStorage<T>(
  key: string,
  defaultValue: T,
): [T, (next: T | ((prev: T) => T)) => void, boolean] {
  const [value, setValue] = useState<T>(defaultValue);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(key);
      if (raw !== null) {
        setValue(JSON.parse(raw) as T);
      }
    } catch {
      // ignore unparseable / unavailable storage
    }
    setHydrated(true);
  }, [key]);

  useEffect(() => {
    if (!hydrated) return;
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // ignore quota / privacy mode
    }
  }, [key, value, hydrated]);

  return [value, setValue, hydrated];
}
