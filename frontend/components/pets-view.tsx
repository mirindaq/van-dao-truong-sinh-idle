"use client";

import { PawPrint } from "lucide-react";
import { assetPath } from "@/lib/assets";
import { number } from "@/lib/format";
import type { GameState, PetSpecies } from "@/lib/types";
import { StatRow } from "./game-ui";

export function PetsView({ state, species, busy, onBond, onRest, onRecall }: {
  state: GameState;
  species: PetSpecies[] | null;
  busy: boolean;
  onBond: (key: string) => void;
  onRest: () => void;
  onRecall: () => void;
}) {
  const pet = state.spirit_pet;
  const cult = state.cultivation;
  return <section className="collection-page">
    <div className="page-heading"><div><p className="eyebrow">KẾT KHẾ ƯỚC</p><h1>Linh Thú</h1></div><span>{pet ? pet.name : "Chưa kết khế ước"}</span></div>
    <div className="equipment-summary">
      <StatRow label="Từ linh thú" value={pet?.active ? `+${number(state.player.pet_bonus)}` : "+0"} />
      <StatRow label="Tốc độ tu vi" value={`+${number(cult.rate_per_minute, 2)} / phút`} />
      <StatRow label="Hệ số linh thú" value={`×${number(cult.pet_factor, 2)}`} />
      <StatRow label="Lượng mỗi phút" value={`+${number(cult.pet_flat_per_minute, 2)}`} />
    </div>
    <p className="muted">{pet?.active ? `${pet.name} đang theo.` : pet ? `${pet.name} đang nghỉ.` : "Chọn một trong ba loài. Mỗi save chỉ kết một lần."}</p>
    <div className="equipment-grid">{(species ?? []).map(item => <article className="equipment-panel" key={item.key} aria-label={item.name}>
      <div className="section-heading"><h2>{item.name}</h2><PawPrint size={20} /></div>
      <div className="equipped-detail"><img src={assetPath(item.asset_key)} alt="" width={48} height={48} /><div><strong>+{number(item.combat_bonus)} chiến lực</strong><p>×{number(item.cultivation_factor, 2)} và +{number(item.cultivation_flat_per_minute, 2)} tu vi / phút</p></div></div>
      {pet?.key === item.key && pet.active && <button className="secondary-button" disabled={busy} onClick={onRest}>Cho nghỉ</button>}
      {pet?.key === item.key && !pet.active && <button className="secondary-button" disabled={busy} onClick={onRecall}>Gọi lại</button>}
      {!pet && <button className="primary-button" disabled={busy} onClick={() => onBond(item.key)}>Kết khế ước {item.name}</button>}
    </article>)}</div>
  </section>;
}
