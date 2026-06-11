"use client";

import { animate } from "framer-motion";
import { useEffect, useState } from "react";

/**
 * Animates 0 → target once on mount (easeOut), returning the in-flight value.
 * Jumps straight to target under prefers-reduced-motion.
 */
export function useCountUp(
  target: number,
  { durationMs = 1200, delayMs = 0 }: { durationMs?: number; delayMs?: number } = {}
): number {
  const [value, setValue] = useState(0);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setValue(target);
      return;
    }

    const controls = animate(0, target, {
      delay: delayMs / 1000,
      duration: durationMs / 1000,
      ease: "easeOut",
      onUpdate: (latest) => setValue(latest),
    });
    return () => controls.stop();
  }, [target, durationMs, delayMs]);

  return value;
}
