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

export async function burst(strength: "small" | "large" = "large") {
  if (isReducedMotion() || document.hidden) return;
  try {
    const { default: confetti } = await import("canvas-confetti");
    const count = strength === "large" ? 120 : 50;
    await confetti({ particleCount: count, spread: 75, startVelocity: 32, gravity: .8, ticks: 160, scalar: .8, origin: { y: .55 }, colors: palette, disableForReducedMotion: true });
  } catch { /* particles are decoration; the moment still completes without them */ }
}
