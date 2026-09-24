"use client";

import { useEffect, useRef, useState } from "react";
import * as m from "motion/react-m";
import { useMotionPreference } from "@/lib/motion";
import { Leaf, X } from "lucide-react";
import type { GameState } from "@/lib/types";
import { elementNames, number, qualityNames } from "@/lib/format";

export function GameModal({ title, children, onClose, busy = false }: { title: string; children: React.ReactNode; onClose?: () => void; busy?: boolean }) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    const dialog = ref.current;
    dialog?.showModal();
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { dialog?.close(); document.body.style.overflow = overflow; previous?.focus(); };
  }, []);
  return <dialog ref={ref} className="game-modal" aria-labelledby="modal-title" onCancel={e => { e.preventDefault(); if (!busy) onClose?.(); }}>
    <div className="modal-heading"><span className="eyebrow">VẠN ĐẠO TRƯỜNG SINH</span>{onClose && <button className="icon-button" aria-label="Đóng" title="Đóng" disabled={busy} onClick={onClose}><X size={20} /></button>}</div>
    <h2 id="modal-title">{title}</h2>{children}
  </dialog>;
}

export function StatRow({ label, value, accent = false }: { label: string; value: React.ReactNode; accent?: boolean }) {
  return <div className={`stat-row ${accent ? "accent" : ""}`}><span>{label}</span><strong>{value}</strong></div>;
}

export function SpiritualRootBadge({ root }: { root: GameState["spiritual_root"] }) {
  return <div className={`root-badge element-${root.elements[0] ?? "wood"}`}><Leaf size={20} /><span><strong>{root.name}</strong><small>{qualityNames[root.quality] ?? root.quality} · {root.elements.map(e => elementNames[e] ?? e).join(" / ")}</small></span></div>;
}

export function RarityBadge({ rarity = "unknown" }: { rarity?: string }) {
  const label: Record<string, string> = { common: "Phàm", rare: "Huyền", epic: "Địa", legendary: "Thiên", immortal: "Tiên", unknown: "Chưa định phẩm" };
  return <span className={`rarity-badge rarity-${rarity}`}>{label[rarity] ?? rarity}</span>;
}

export function CultivationProgress({ cultivation, current = cultivation.current_exp }: { cultivation: GameState["cultivation"]; current?: number }) {
  const progress = Math.min(100, Math.max(0, current / cultivation.required_exp * 100));
  return <div className="cultivation-progress">
    <div className="progress-label"><span>Tu vi tích lũy</span><span><strong>{number(current, 1)}</strong><span className="muted"> / {number(cultivation.required_exp)}</span></span></div>
    <div className="progress-track" role="progressbar" aria-label="Tu vi tích lũy" aria-valuemin={0} aria-valuemax={cultivation.required_exp} aria-valuenow={Math.min(current, cultivation.required_exp)} aria-valuetext={`${number(current, 1)} trên ${number(cultivation.required_exp)} tu vi`}><div style={{ width: `${progress}%` }} /></div>
  </div>;
}

export function GameTimeline({ logs }: { logs: GameState["recent_logs"] }) {
  if (!logs.length) return <p className="muted">Trang tiên ký đầu tiên còn đang chờ bạn viết.</p>;
  return <ol className="timeline">{logs.map(log => <li key={log.id}><time dateTime={log.created_at}>{new Date(log.created_at).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" })}</time><p>{log.message}</p></li>)}</ol>;
}

export const BOND_AFFINITY = 8;

// Affinity out of 100 with the bonding threshold marked; the mark is lit at or above it,
// and "Mốc mới" appears only when the threshold is crossed while the meter is on screen.
export function AffinityMeter({ value, label }: { value: number; label: string }) {
  const { reduced } = useMotionPreference();
  const [start] = useState(value);
  const reached = value >= BOND_AFFINITY;
  const crossed = reached && start < BOND_AFFINITY && !reduced;
  const width = `${Math.min(100, Math.max(0, value))}%`;
  return <div className={`affinity-meter ${reached ? "reached" : ""}`}>
    <div className="affinity-track" role="meter" aria-label={label} aria-valuemin={0} aria-valuemax={100} aria-valuenow={value}>
      {reduced ? <div style={{ width }} /> : <m.div initial={{ width: `${Math.min(100, start)}%` }} animate={{ width }} transition={{ duration: .7, ease: [.2, .7, .2, 1] }} />}
      <span className="affinity-mark" style={{ left: `${BOND_AFFINITY}%` }} aria-hidden="true" />
    </div>
    <div className="affinity-legend"><span>{reached ? "Đủ duyên kết đạo lữ" : `Còn ${BOND_AFFINITY - value} thiện cảm để đủ duyên`}</span>{crossed && <m.span className="affinity-lit" initial={{ opacity: 0, scale: .8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: .5, duration: .4 }}>Mốc mới</m.span>}</div>
  </div>;
}
