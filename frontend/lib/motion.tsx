"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { LazyMotion, MotionConfig, domAnimation } from "motion/react";

const KEY = "reduce-motion";
const QUERY = "(prefers-reduced-motion: reduce)";

type MotionPreference = { reduced: boolean; setReduced: (value: boolean) => void };

const PreferenceContext = createContext<MotionPreference>({ reduced: false, setReduced: () => {} });

function stored(): boolean | null {
  try {
    const value = localStorage.getItem(KEY);
    return value === "true" ? true : value === "false" ? false : null;
  } catch { return null; }
}

function apply(value: boolean) {
  document.documentElement.dataset.reduceMotion = String(value);
}

export function isReducedMotion() {
  return typeof document !== "undefined" && document.documentElement.dataset.reduceMotion === "true";
}

export function MotionProvider({ children }: { children: React.ReactNode }) {
  const [reduced, setState] = useState(false);

  useEffect(() => {
    const media = matchMedia(QUERY);
    const sync = () => { const value = stored() ?? media.matches; setState(value); apply(value); };
    sync();
    media.addEventListener("change", sync);
    return () => media.removeEventListener("change", sync);
  }, []);

  const setReduced = useCallback((value: boolean) => {
    setState(value); apply(value);
    try { localStorage.setItem(KEY, String(value)); } catch { /* the choice still applies for this visit */ }
  }, []);

  // MotionConfig's reducedMotion only drops transform/layout animations, so opacity
  // and colour tweens are zeroed through the default transition as well.
  return <PreferenceContext.Provider value={{ reduced, setReduced }}>
    <MotionConfig reducedMotion={reduced ? "always" : "never"} transition={reduced ? { duration: 0 } : undefined}>
      <LazyMotion features={domAnimation} strict>{children}</LazyMotion>
    </MotionConfig>
  </PreferenceContext.Provider>;
}

export function useMotionPreference() {
  return useContext(PreferenceContext);
}
