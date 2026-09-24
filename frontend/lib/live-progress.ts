"use client";

import { useEffect, useRef, useState } from "react";

const BLEND_MS = 400;

type Source = { current: number; required: number; ratePerMinute: number };

// Projects the server's cultivation forward between syncs. The server stays the source of
// truth: every sync re-anchors the projection, and the display eases onto the new anchor.
export function useLiveExp({ current, required, ratePerMinute }: Source, paused: boolean, reduced: boolean) {
  const [shown, setShown] = useState(current);
  const shownRef = useRef(current);
  const anchor = useRef({ value: current, at: 0, from: current, blendAt: 0 });

  useEffect(() => {
    const now = performance.now();
    anchor.current = { value: current, at: now, from: shownRef.current, blendAt: now };
  }, [current]);

  useEffect(() => {
    const project = (now: number) => {
      const { value, at, from, blendAt } = anchor.current;
      const target = Math.min(required, value + ratePerMinute / 60 * Math.max(0, now - at) / 1000);
      const t = reduced ? 1 : Math.min(1, (now - blendAt) / BLEND_MS);
      const next = Math.min(required, from + (target - from) * (1 - (1 - t) ** 2));
      if (Math.abs(next - shownRef.current) < .002) return;
      shownRef.current = next; setShown(next);
    };
    if (paused) { project(performance.now()); return; }
    if (reduced) {
      project(performance.now());
      const timer = window.setInterval(() => { if (!document.hidden) project(performance.now()); }, 1000);
      return () => clearInterval(timer);
    }
    let frame = 0;
    const loop = (now: number) => { if (!document.hidden) project(now); frame = requestAnimationFrame(loop); };
    frame = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(frame);
  }, [required, ratePerMinute, paused, reduced]);

  return shown;
}
