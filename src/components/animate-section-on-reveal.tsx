"use client";

import type { HTMLMotionProps } from "framer-motion";
import { AnimatePresence, motion } from "framer-motion";
import type { PropsWithChildren } from "react";
import { useMemo } from "react";

// --- timing (Profile A defaults) ---
export const SECTION_REVEAL_DURATION_MS = 125;
export const SECTION_REVEAL_STAGGER_MS = 125;

// --- timing (Profile B — chrome / landing) ---
export const UI_SLIDE_REVEAL_MS = 250;

type TransitionState = {
  opacity?: number;
  y?: number | string;
  transition?: { duration?: number; delay?: number; ease?: string };
};

type SectionRevealVariants = {
  initial: { opacity?: number; y?: number | string };
  open: TransitionState | ((custom: number) => TransitionState);
  exit: TransitionState | ((custom: number) => TransitionState);
};

export function createSectionRevealVariants({
  delayMs = SECTION_REVEAL_STAGGER_MS,
  durationMs = SECTION_REVEAL_DURATION_MS,
}: { delayMs?: number; durationMs?: number } = {}): SectionRevealVariants {
  return {
    initial: { opacity: 0, y: 12 },
    open: (index: number) => ({
      opacity: 1,
      y: 0,
      transition: {
        duration: durationMs / 1000,
        delay: (index * delayMs) / 1000,
      },
    }),
    exit: (index: number) => ({
      opacity: 0,
      y: -12,
      transition: {
        duration: durationMs / 1000,
        delay: (index * delayMs) / 1000,
      },
    }),
  };
}

type AnimateSectionOnRevealProps = PropsWithChildren<
  Omit<HTMLMotionProps<"div">, "initial" | "animate" | "variants" | "custom"> & {
    index?: number;
    delayMs?: number;
    durationMs?: number;
    sectionVariants?: SectionRevealVariants;
    className?: string;
    isVisible?: boolean;
    presenceKey?: string | number;
    presenceMode?: "sync" | "wait" | "popLayout";
    usePresence?: boolean;
  }
>;

export function AnimateSectionOnReveal({
  children,
  className,
  index = 0,
  delayMs = SECTION_REVEAL_STAGGER_MS,
  durationMs = SECTION_REVEAL_DURATION_MS,
  sectionVariants,
  isVisible = true,
  presenceKey,
  presenceMode = "popLayout",
  usePresence = false,
  ...props
}: AnimateSectionOnRevealProps) {
  const variants = useMemo(
    () => sectionVariants ?? createSectionRevealVariants({ delayMs, durationMs }),
    [sectionVariants, delayMs, durationMs]
  );

  if (!usePresence) {
    return (
      <motion.div
        animate="open"
        className={className}
        custom={index}
        exit="exit"
        initial="initial"
        variants={variants}
        {...props}
      >
        {children}
      </motion.div>
    );
  }

  return (
    <AnimatePresence mode={presenceMode}>
      {isVisible ? (
        <motion.div
          animate="open"
          className={className}
          custom={index}
          exit="exit"
          initial="initial"
          key={presenceKey}
          variants={variants}
          {...props}
        >
          {children}
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
