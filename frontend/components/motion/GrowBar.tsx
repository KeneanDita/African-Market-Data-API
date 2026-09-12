"use client";

import { motion, useReducedMotion } from "framer-motion";

type Props = {
  /** Target width as a percentage (0–100). */
  pct: number;
  className?: string;
  delay?: number;
};

/** A horizontal bar that grows from 0 to `pct`% width when scrolled into view. */
export default function GrowBar({ pct, className, delay = 0 }: Props) {
  const reduce = useReducedMotion();

  return (
    <motion.div
      className={className}
      initial={reduce ? false : { width: 0 }}
      whileInView={{ width: `${pct}%` }}
      viewport={{ once: true, margin: "-48px" }}
      transition={{ duration: 0.9, delay, ease: [0.22, 1, 0.36, 1] }}
      style={reduce ? { width: `${pct}%` } : undefined}
    />
  );
}
