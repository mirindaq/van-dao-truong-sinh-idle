"use client";

import { Clock, Compass, Gem, RefreshCw, ScrollText, Sparkles, Sword } from "lucide-react";
import { number } from "@/lib/format";
import type { Exploration, GameState } from "@/lib/types";

const JOURNEYS = [
  { key: "hau_son", name: "Hậu Sơn", minutes: 5, reward: "Vân Linh Thảo", danger: "Thấp" },
  { key: "ngoai_vi", name: "Ngoại Vi", minutes: 10, reward: "Thanh Trúc Kiếm", danger: "Vừa" },
  { key: "linh_mach", name: "Linh Mạch", minutes: 15, reward: "Linh Mạch Kiếm", danger: "Cao" },
];

const REWARD_NAMES: Record<string, string> = {
  "items/cloud_mist_herb": "Vân Linh Thảo",
  "items/bamboo_sword": "Thanh Trúc Kiếm",
  "items/spirit_vein_sword": "Linh Mạch Kiếm",
};

function remainingSeconds(availableAt: string, serverTime: string, elapsed: number) {
  return Math.max(0, Math.ceil((Date.parse(availableAt) - Date.parse(serverTime)) / 1000 - elapsed));
}

export function ExplorationView({ state, result, journey, busy, elapsed, onExplore, onJourney, onClaim }: {
  state: GameState; result: Exploration | null; journey: Exploration | null; busy: boolean; elapsed: number;
  onExplore: () => void; onJourney: (locationKey: string) => void; onClaim: (requestId: string) => void;
}) {
  const traveling = journey?.state === "traveling" ? journey : null;
  return <section className="exploration-page">
    <div className="page-heading"><div><p className="eyebrow">CƠ DUYÊN · SƠN HÀ</p><h1>Thám Hiểm</h1></div><span>Thanh Vân Sơn</span></div>
    <section className="exploration-location"><div className="exploration-mark"><Compass size={42} /></div><div><p className="eyebrow">ĐỊA ĐIỂM ĐÃ MỞ</p><h2>Thanh Vân Sơn</h2><p className="muted">Một lối mòn xuyên rừng, nơi dã thú và cơ duyên cùng ẩn mình.</p><div className="exploration-meta"><span><Sword size={16} /> Nguy hiểm thấp</span><span><Sparkles size={16} /> Xử lý ngay</span></div></div><button className="primary-button" disabled={busy} onClick={onExplore}>{busy ? <><RefreshCw className="spin" size={17} />ĐANG THÁM HIỂM…</> : <><Compass size={17} />BẮT ĐẦU THÁM HIỂM</>}</button></section>
    <div className="journey-list">
      {JOURNEYS.map(place => {
        const active = journey?.location_key === place.key ? journey : null;
        const locked = Boolean(traveling && traveling.location_key !== place.key);
        const seconds = active?.available_at ? remainingSeconds(active.available_at, state.server_time, elapsed) : place.minutes * 60;
        const label = active?.state === "traveling" ? `NHẬN KẾT QUẢ ${place.name.toUpperCase()}` : `BẮT ĐẦU ${place.name.toUpperCase()}`;
        return <article className="journey-card" key={place.key} aria-label={place.name}>
          <p className="eyebrow">{place.minutes} PHÚT · NGUY HIỂM {place.danger.toUpperCase()}</p>
          <h2>{place.name}</h2>
          <p className="muted">Thưởng: {place.reward}</p>
          {active?.state === "traveling" && <p><Clock size={16} /> {seconds === 0 ? "Đã tới giờ server" : `Còn ${Math.floor(seconds / 60)} phút ${seconds % 60} giây`}</p>}
          {active && active.state !== "traveling" && <p>{active.message}{active.reward_item_quantity > 0 ? ` +${active.reward_item_quantity} ${REWARD_NAMES[active.reward_item_key ?? ""] ?? "vật phẩm"}` : ""}</p>}
          <button className="secondary-button" disabled={busy || locked || Boolean(active && active.state !== "traveling")} onClick={() => active?.state === "traveling" ? onClaim(active.request_id) : onJourney(place.key)}>{active && active.state !== "traveling" ? "ĐÃ XONG" : label}</button>
        </article>;
      })}
    </div>
    {result && <section className={`exploration-result ${result.state}`} aria-live="polite"><div><p className="eyebrow">KẾT QUẢ ĐÃ LƯU</p><h2>{result.state === "victory" ? "Cơ duyên trong rừng" : result.state === "defeat" ? "Dã thú quá mạnh" : "Sơn lâm lặng gió"}</h2><p>{result.message}</p></div><div className="exploration-rewards"><span><Gem size={17} /> +{number(result.reward_stones)} Linh Thạch</span><span><Sparkles size={17} /> +{number(result.reward_pills)} Tụ Khí Đan</span></div></section>}
    {result?.battle_log.length ? <section className="battle-log"><div className="section-heading"><h2>Battle Log</h2><ScrollText size={18} /></div><ol>{result.battle_log.map((turn, index) => <li key={`${turn.turn}-${index}`}><strong>Lượt {turn.turn}</strong><span>{turn.actor} gây {number(turn.damage)} sát thương</span><small>Còn lại: {number(turn.target_hp)} HP</small></li>)}</ol></section> : result && <p className="muted exploration-empty">Không có trận chiến trong lượt này.</p>}
    {journey?.battle_log.length ? <section className="battle-log" aria-label="Nhật ký hành trình"><div className="section-heading"><h2>Nhật ký hành trình</h2><ScrollText size={18} /></div><ol>{journey.battle_log.map((turn, index) => <li key={`${turn.turn}-${index}`}><strong>Lượt {turn.turn}</strong><span>{turn.actor} gây {number(turn.damage)} sát thương</span><small>Còn lại: {number(turn.target_hp)} HP</small></li>)}</ol></section> : null}
    <p className="muted">Chiến lực hiện tại: {number(state.player.combat_power)} · Phần thưởng được lưu cùng lượt thám hiểm.</p>
  </section>;
}
