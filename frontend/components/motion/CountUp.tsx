"use client";

import { animate, useInView, useReducedMotion } from "framer-motion";
import { useEffect, useRef } from "react";

type Props = {
  value: number;
  className?: string;
  duration?: number;
};

/**
 * Renders the final value (SSR/no-JS safe), then counts up from 0 the first
 * time it scrolls into view.
 */
export default function CountUp({ value, className, duration = 1.2 }: Props) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-48px" });
  const reduce = useReducedMotion();

  // Zero the number on mount so the count-up has somewhere to go.
  useEffect(() => {
    if (!reduce && ref.current) ref.current.textContent = "0";
  }, [reduce]);

  useEffect(() => {
    if (!inView || reduce || !ref.current) return;
    const controls = animate(0, value, {
      duration,
      ease: [0.22, 1, 0.36, 1],
      onUpdate: (v) => {
        if (ref.current) ref.current.textContent = Math.round(v).toString();
      },
    });
    return () => controls.stop();
  }, [inView, reduce, value, duration]);

  return (
    <span ref={ref} className={className}>
      {value}
    </span>
  );
}
