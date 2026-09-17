import type { BreakthroughRequest } from "./types";

const key = (playerId: number) => `breakthrough-pending:${playerId}`;

export function readPending(playerId: number): BreakthroughRequest | null {
  const value = localStorage.getItem(key(playerId));
  if (!value) return null;
  const data: unknown = JSON.parse(value);
  if (typeof data !== "object" || data === null) throw new Error("Không đọc được lần đột phá đang chờ.");
  const pending = data as BreakthroughRequest;
  if (typeof pending.request_id !== "string" || !/^[0-9a-f-]{36}$/i.test(pending.request_id)
      || typeof pending.revision !== "string" || !pending.revision
      || !((pending.quantity === 0 && pending.item_key === null)
        || (pending.quantity === 1 && pending.item_key === "items/qi_gathering_pill"))) {
    throw new Error("Lần đột phá đang chờ không hợp lệ. Chưa gửi yêu cầu mới.");
  }
  return pending;
}

export function writePending(playerId: number, request: BreakthroughRequest) {
  try { localStorage.setItem(key(playerId), JSON.stringify(request)); }
  catch { throw new Error("Không thể lưu lần đột phá đang chờ. Hãy cho phép lưu trữ rồi thử lại."); }
}

export function clearPending(playerId: number) {
  localStorage.removeItem(key(playerId));
}
