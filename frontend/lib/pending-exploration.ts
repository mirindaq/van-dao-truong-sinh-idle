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

const journeyKey = (playerId: number) => `pending-journey:${playerId}`;

export function readPendingJourney(playerId: number): { requestId: string; locationKey: string } | null {
  try {
    const raw = localStorage.getItem(journeyKey(playerId));
    if (!raw) return null;
    const parsed = JSON.parse(raw) as { requestId?: string; locationKey?: string };
    return parsed.requestId && parsed.locationKey ? { requestId: parsed.requestId, locationKey: parsed.locationKey } : null;
  } catch { return null; }
}

export function writePendingJourney(playerId: number, requestId: string, locationKey: string): void {
  try { localStorage.setItem(journeyKey(playerId), JSON.stringify({ requestId, locationKey })); } catch { /* server receipt stays authoritative */ }
}

export function clearPendingJourney(playerId: number): void {
  try { localStorage.removeItem(journeyKey(playerId)); } catch { /* best effort */ }
}
