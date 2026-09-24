import { isReducedMotion } from "./motion";

const KEY = "played-moments";
const LIMIT = 60;

function played(): string[] {
  try {
    const value: unknown = JSON.parse(localStorage.getItem(KEY) ?? "[]");
    return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
  } catch { return []; }
}

export function hasPlayed(kind: string, id: string | number) {
  return played().includes(`${kind}:${id}`);
}

export function markPlayed(kind: string, id: string | number) {
  const entry = `${kind}:${id}`;
  const next = [...played().filter(item => item !== entry), entry].slice(-LIMIT);
  try { localStorage.setItem(KEY, JSON.stringify(next)); } catch { /* a replay after reload is the only cost */ }
}

const palette = ["#294c3e", "#5f8a74", "#a74735", "#c3a773", "#fcfaf4"];

type Confetti = typeof import("canvas-confetti");
const launchers = new WeakMap<HTMLCanvasElement, ReturnType<Confetti["create"]>>();

// Modals live in the browser's top layer, so particles draw on a canvas inside the
// modal; drawing on the page would leave them under the backdrop.
export async function burst(canvas: HTMLCanvasElement | null, strength: "small" | "large" = "large") {
  if (!canvas || isReducedMotion() || document.hidden) return;
  try {
    const { default: confetti } = await import("canvas-confetti");
    let fire = launchers.get(canvas);
    if (!fire) { fire = confetti.create(canvas, { resize: true, disableForReducedMotion: true }); launchers.set(canvas, fire); }
    const count = strength === "large" ? 120 : 50;
    await fire({ particleCount: count, spread: 75, startVelocity: 32, gravity: .8, ticks: 160, scalar: .8, origin: { y: .55 }, colors: palette });
  } catch { /* particles are decoration; the moment still completes without them */ }
}
