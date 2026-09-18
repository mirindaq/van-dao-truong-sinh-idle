"use client";

import { Backpack, Shield, Sword } from "lucide-react";
import { assetPath } from "@/lib/assets";
import { number } from "@/lib/format";
import type { EquipmentSlot, GameState } from "@/lib/types";
import { StatRow } from "./game-ui";

const slots: Array<[EquipmentSlot, string]> = [["weapon", "Vũ Khí"], ["head", "Mũ"], ["body", "Áo"], ["feet", "Giày"], ["ring", "Nhẫn"], ["amulet", "Ngọc Bội"]];

export function EquipmentView({ state, navigate, onEquip, disabled }: {
  state: GameState; navigate: (view: string) => void;
  onEquip: (slot: EquipmentSlot, item: string | null) => void; disabled: boolean;
}) {
  return <section className="collection-page">
    <div className="page-heading"><div><p className="eyebrow">PHÁP BẢO · HỘ THÂN</p><h1>Trang Bị</h1></div><span>{state.equipment.length} / 6 ô đang mặc</span></div>
    <div className="equipment-summary"><StatRow label="Chiến lực nền" value={number(state.player.base_combat_power)} /><StatRow label="Từ trang bị" value={`+${number(state.player.equipment_bonus)}`} /><StatRow label="Tổng chiến lực" value={number(state.player.combat_power)} accent /></div>
    <p className="muted">Trang bị cộng chiến lực. Mặc và tháo không tiêu hao vật phẩm.</p>
    <div className="equipment-grid">{slots.map(([slot, label]) => {
      const current = state.equipment.find(e => e.slot === slot);
      const item = state.inventory.find(i => i.key === current?.item_key);
      const candidates = state.inventory.filter(i => i.equipment_slot === slot && i.quantity > 0 && i.key !== current?.item_key);
      return <article className="equipment-panel" key={slot} aria-label={label}>
        <div className="section-heading"><h2>{label}</h2>{slot === "weapon" ? <Sword size={20} /> : <Shield size={20} />}</div>
        {item ? <><div className="equipped-detail"><img src={assetPath(item.asset_key)} alt="" width={48} height={48} /><div><strong>{item.name}</strong><p>+{number(item.combat_bonus)} chiến lực</p></div></div><button className="secondary-button" disabled={disabled} onClick={() => onEquip(slot, null)} aria-label={`Tháo ${item.name}`}>Tháo trang bị</button></> : <p className="muted">Ô trống</p>}
        {candidates.map(candidate => <button key={candidate.key} className="secondary-button equipment-choice" disabled={disabled} onClick={() => onEquip(slot, candidate.key)}>{item ? "Thay bằng" : "Mặc"} {candidate.name}<span>+{number(candidate.combat_bonus)}</span></button>)}
        {!item && candidates.length === 0 && <small className="muted">Chưa có trang bị phù hợp.</small>}
      </article>;
    })}</div>
    <button className="secondary-button" onClick={() => navigate("inventory")}><Backpack size={17} />Mở túi đồ</button>
  </section>;
}
