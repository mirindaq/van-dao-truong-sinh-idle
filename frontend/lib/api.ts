import type { BreakthroughPreview, BreakthroughResult, GameState } from "@/lib/types";

const messages: Record<string, string> = {
  no_save: "Tiên lộ của bạn chưa bắt đầu.",
  save_exists: "Đã có một hành trình được lưu. Đang tìm lại động phủ của bạn.",
  insufficient_cultivation: "Tu vi chưa đủ để đột phá.",
  stale_preview: "Khí tức đã thay đổi. Hãy xem lại cơ hội đột phá.",
  max_realm: "Bạn đã tới tận cùng tiên lộ hiện tại.",
  realm_unavailable: "Cảnh giới tiếp theo chưa mở.",
};

export class GameApiError extends Error {
  constructor(public code: string, message: string) { super(message); }
}

async function request<T>(path: string, body?: unknown): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/api${path}`, {
      method: body === undefined ? "GET" : "POST",
      headers: body === undefined ? undefined : { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
      cache: "no-store",
      signal: AbortSignal.timeout(15000),
    });
  } catch {
    throw new GameApiError("connection", "Tạm mất liên lạc với động phủ. Hãy kiểm tra kết nối rồi thử lại.");
  }
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    const code = typeof payload?.detail === "string" ? payload.detail : "unknown";
    throw new GameApiError(code, messages[code] ?? (response.status === 422 ? "Tên đạo hữu cần từ 1 đến 40 ký tự hợp lệ." : "Chưa thể kết nối với động phủ. Hãy thử lại sau ít phút."));
  }
  return response.status === 204 ? undefined as T : response.json();
}

export const gameApi = {
  state: () => request<GameState>("/game/state"),
  newGame: (name: string) => request<GameState>("/game/new", { name }),
  acknowledgeOffline: (id: number) => request<void>(`/game/offline/${id}/ack`, {}),
  preview: () => request<BreakthroughPreview>("/breakthrough/preview"),
  attempt: (request_id: string, revision: string) => request<BreakthroughResult>("/breakthrough/attempt", { request_id, revision }),
};
