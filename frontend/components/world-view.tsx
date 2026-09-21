"use client";

import { useMemo, useState } from "react";
import { ArrowLeft, Check, Clock3, Globe2, MapPin, ScrollText, Sparkles, UserRound } from "lucide-react";
import { assetPath } from "@/lib/assets";
import { number, percent } from "@/lib/format";
import type { WorldNpc, WorldReport, WorldState } from "@/lib/types";

const activity: Record<string, string> = { cultivating: "Đang tu luyện", exploring: "Đang thám du", injured: "Đang dưỡng thương" };

export function WorldView({ world, busy, onSync, onAcknowledge, onLoadMore }: {
  world: WorldState | null; busy: boolean; onSync: () => void; onAcknowledge: (id: number) => void; onLoadMore: () => void;
}) {
  const [selected, setSelected] = useState<string | null>(null);
  const [filter, setFilter] = useState<"all" | "npc" | "world">("all");
  const npc = world?.npcs.find(item => item.key === selected) ?? null;
  const events = useMemo(() => world?.events.filter(event => filter === "all" || (filter === "world" ? event.source_key === "world" : event.source_key !== "world")) ?? [], [world, filter]);
  if (!world) return <section className="world-page"><div className="page-heading"><div><p className="eyebrow">THIÊN ĐỊA VẬN HÀNH</p><h1>Thiên Hạ</h1></div></div><div className="world-empty"><Globe2 size={42} /><p>Chưa đọc được diễn biến thiên hạ.</p><button className="secondary-button" disabled={busy} onClick={onSync}>ĐỒNG BỘ THIÊN HẠ</button></div></section>;
  if (npc) return <NpcProfile npc={npc} events={world.events.filter(event => event.source_key === npc.key)} onBack={() => setSelected(null)} />;
  return <section className="world-page">
    <div className="page-heading"><div><p className="eyebrow">THIÊN ĐỊA VẬN HÀNH</p><h1>Thiên Hạ</h1></div><span className="activity-tag"><span />Cập nhật {new Date(world.updated_at).toLocaleString("vi-VN")}</span></div>
    {world.report && <section className="world-report" aria-label="Trong lúc bạn vắng mặt"><div><p className="eyebrow">TRONG LÚC BẠN VẮNG MẶT</p><h2>Thiên hạ đã chuyển mình</h2><WorldReportDetails report={world.report} /></div><button className="secondary-button" disabled={busy} onClick={() => onAcknowledge(world.report!.id)}><Check size={16} />ĐÃ ĐỌC</button></section>}
    <section><div className="section-heading"><h2>Tu sĩ trong thiên hạ</h2><UserRound size={18} /></div><div className="npc-grid">{world.npcs.map(item => <button className="npc-card" key={item.key} onClick={() => setSelected(item.key)}><img src={assetPath(item.portrait_key ?? "npc/fallback")} alt="" /><div><span className={`npc-state ${item.activity}`}>{activity[item.activity]}</span><h3>{item.name}</h3><p>{item.realm_name} · Tầng {item.stage}</p><small><MapPin size={13} />{item.location}</small></div></button>)}</div></section>
    <section className="world-news"><div className="section-heading"><h2>Tin tức gần đây</h2><ScrollText size={18} /></div><div className="world-filters" role="group" aria-label="Lọc tin tức">{(["all", "npc", "world"] as const).map(value => <button key={value} className={filter === value ? "active" : ""} aria-pressed={filter === value} onClick={() => setFilter(value)}>{value === "all" ? "Tất cả" : value === "npc" ? "NPC" : "Thế giới"}</button>)}</div>{events.length ? <ol className="world-event-list">{events.map(event => <li key={event.id}><span className="event-mark"><Sparkles size={15} /></span><div><p>{event.message}</p><small><Clock3 size={12} />{new Date(event.occurred_at).toLocaleString("vi-VN")}</small></div></li>)}</ol> : <p className="muted world-no-news">Thiên hạ đang yên tĩnh.</p>}{world.next_cursor !== null && <button className="secondary-button world-more" disabled={busy} onClick={onLoadMore}>XEM TIN CŨ HƠN</button>}</section>
  </section>;
}

function NpcProfile({ npc, events, onBack }: { npc: WorldNpc; events: WorldState["events"]; onBack: () => void }) {
  const progress = npc.required_exp ? Math.min(1, npc.cultivation_exp / npc.required_exp) : 1;
  return <section className="npc-profile-page"><button className="back-button" onClick={onBack}><ArrowLeft size={16} />Trở lại Thiên Hạ</button><div className="npc-profile-hero"><img src={assetPath(npc.portrait_key ?? "npc/fallback")} alt="" /><div><p className="eyebrow">HỒ SƠ TU SĨ</p><h1>{npc.name}</h1><p>{npc.description}</p><div className="npc-facts"><span>{npc.spiritual_root}</span><span>{npc.realm_name} · Tầng {npc.stage}</span><span>{activity[npc.activity]}</span><span>{npc.location}</span>{npc.injured_until && <span>Dưỡng thương đến {new Date(npc.injured_until).toLocaleString("vi-VN")}</span>}<span>Cập nhật {new Date(npc.updated_at).toLocaleString("vi-VN")}</span></div></div></div><section className="npc-progress"><div className="progress-label"><span>Tu vi</span><strong>{number(npc.cultivation_exp, 1)} / {number(npc.required_exp)}</strong></div><div className="progress-track"><div style={{ width: percent(progress) }} /></div></section><section className="world-news"><div className="section-heading"><h2>Dấu chân gần đây</h2><ScrollText size={18} /></div>{events.length ? <ol className="world-event-list">{events.map(event => <li key={event.id}><span className="event-mark"><Sparkles size={15} /></span><div><p>{event.message}</p><small>{new Date(event.occurred_at).toLocaleString("vi-VN")}</small></div></li>)}</ol> : <p className="muted world-no-news">Chưa có sự kiện đáng chú ý.</p>}</section></section>;
}

const summaryLabels: Record<string, string> = { breakthrough: "đột phá", breakthrough_failed: "đột phá thất bại", opportunity: "cơ duyên", injured: "bị thương", recovered: "bình phục", spiritual_tide: "linh triều", merchant_caravan: "thương đội", beast_aura: "khí tức yêu thú" };

export function WorldReportDetails({ report }: { report: WorldReport }) {
  const details = Object.entries(report.summary).filter(([, count]) => count > 0).map(([kind, count]) => `${count} ${summaryLabels[kind] ?? kind}`);
  return <><p>{report.processed_ticks} nhịp · {report.npc_updates} NPC tiến triển · {report.event_count} tin đáng chú ý</p>{details.length > 0 && <small>{details.join(" · ")}</small>}{report.skipped_seconds > 0 && <small>{number(report.skipped_seconds / 3600, 1)} giờ vượt giới hạn không được mô phỏng.</small>}<small>Bộ luật v{report.rules_version} · {report.rules_fingerprint}</small></>;
}
