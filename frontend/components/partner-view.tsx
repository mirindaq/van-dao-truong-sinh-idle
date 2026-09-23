"use client";

import { Heart, Swords } from "lucide-react";
import { number } from "@/lib/format";
import type { DaoPartner, GameState } from "@/lib/types";
import { StatRow } from "./game-ui";

export function PartnerView({ state, partners, busy, onBond, onDismiss }: {
  state: GameState;
  partners: DaoPartner[] | null;
  busy: boolean;
  onBond: (npcKey: string) => void;
  onDismiss: (npcKey: string) => void;
}) {
  const active = state.dao_partners.filter(partner => partner.active);
  return <section className="collection-page">
    <div className="page-heading"><div><p className="eyebrow">NHÂN DUYÊN ĐỒNG HÀNH</p><h1>Đạo Lữ</h1></div><span>{active.length ? `${active.length} người đang kết` : "Chưa kết duyên"}</span></div>
    <div className="equipment-summary">
      <StatRow label="Đạo lữ đang kết" value={number(active.length)} />
      <StatRow label="Từ đạo lữ" value={`+${number(state.player.partner_bonus)}`} />
      <StatRow label="Hệ số đạo lữ" value={`×${number(state.cultivation.partner_factor, 2)}`} />
      <StatRow label="Lượng mỗi phút" value={`+${number(state.cultivation.partner_flat_per_minute, 2)}`} />
      <StatRow label="Tốc độ tu vi" value={`+${number(state.cultivation.rate_per_minute, 3)}`} accent />
    </div>
    <p className="muted">Đạt 8 thiện cảm để kết duyên. Mỗi đạo lữ cộng riêng chiến lực và tốc độ tu vi.</p>
    <div className="equipment-grid">{(partners ?? []).map(partner => <article className="equipment-panel" key={partner.npc_key} aria-label={partner.name}>
      <div className="section-heading"><h2>{partner.name}</h2>{partner.active ? <Heart size={20} /> : <Swords size={20} />}</div>
      <StatRow label="Thiện cảm" value={`${number(partner.affinity)} / 100`} />
      <StatRow label="Trạng thái" value={partner.active ? "Đang kết duyên" : partner.affinity >= 8 ? "Có thể kết duyên" : "Chưa đủ duyên"} />
      {partner.active
        ? <button className="secondary-button" disabled={busy} onClick={() => onDismiss(partner.npc_key)}>Gỡ duyên {partner.name}</button>
        : <button className="primary-button" disabled={busy || partner.affinity < 8} onClick={() => onBond(partner.npc_key)}>Kết duyên {partner.name}</button>}
    </article>)}</div>
    {partners === null && <p role="status">Đang đọc nhân duyên…</p>}
  </section>;
}
