"use client";

import { createContext, useContext, useEffect, useRef, useState } from "react";
import * as m from "motion/react-m";
import { number } from "@/lib/format";
import { useMotionPreference } from "@/lib/motion";

// A value that briefly lifts when it changes, so a craft or an equip reads as a result.
export function Pop({ value, children }: { value: number | string; children?: React.ReactNode }) {
  const { reduced } = useMotionPreference();
  const [mounted] = useState(value);
  if (reduced) return <span className="pop">{children ?? value}</span>;
  return <m.span key={String(value)} className="pop" initial={value === mounted ? false : { scale: 1.3 }} animate={{ scale: 1 }} transition={{ duration: .45, ease: "easeOut" }}>{children ?? value}</m.span>;
}

// "+N" that rises and fades whenever the watched amount grows. Decorative: the amount
// itself is already on screen, so the chip stays out of the accessibility tree.
export function GainChip({ amount, unit }: { amount: number; unit: string }) {
  const { reduced } = useMotionPreference();
  const previous = useRef(amount);
  const [gain, setGain] = useState<{ id: number; value: number } | null>(null);
  useEffect(() => {
    const delta = amount - previous.current;
    previous.current = amount;
    if (delta <= 0) return;
    setGain({ id: Date.now(), value: delta });
    const timer = window.setTimeout(() => setGain(null), reduced ? 2500 : 1400);
    return () => clearTimeout(timer);
  }, [amount, reduced]);
  if (!gain) return null;
  const text = `+${number(gain.value)} ${unit}`;
  if (reduced) return <span className="gain-chip" aria-hidden="true">{text}</span>;
  return <m.span key={gain.id} className="gain-chip" aria-hidden="true" initial={{ opacity: 0, y: 6 }} animate={{ opacity: [0, 1, 1, 0], y: [6, 0, -4, -14] }} transition={{ duration: 1.4, times: [0, .15, .7, 1] }}>{text}</m.span>;
}

const SETTLE_MS = 400;
const ScreenOpened = createContext(0);

// Marks when the current screen was opened. Content that is already there when a screen
// opens (a revisit, a reload) appears still; only what arrives afterwards slides in.
export function ScreenMoments({ children }: { children: React.ReactNode }) {
  const [openedAt] = useState(() => performance.now());
  return <ScreenOpened.Provider value={openedAt}>{children}</ScreenOpened.Provider>;
}

export function Reveal({ id, delay = 0, className, children, ...rest }: { id?: string | number; delay?: number; className?: string; children: React.ReactNode } & React.AriaAttributes & { role?: string }) {
  const { reduced } = useMotionPreference();
  const openedAt = useContext(ScreenOpened);
  const [arrived] = useState(() => performance.now() - openedAt > SETTLE_MS);
  const [firstId] = useState(id);
  if (reduced || !(arrived || id !== firstId)) return <div key={id} className={className} {...rest}>{children}</div>;
  return <m.div key={id} className={className} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay, duration: .4, ease: [.2, .7, .2, 1] }} {...rest}>{children}</m.div>;
}
