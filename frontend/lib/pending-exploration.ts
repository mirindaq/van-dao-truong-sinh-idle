const key = (playerId: number) => `pending-exploration:${playerId}`;

export function readPendingExploration(playerId: number): string | null {
  try { return localStorage.getItem(key(playerId)); } catch { return null; }
}

export function writePendingExploration(playerId: number, requestId: string): void {
  try { localStorage.setItem(key(playerId), requestId); } catch { /* best effort; server idempotency remains authoritative */ }
}

export function clearPendingExploration(playerId: number): void {
  try { localStorage.removeItem(key(playerId)); } catch { /* best effort */ }
}
