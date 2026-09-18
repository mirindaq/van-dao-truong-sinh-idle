"use client";

import { Compass, Gem, RefreshCw, ScrollText, Sparkles, Sword } from "lucide-react";
import { number } from "@/lib/format";
import type { Exploration, GameState } from "@/lib/types";

export function ExplorationView({ state, result, busy, onExplore }: { state: GameState; result: Exploration | null; busy: boolean; onExplore: () => void }) {
  return <section className="exploration-page">
    <div className="page-heading"><div><p className="eyebrow">CƠ DUYÊN · SƠN HÀ</p><h1>Thám Hiểm</h1></div><span>Thanh Vân Sơn</span></div>
    <section className="exploration-location"><div className="exploration-mark"><Compass size={42} /></div><div><p className="eyebrow">ĐỊA ĐIỂM ĐÃ MỞ</p><h2>Thanh Vân Sơn</h2><p className="muted">Một lối mòn xuyên rừng, nơi dã thú và cơ duyên cùng ẩn mình.</p><div className="exploration-meta"><span><Sword size={16} /> Nguy hiểm thấp</span><span><Sparkles size={16} /> Xử lý ngay</span></div></div><button className="primary-button" disabled={busy} onClick={onExplore}>{busy ? <><RefreshCw className="spin" size={17} />ĐANG THÁM HIỂM…</> : <><Compass size={17} />BẮT ĐẦU THÁM HIỂM</>}</button></section>
    {result && <section className={`exploration-result ${result.state}`} aria-live="polite"><div><p className="eyebrow">KẾT QUẢ ĐÃ LƯU</p><h2>{result.state === "victory" ? "Cơ duyên trong rừng" : result.state === "defeat" ? "Dã thú quá mạnh" : "Sơn lâm lặng gió"}</h2><p>{result.message}</p></div><div className="exploration-rewards"><span><Gem size={17} /> +{number(result.reward_stones)} Linh Thạch</span><span><Sparkles size={17} /> +{number(result.reward_pills)} Tụ Khí Đan</span></div></section>}
    {result?.battle_log.length ? <section className="battle-log"><div className="section-heading"><h2>Battle Log</h2><ScrollText size={18} /></div><ol>{result.battle_log.map((turn, index) => <li key={`${turn.turn}-${index}`}><strong>Lượt {turn.turn}</strong><span>{turn.actor} gây {number(turn.damage)} sát thương</span><small>Còn lại: {number(turn.target_hp)} HP</small></li>)}</ol></section> : result && <p className="muted exploration-empty">Không có trận chiến trong lượt này.</p>}
    <p className="muted">Chiến lực hiện tại: {number(state.player.combat_power)} · Phần thưởng được lưu cùng lượt thám hiểm.</p>
  </section>;
}
