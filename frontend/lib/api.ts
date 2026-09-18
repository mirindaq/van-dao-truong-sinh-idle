import type { BreakthroughPreview, BreakthroughRequest, BreakthroughResult, GameState, EquipmentSlot, ExplorationResponse } from "@/lib/types";

const messages: Record<string, string> = {
  no_save: "Tiên lộ của bạn chưa bắt đầu.",
  save_exists: "Đã có một hành trình được lưu. Đang tìm lại động phủ của bạn.",
  insufficient_cultivation: "Tu vi chưa đủ để đột phá.",
  stale_preview: "Khí tức đã thay đổi. Hãy xem lại cơ hội đột phá.",
  max_realm: "Bạn đã tới tận cùng tiên lộ hiện tại.",
  realm_unavailable: "Cảnh giới tiếp theo chưa mở.",
  insufficient_items: "Tụ Khí Đan đã hết. Hãy xem lại chuẩn bị đột phá.",
  invalid_item: "Vật phẩm này không thể dùng để đột phá.",
  item_not_owned: "Bạn chưa sở hữu trang bị này. Hãy đồng bộ lại túi đồ.",
  invalid_equipment: "Vật phẩm không phù hợp với ô trang bị này.",
  request_conflict: "Lần đột phá này đã được gửi với lựa chọn khác. Hãy đồng bộ lại hành trình.",
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
    throw new GameApiError(response.status >= 500 ? "connection" : code, messages[code] ?? (response.status === 422 ? "Thông tin chưa hợp lệ. Hãy kiểm tra lại lựa chọn." : "Chưa thể kết nối với động phủ. Hãy thử lại sau ít phút."));
  }
  return response.status === 204 ? undefined as T : response.json();
}

export const gameApi = {
  claimEquipment: () => request<GameState>("/equipment/claim", {}),
  equip: (slot: EquipmentSlot, item_key: string | null) => request<GameState>("/equipment/slot", { slot, item_key }),
  explore: (request_id: string) => request<ExplorationResponse>("/exploration/run", { request_id, location_key: "qingyun_mountain" }),
  getExploration: (request_id: string) => request<ExplorationResponse>(`/exploration/run/${request_id}`),
  latestExploration: () => request<ExplorationResponse>("/exploration/latest"),
  state: () => request<GameState>("/game/state"),
  newGame: (name: string) => request<GameState>("/game/new", { name }),
  acknowledgeOffline: (id: number) => request<void>(`/game/offline/${id}/ack`, {}),
  preview: (usePill = false) => request<BreakthroughPreview>(`/breakthrough/preview${usePill ? "?item_key=items%2Fqi_gathering_pill&quantity=1" : ""}`),
  attempt: (payload: BreakthroughRequest) => request<BreakthroughResult>("/breakthrough/attempt", payload),
};
