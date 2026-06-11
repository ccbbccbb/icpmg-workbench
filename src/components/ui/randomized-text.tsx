"use client";

import { motion } from "framer-motion";
import { useMemo } from "react";

type SplitType = "words" | "chars";

interface RandomizedTextProps {
  children: string;
  className?: string;
  split?: SplitType;
  delay?: number;
  inView?: boolean;
  once?: boolean;
}

export function RandomizedText({
  children,
  className = "",
  split = "words",
  delay = 0.2,
  inView = false,
  once = true,
}: RandomizedTextProps) {
  const expoOut = (t: number): number => {
    return t === 1 ? 1 : 1 - 2 ** (-10 * t);
  };

  const elements = useMemo(() => {
    if (split === "chars") {
      return children.split("").map((char, i) => ({
        content: char === " " ? " " : char,
        key: `char-${i}`,
      }));
    }
    return children.split(" ").map((word, i) => ({
      content: word,
      key: `word-${i}`,
    }));
  }, [children, split]);

  const randomizedDelays = useMemo(() => {
    return elements.map(() => delay + Math.random() * 0.2 + Math.random() * 0.03);
  }, [elements, delay]);

  const variants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1 },
  };

  return (
    <motion.span
      animate={inView ? undefined : "visible"}
      aria-label={children}
      className={className}
      initial="hidden"
      style={{ display: "inline-block", wordBreak: "break-word" }}
      viewport={{ once }}
      whileInView={inView ? "visible" : undefined}
    >
      {elements.map((element, i) => (
        <motion.span
          className={split === "words" ? "mr-[0.25em]" : ""}
          key={element.key}
          style={{ display: split === "words" ? "inline-block" : "inline" }}
          transition={{
            duration: 1.2,
            delay: randomizedDelays[i],
            ease: expoOut,
          }}
          variants={variants}
        >
          {element.content}
        </motion.span>
      ))}
    </motion.span>
  );
}
