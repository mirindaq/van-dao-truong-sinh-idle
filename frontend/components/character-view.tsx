import { Backpack, BookOpen, Gem, ScrollText, Shield, Sparkles, Sword } from "lucide-react";
import { assetPath } from "@/lib/assets";
import { elementNames, number } from "@/lib/format";
import type { GameState } from "@/lib/types";
import { CultivationProgress, RarityBadge, SpiritualRootBadge, StatRow } from "./game-ui";

const manualNames: Record<string, string> = { qing_mu_jue: "Thanh Mộc Quyết", "manual/qing_mu_jue": "Thanh Mộc Quyết" };

export function CharacterView({ state, navigate }: { state: GameState; navigate: (view: string) => void }) {
  const manualName = manualNames[state.player.manual_key] ?? state.player.manual_key;
  return <div className="character-page">
    <div className="page-heading"><div><p className="eyebrow">ĐẠO THÂN · CĂN CỐT</p><h1>Nhân Vật</h1></div><span>{state.realm.name} · Tầng {state.realm.stage}</span></div>
    <section className="character-hero">
      <div className="character-portrait" style={{ backgroundImage: `url(${assetPath("maps/qingyun_mountain")})` }}><img src={assetPath("characters/player/default")} alt="Chân dung tu sĩ" width={260} height={360} /></div>
      <div className="character-profile"><p className="eyebrow">PHÀM THÂN VẤN ĐẠO</p><h2>{state.player.name}</h2><div className="realm-strip"><strong>{state.realm.name}</strong><span>Tầng {state.realm.stage}</span></div><CultivationProgress cultivation={state.cultivation} /><div className="profile-actions"><button className="secondary-button" onClick={() => navigate("cultivation")}><Sparkles size={17} />Tu luyện</button><button className="secondary-button" onClick={() => navigate("inventory")}><Backpack size={17} />Túi đồ</button></div></div>
      <aside className="character-stats"><StatRow label="Chiến lực" value={number(state.player.combat_power)} accent /><StatRow label="Linh thạch" value={number(state.player.spirit_stones)} /><StatRow label="Tụ Khí Đan" value={number(state.player.qi_gathering_pills)} /><StatRow label="Hoạt động" value={state.player.current_activity === "cultivating" ? "Tu luyện" : "Nghỉ ngơi"} /></aside>
    </section>
    <div className="feature-grid two">
      <section className="feature-panel"><div className="section-heading"><h2>Linh Căn</h2><Sparkles size={18} /></div><SpiritualRootBadge root={state.spiritual_root} /><StatRow label="Nguyên tố" value={state.spiritual_root.elements.map(e => elementNames[e] ?? e).join(" / ")} /><StatRow label="Tu luyện" value={`×${number(state.spiritual_root.cultivation_modifier, 2)}`} /><StatRow label="Đột phá" value={`×${number(state.spiritual_root.breakthrough_modifier, 2)}`} /></section>
      <section className="feature-panel"><div className="section-heading"><h2>Công Pháp</h2><BookOpen size={18} /></div><div className="manual-card"><ScrollText size={28} /><div><strong>{manualName}</strong><span>Tâm pháp đang vận chuyển</span></div></div><p className="muted">Chỉ hiển thị công pháp backend đang lưu cho nhân vật.</p></section>
    </div>
  </div>;
}

export function InventoryView({ state, navigate }: { state: GameState; navigate: (view: string) => void }) {
  const hasPills = state.player.qi_gathering_pills > 0;
  return <section className="collection-page"><div className="page-heading"><div><p className="eyebrow">TÚI CÀN KHÔN</p><h1>Túi Đồ</h1></div><span>{hasPills ? `${number(state.player.qi_gathering_pills)} vật phẩm` : "Trống"}</span></div><div className="filter-row"><button className="filter-pill active">Tất Cả</button><button className="filter-pill" disabled>Đan Dược</button><button className="filter-pill" disabled>Linh Thảo</button><button className="filter-pill" disabled>Trang Bị</button><button className="filter-pill" disabled>Công Pháp</button></div>{hasPills ? <div className="inventory-grid"><article className="item-card"><div className="item-icon"><Gem size={25} /></div><div><strong>Tụ Khí Đan</strong><span>Đan dược khởi đầu</span></div><RarityBadge /><b>x{number(state.player.qi_gathering_pills)}</b></article></div> : <EmptyLore icon={<Backpack size={42} />} title="Túi càn khôn còn trống" text="Ngoài mấy sợi linh khí vương trên tay áo, bạn chưa cất giữ thêm vật gì." action="Đi tu luyện" onAction={() => navigate("cultivation")} />}</section>;
}

export function SkillsView({ state, navigate }: { state: GameState; navigate: (view: string) => void }) {
  const manualName = manualNames[state.player.manual_key] ?? state.player.manual_key;
  return <section className="collection-page"><div className="page-heading"><div><p className="eyebrow">ĐẠO PHÁP · TÂM QUYẾT</p><h1>Công Pháp</h1></div><span>Tâm pháp</span></div><div className="manual-detail"><div className="manual-emblem"><BookOpen size={42} /></div><div><RarityBadge /><h2>{manualName}</h2><p>Công pháp hiện đang được backend lưu cho nhân vật. Chưa có API học hoặc nâng cấp công pháp, nên màn này không sinh hành động giả.</p><StatRow label="Loại" value="Tâm pháp" /><StatRow label="Trạng thái" value="Đang vận chuyển" /></div></div><button className="secondary-button" onClick={() => navigate("cultivation")}><Sparkles size={17} />Quay lại tu luyện</button></section>;
}

export function EquipmentView({ navigate }: { navigate: (view: string) => void }) {
  const slots = ["Vũ Khí", "Mũ", "Áo", "Giày", "Nhẫn", "Ngọc Bội"];
  return <section className="collection-page"><div className="page-heading"><div><p className="eyebrow">PHÁP BẢO · HỘ THÂN</p><h1>Trang Bị</h1></div><span>Chưa có trang bị</span></div><div className="equipment-board"><div className="equipment-slots">{slots.map(slot => <div className="equipment-slot" key={slot}><Shield size={20} /><span>{slot}</span><small>Trống</small></div>)}</div><div className="equipment-center"><Sword size={54} /><p>Chưa có pháp khí nào nhận chủ.</p></div></div><button className="secondary-button" onClick={() => navigate("inventory")}><Backpack size={17} />Mở túi đồ</button></section>;
}

function EmptyLore({ icon, title, text, action, onAction }: { icon: React.ReactNode; title: string; text: string; action: string; onAction: () => void }) {
  return <div className="empty-lore">{icon}<h2>{title}</h2><p>{text}</p><button className="secondary-button" onClick={onAction}>{action}</button></div>;
}
