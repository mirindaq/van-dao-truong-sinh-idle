import { ArrowRight, Clock3, Compass, Flame, Heart, Leaf, Mountain, Orbit, PawPrint, ScrollText, Sparkles } from "lucide-react";
import { assetPath } from "@/lib/assets";
import { duration, number, percent } from "@/lib/format";
import { useLiveExp } from "@/lib/live-progress";
import { useMotionPreference } from "@/lib/motion";
import type { GameState } from "@/lib/types";
import { CultivationProgress, GameTimeline, SpiritualRootBadge, StatRow } from "./game-ui";

function LiveProgress({ state, paused }: { state: GameState; paused: boolean }) {
  const { reduced } = useMotionPreference();
  const { cultivation } = state;
  const rate = state.player.current_activity === "cultivating" ? cultivation.rate_per_minute : 0;
  const current = useLiveExp({ current: cultivation.current_exp, required: cultivation.required_exp, ratePerMinute: rate }, paused, reduced);
  return <CultivationProgress cultivation={cultivation} current={current} />;
}

const motes = Array.from({ length: 7 }, (_, i) => i);

export function CultivationView({ state, detailed, eta, navigate, onBreakthrough, busy, paused }: { state: GameState; detailed: boolean; eta: number | null; navigate: (view: string) => void; onBreakthrough: () => void; busy: boolean; paused: boolean }) {
  const { cultivation, breakthrough } = state;
  return <>
    <div className="page-heading"><div><p className="eyebrow">THANH VÂN SƠN · ĐỘNG PHỦ VÔ DANH</p><h1>{detailed ? "Tĩnh tâm tu luyện" : "Động Phủ"}</h1><p className="page-description">Gác lại hồng trần, lắng nghe một nhịp linh khí.</p></div><span className="activity-tag"><span />{state.player.current_activity === "cultivating" ? "Đang tu luyện" : "Đang nghỉ ngơi"}</span></div>
    <div className="home-layout"><div className="main-column">
      <section className="cultivation-scene" aria-label="Động phủ tu luyện" style={{ backgroundImage: `url(${assetPath("maps/qingyun_mountain")})` }}>
        <div className="scene-top"><span><Mountain size={14} /> THANH VÂN ĐỘNG PHỦ</span><span className="scene-seal">Tĩnh tâm</span></div>
        <div className="scene-body"><div className="realm-heading"><p>Đạo hữu {state.player.name}</p><h2>{state.realm.name}</h2><span className="stage-ornament">TẦNG {state.realm.stage}</span><p className="scene-verse">Một niệm tĩnh tâm,<br />vạn đạo quy nguyên.</p></div>
        <div className="cultivator-art"><div className="qi-motes" aria-hidden="true">{motes.map(i => <span key={i} />)}</div><div className="cultivation-circle" /><img src={assetPath("characters/player/default")} width={320} height={420} alt="Tu sĩ áo dài giữa núi mây Thanh Vân" /></div></div>
        <div className="scene-progress"><LiveProgress state={state} paused={paused} /><div className="progress-meta"><span><Sparkles size={14} /> +{number(cultivation.rate_per_minute, 2)} tu vi / phút</span><span><Clock3 size={14} />{eta === 0 ? "Bình cảnh đã tới" : `Còn ${duration(eta)}`}</span></div></div>
      </section>
      <div className="cultivation-actions"><div><Orbit size={20} /><span><strong>{breakthrough.available ? "Bình cảnh đã tới" : "Linh khí đang vận chuyển"}</strong><small>{breakthrough.available ? "Đã đủ tu vi để thử sức với cảnh giới tiếp theo." : "Năm tháng trôi qua, đạo hạnh dần sâu."}</small></span></div>{detailed || breakthrough.available ? <button className={`primary-button ${breakthrough.available ? "breakthrough-ready" : ""}`} onClick={onBreakthrough} disabled={busy || !breakthrough.target}><Flame size={18} />{busy ? "Đang cảm nhận…" : breakthrough.available ? "ĐỘT PHÁ" : "XEM BÌNH CẢNH"}<ArrowRight size={16} /></button> : <button className="primary-button" onClick={() => navigate("cultivation")}><Orbit size={18} />TU LUYỆN<ArrowRight size={16} /></button>}</div>
      {detailed && <div className="cultivation-summary" aria-label="Tổng quan tu hành"><div><span>Tiến cảnh tiếp theo</span><strong>{breakthrough.target ? `${breakthrough.target.name} · ${breakthrough.target.stage}` : "Viên mãn"}</strong></div><div><span>Cơ hội đột phá</span><strong>{percent(breakthrough.final_chance)}</strong></div><div><span>Tụ Khí Đan</span><strong>{number(state.player.qi_gathering_pills)} <small>viên</small></strong></div></div>}
      {detailed ? <section className="cultivation-details"><div><div className="section-heading"><h2>Vận chuyển linh khí</h2><Leaf size={18} /></div><StatRow label="Cơ sở" value={`+${number(cultivation.base_rate_per_minute, 3)}`} /><StatRow label={state.spiritual_root.name} value={`+${number(cultivation.root_bonus_per_minute, 3)}`} /><StatRow label="Hệ số linh thú" value={`×${number(cultivation.pet_factor, 2)}`} /><StatRow label="Lượng linh thú" value={`+${number(cultivation.pet_flat_per_minute, 2)}`} /><StatRow label="Hệ số đạo lữ" value={`×${number(cultivation.partner_factor, 2)}`} /><StatRow label="Lượng đạo lữ" value={`+${number(cultivation.partner_flat_per_minute, 2)}`} /><StatRow label="Tổng tu vi / phút" value={`+${number(cultivation.rate_per_minute, 3)}`} accent /></div><div><div className="section-heading"><h2>Bình cảnh tiếp theo</h2><Flame size={18} /></div><h3>{breakthrough.target ? `${breakthrough.target.name} · Tầng ${breakthrough.target.stage}` : "Tận cùng tiên lộ"}</h3><StatRow label="Tu vi cần thiết" value={number(breakthrough.required_exp)} /><StatRow label="Trạng thái" value={breakthrough.available ? "Có thể đột phá" : breakthrough.target ? "Đang tích lũy" : "Đã viên mãn"} /></div></section> : <section className="opportunities"><div className="section-heading"><h2>Trên đường vấn đạo</h2><span>Mỗi bước một cơ duyên</span></div><div className="opportunity-grid">{[
        { id: "cultivation", icon: Flame, name: "Đột phá", text: breakthrough.target ? `${breakthrough.target.name} · Tầng ${breakthrough.target.stage} — ${percent(breakthrough.final_chance)} cơ hội` : "Tiên lộ đã viên mãn.", action: breakthrough.available ? "Bình cảnh đã tới" : eta === null ? "Xem bình cảnh" : `Còn ${duration(eta)}`, index: "01", ready: breakthrough.available },
        { id: "alchemy", icon: Leaf, name: "Luyện đan", text: `Tụ Khí Đan trong túi: ${number(state.player.qi_gathering_pills)} viên.`, action: "Vào đan phòng", index: "02", ready: false },
        { id: "exploration", icon: Compass, name: "Thám hiểm", text: "Qua núi ngàn, tìm tiên duyên.", action: "Lên đường", index: "03", ready: false },
      ].map(item => <a key={item.id} href={`#${item.id}`} onClick={() => navigate(item.id)} className={`opportunity ${item.id} ${item.ready ? "ready" : ""}`}><div className="opportunity-mark"><item.icon size={25} /><small>{item.index}</small></div><h3>{item.name}</h3><p>{item.text}</p><span>{item.action}<ArrowRight size={16} /></span></a>)}</div></section>}
    </div><aside className="context-column">
      <section className="root-section"><div className="section-heading"><h2>Căn nguyên</h2><Sparkles size={17} /></div><SpiritualRootBadge root={state.spiritual_root} /><StatRow label="Tu luyện" value={`×${number(state.spiritual_root.cultivation_modifier, 2)}`} /><StatRow label="Tỷ lệ đột phá" value={`×${number(state.spiritual_root.breakthrough_modifier, 2)}`} /><p className="root-note">Linh căn là khởi điểm.<br />Đạo hạnh nằm ở lòng kiên định.</p></section>
      <section className="companions"><div className="section-heading"><h2>Tiên lộ đồng hành</h2></div><a href="#pets" onClick={() => navigate("pets")} className="companion-row"><PawPrint size={23} /><span><strong>Linh thú</strong><small>{state.spirit_pet ? `${state.spirit_pet.name}${state.spirit_pet.active ? "" : " · đang nghỉ"}` : "Chưa kết khế ước"}</small></span><ArrowRight size={15} /></a><a href="#partner" onClick={() => navigate("partner")} className="companion-row"><Heart size={23} /><span><strong>Đạo lữ</strong><small>{state.dao_partners.filter(partner => partner.active).map(partner => partner.name).join(", ") || "Chưa có người đồng hành"}</small></span><ArrowRight size={15} /></a></section>
      <section className="recent-section"><div className="section-heading"><h2>Tiên ký</h2><ScrollText size={17} /></div><GameTimeline logs={state.recent_logs.slice(0, 4)} /><a href="#journal" onClick={() => navigate("journal")} className="text-link">Xem nhật ký <ArrowRight size={14} /></a></section>
      {detailed && <p className="muted footnote">Cơ hội đột phá hiện tại: {percent(breakthrough.final_chance)}</p>}
    </aside></div>
  </>;
}
