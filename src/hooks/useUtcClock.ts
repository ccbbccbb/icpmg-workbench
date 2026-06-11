"use client";

import { useEffect, useState } from "react";

/**
 * Current UTC time as "HH:MM", ticking on an interval.
 * Returns null until mounted (avoids SSR/client hydration mismatch).
 */
export function useUtcClock(intervalMs = 30_000): string | null {
  const [time, setTime] = useState<string | null>(null);

  useEffect(() => {
    const update = () => {
      const now = new Date();
      const hours = String(now.getUTCHours()).padStart(2, "0");
      const minutes = String(now.getUTCMinutes()).padStart(2, "0");
      setTime(`${hours}:${minutes}`);
    };

    update();
    const id = globalThis.setInterval(update, intervalMs);
    return () => globalThis.clearInterval(id);
  }, [intervalMs]);

  return time;
}
