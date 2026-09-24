"use client";

import { useEffect, useRef, useState } from "react";
import * as m from "motion/react-m";
import { burst, hasPlayed, markPlayed } from "@/lib/moments";
import { useMotionPreference } from "@/lib/motion";

const CEREMONY_MS = 1400;
const PEAK_MS = 650;

export function BreakthroughCeremony({ id, success, children }: { id: string; success: boolean; children: React.ReactNode }) {
  const { reduced } = useMotionPreference();
  const [playing, setPlaying] = useState(() => !reduced && !hasPlayed("breakthrough", id));
  const canvas = useRef<HTMLCanvasElement>(null);

  useEffect(() => { markPlayed("breakthrough", id); }, [id]);

  useEffect(() => {
    if (!playing) return;
    const done = window.setTimeout(() => setPlaying(false), CEREMONY_MS);
    const peak = success ? window.setTimeout(() => void burst(canvas.current, "large"), PEAK_MS) : 0;
    // Escape skips the ceremony instead of closing the dialog around it.
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      event.preventDefault(); event.stopPropagation(); setPlaying(false);
    };
    document.addEventListener("keydown", onKey, true);
    return () => { clearTimeout(done); clearTimeout(peak); document.removeEventListener("keydown", onKey, true); };
  }, [playing, success]);

  const tone = success ? "success" : "failure";
  return <>
    {success && !reduced && <canvas ref={canvas} className="moment-canvas" aria-hidden="true" />}
    {playing
      ? <button type="button" className={`ceremony ${tone}`} onClick={() => setPlaying(false)} aria-label="Bỏ qua nghi thức đột phá">
        <m.span className="ceremony-ring" initial={{ scale: .4, opacity: 0 }} animate={{ scale: [.4, 1.08, 1], opacity: [0, 1, 1] }} transition={{ duration: .9, times: [0, .7, 1], ease: "easeOut" }} />
        <m.span className="ceremony-ring outer" initial={{ scale: .6, opacity: 0 }} animate={{ scale: [.6, 1.35], opacity: [0, .8, 0] }} transition={{ duration: 1.2, delay: .25, ease: "easeOut" }} />
        <m.span className="ceremony-core" initial={{ scale: 0 }} animate={{ scale: success ? [0, 1.25, 1] : [0, .9, .7] }} transition={{ duration: .8, delay: .2 }} />
        <m.span className="ceremony-word" initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: .55, duration: .4 }}>{success ? "Phá cảnh" : "Đạo tâm chấn động"}</m.span>
      </button>
      : <m.div initial={reduced ? false : { opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .35 }}>{children}</m.div>}
  </>;
}
