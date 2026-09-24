"use client";

import { useEffect, useRef, useState } from "react";
import { Check, Mountain, Sparkles } from "lucide-react";
import * as m from "motion/react-m";
import { duration, number } from "@/lib/format";
import { burst, hasPlayed, markPlayed } from "@/lib/moments";
import { useMotionPreference } from "@/lib/motion";
import type { GameState } from "@/lib/types";
import { GameModal } from "./game-ui";

type Report = NonNullable<GameState["offline_report"]>;

const COUNT_MS = 900;
const LARGE_ABSENCE_SECONDS = 3600;

function useCountUp(target: number, animate: boolean) {
  const [value, setValue] = useState(animate ? 0 : target);
  const frame = useRef(0);
  const skip = () => { cancelAnimationFrame(frame.current); setValue(target); };
  useEffect(() => {
    if (!animate) return;
    const start = performance.now();
    const step = (now: number) => {
      const t = Math.min(1, (now - start) / COUNT_MS);
      setValue(target * (1 - (1 - t) ** 3));
      if (t < 1) frame.current = requestAnimationFrame(step);
    };
    frame.current = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frame.current);
  }, [target, animate]);
  return [value, skip] as const;
}

export function OfflineReport({ report, logs, serverTime, busy, error, onLeave }: {
  report: Report; logs: GameState["recent_logs"]; serverTime: string; busy: boolean; error: React.ReactNode; onLeave: () => void;
}) {
  const { reduced } = useMotionPreference();
  // Captured once so a reload after the first showing lands on the final numbers.
  const [fresh] = useState(() => !hasPlayed("offline", report.id));
  const animate = fresh && !reduced;
  const [shown, skip] = useCountUp(report.earned_exp, animate);

  const canvas = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    if (!fresh) return;
    markPlayed("offline", report.id);
    if (report.elapsed_seconds < LARGE_ABSENCE_SECONDS) return;
    // Waits out the modal's entry transform so the fixed canvas covers the viewport.
    const timer = window.setTimeout(() => void burst(canvas.current, "large"), 450);
    return () => clearTimeout(timer);
  }, [fresh, report.id, report.elapsed_seconds]);

  const since = Date.parse(serverTime) - report.elapsed_seconds * 1000;
  const events = logs.filter(log => Date.parse(log.created_at) >= since).slice(0, 3);
  const enter = (delay: number) => animate ? { initial: { opacity: 0, y: 8 }, animate: { opacity: 1, y: 0 }, transition: { delay, duration: .35 } } : {};

  return <GameModal title="Bế Quan Kết Thúc" busy={busy}>
    {animate && <canvas ref={canvas} className="moment-canvas" aria-hidden="true" />}
    <div className="seclusion-report" onClick={skip}>
      <m.div className="offline-mark" {...enter(0)}><Mountain size={44} /></m.div>
      <m.p className="center muted" {...enter(.1)}>Bạn đã bế quan {duration(report.elapsed_seconds)}.</m.p>
      <m.div className="offline-reward" {...enter(.2)}>
        <Sparkles size={24} />
        <strong aria-hidden="true">+{number(shown, 2)}</strong>
        <span className="visually-hidden">+{number(report.earned_exp, 2)}</span>
        <span>Tu vi</span>
      </m.div>
      {events.length > 0 && <m.ul className="seclusion-events" aria-label="Trong lúc bế quan" {...enter(.35)}>
        {events.map(log => <li key={log.id}>{log.message}</li>)}
      </m.ul>}
      <p className="center muted">Đạo hạnh đã được ghi vào hành trình.</p>
      <p className="center muted">Bộ luật v{report.rules_version} · {report.rules_fingerprint}</p>
    </div>
    <button className="primary-button full-width" disabled={busy} onClick={onLeave}><Check size={18} />{busy ? "ĐANG XÁC NHẬN…" : "XUẤT QUAN"}</button>
    {error}
  </GameModal>;
}
