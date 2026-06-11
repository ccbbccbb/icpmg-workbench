"use client";

import { useEffect, useRef } from "react";

interface ProximityScaleOptions {
  /** Distance (px) at which the effect fades to zero. */
  radius?: number;
  /** Scale applied at zero distance. */
  maxScale?: number;
  /** Brightness applied at zero distance (>1 brightens, <1 darkens). */
  maxBrightness?: number;
  /** Distance axis: "x" for horizontal docks, "y" for vertical lists, "both" for radial. */
  axis?: "x" | "y" | "both";
  /** CSS transform-origin for the scaled children. */
  transformOrigin?: string;
}

/**
 * macOS-dock-style proximity effect: direct children of the returned ref's
 * element scale/brighten as the cursor approaches, easing back when it leaves.
 * Transform/filter only (no reflow), rects cached and re-measured on
 * scroll/resize, disabled under prefers-reduced-motion.
 */
export function useProximityScale<T extends HTMLElement>({
  radius = 120,
  maxScale = 1.02,
  maxBrightness = 1,
  axis = "both",
  transformOrigin = "center",
}: ProximityScaleOptions = {}) {
  const containerRef = useRef<T | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) {
      return;
    }
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return;
    }

    const children = Array.from(container.children).filter(
      (child): child is HTMLElement => child instanceof HTMLElement
    );
    let rects: DOMRect[] = [];
    const measure = () => {
      rects = children.map((child) => child.getBoundingClientRect());
    };
    measure();

    for (const child of children) {
      child.style.transition = "transform 150ms ease-out, filter 150ms ease-out";
      child.style.willChange = "transform, filter";
      child.style.transformOrigin = transformOrigin;
    }

    let frame = 0;
    const apply = (clientX: number, clientY: number) => {
      children.forEach((child, index) => {
        const rect = rects[index];
        if (!rect) {
          return;
        }
        const centerX = rect.x + rect.width / 2;
        const centerY = rect.y + rect.height / 2;
        const distance =
          axis === "x"
            ? Math.abs(clientX - centerX)
            : axis === "y"
              ? Math.abs(clientY - centerY)
              : Math.hypot(clientX - centerX, clientY - centerY);
        const t = Math.max(0, 1 - distance / radius);
        child.style.transform = `scale(${1 + t * (maxScale - 1)})`;
        child.style.filter = `brightness(${1 + t * (maxBrightness - 1)})`;
      });
    };

    const onPointerMove = (event: PointerEvent) => {
      if (frame) {
        return;
      }
      frame = requestAnimationFrame(() => {
        frame = 0;
        apply(event.clientX, event.clientY);
      });
    };

    const reset = () => {
      for (const child of children) {
        child.style.transform = "scale(1)";
        child.style.filter = "brightness(1)";
      }
    };

    window.addEventListener("pointermove", onPointerMove, { passive: true });
    window.addEventListener("scroll", measure, true);
    window.addEventListener("resize", measure);
    document.documentElement.addEventListener("pointerleave", reset);

    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("scroll", measure, true);
      window.removeEventListener("resize", measure);
      document.documentElement.removeEventListener("pointerleave", reset);
      for (const child of children) {
        child.style.transition = "";
        child.style.willChange = "";
        child.style.transformOrigin = "";
        child.style.transform = "";
        child.style.filter = "";
      }
    };
  }, [radius, maxScale, maxBrightness, axis, transformOrigin]);

  return containerRef;
}
