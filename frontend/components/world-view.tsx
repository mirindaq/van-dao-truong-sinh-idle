"use client";

import { useEffect, useMemo, useState } from "react";
import { ArrowLeft, Check, Clock3, HeartHandshake, MapPin, MessageCircle, ScrollText, Sparkles, UserRound } from "lucide-react";
import { gameApi, GameApiError } from "@/lib/api";
import { assetPath } from "@/lib/assets";
import { number, percent } from "@/lib/format";
import { AffinityMeter } from "./game-ui";
import { GainChip, Reveal } from "./moment-ui";
import type { InteractionRequest, InteractionResponse, RelationshipProfile, WorldNpc, WorldReport, WorldState } from "@/lib/types";

const activity: Record<string, string> = { cultivating: "Đang tu luyện", exploring: "Đang thám du", injured: "Đang dưỡng thương" };

function pendingKey(playerId: number, npcKey: string) { return `npc-interaction:${playerId}:${npcKey}`; }
function readPending(playerId: number, npcKey: string): InteractionRequest | null {
  try { const value = localStorage.getItem(pendingKey(playerId, npcKey)); return value ? JSON.parse(value) as InteractionRequest : null; } catch { return null; }
}
function writePending(playerId: number, npcKey: string, value: InteractionRequest) { localStorage.setItem(pendingKey(playerId, npcKey), JSON.stringify(value)); }
function clearPending(playerId: number, npcKey: string) { localStorage.removeItem(pendingKey(playerId, npcKey)); }

export function WorldView({ world, playerId, busy, onSync, onAcknowledge, onLoadMore }: {
  world: WorldState | null; playerId: number; busy: boolean; onSync: () => void; onAcknowledge: (id: number) => void; onLoadMore: () => void;
}) {
  const [selected, setSelected] = useState<string | null>(null);
  const [filter, setFilter] = useState<"all" | "npc" | "world">("all");
  const [relationship, setRelationship] = useState<RelationshipProfile | null>(null);
  const [interaction, setInteraction] = useState<InteractionResponse["interaction"] | null>(null);
  const [relationshipBusy, setRelationshipBusy] = useState(false);
  const [relationshipError, setRelationshipError] = useState<string | null>(null);
  const npc = world?.npcs.find(item => item.key === selected) ?? null;
  const events = useMemo(() => world?.events.filter(event => filter === "all" || (filter === "world" ? event.source_key === "world" : event.source_key !== "world")) ?? [], [world, filter]);

  useEffect(() => {
    if (!selected) { setRelationship(null); setInteraction(null); setRelationshipError(null); return; }
    let active = true;
    const load = async () => {
      setRelationshipBusy(true); setRelationshipError(null);
      try {
        const pending = readPending(playerId, selected);
        if (pending) {
          let recovered: InteractionResponse;
          try { recovered = await gameApi.getInteraction(pending.request_id); }
          catch (error) {
            if (!(error instanceof GameApiError && error.code === "interaction_not_found")) throw error;
            recovered = await gameApi.interact(selected, pending);
          }
          clearPending(playerId, selected);
          if (active) { setRelationship(recovered.profile); setInteraction(recovered.interaction); }
        } else {
          const profile = await gameApi.relationship(selected);
          if (active) setRelationship(profile);
        }
      } catch (error) {
        if (active) setRelationshipError(error instanceof Error ? error.message : "Chưa đọc được quan hệ.");
      } finally { if (active) setRelationshipBusy(false); }
    };
    void load();
    return () => { active = false; };
  }, [playerId, selected]);

  const openPrompt = async () => {
    if (!selected) return;
    setRelationshipBusy(true); setRelationshipError(null);
    try { setRelationship(await gameApi.openInteraction(selected)); }
    catch (error) { setRelationshipError(error instanceof Error ? error.message : "Chưa thể trò chuyện."); }
    finally { setRelationshipBusy(false); }
  };
  const choose = async (choiceKey: string) => {
    if (!selected || !relationship?.prompt) return;
    const payload: InteractionRequest = {
      request_id: crypto.randomUUID(), prompt_key: relationship.prompt.key,
      prompt_version: relationship.prompt.version, choice_key: choiceKey,
    };
    writePending(playerId, selected, payload); setRelationshipBusy(true); setRelationshipError(null);
    try {
      const result = await gameApi.interact(selected, payload);
      clearPending(playerId, selected); setRelationship(result.profile); setInteraction(result.interaction);
    } catch (error) {
      if (error instanceof GameApiError && error.code !== "connection") {
        clearPending(playerId, selected);
        const current = await gameApi.relationship(selected).catch(() => null);
        if (current) { setRelationship(current); setInteraction(current.history[0] ?? null); }
      }
      setRelationshipError(error instanceof Error ? error.message : "Chưa xác nhận được lời đáp.");
    }
    finally { setRelationshipBusy(false); }
  };

  if (!world) return <section className="world-page"><div className="page-heading"><div><p className="eyebrow">THIÊN ĐỊA VẬN HÀNH</p><h1>Thiên Hạ</h1></div></div><div className="world-empty"><UserRound size={42} /><p>Chưa đọc được diễn biến thiên hạ.</p><button className="secondary-button" disabled={busy} onClick={onSync}>ĐỒNG BỘ THIÊN HẠ</button></div></section>;
  if (npc) return <NpcProfile npc={npc} events={world.events.filter(event => event.source_key === npc.key)} relationship={relationship} interaction={interaction} busy={relationshipBusy} error={relationshipError} onOpenPrompt={() => void openPrompt()} onChoose={choice => void choose(choice)} onBack={() => setSelected(null)} />;
  return <section className="world-page">
    <div className="page-heading"><div><p className="eyebrow">THIÊN ĐỊA VẬN HÀNH</p><h1>Thiên Hạ</h1></div><span className="activity-tag"><span />Cập nhật {new Date(world.updated_at).toLocaleString("vi-VN")}</span></div>
    {world.report && <section className="world-report" aria-label="Trong lúc bạn vắng mặt"><div><p className="eyebrow">TRONG LÚC BẠN VẮNG MẶT</p><h2>Thiên hạ đã chuyển mình</h2><WorldReportDetails report={world.report} /></div><button className="secondary-button" disabled={busy} onClick={() => onAcknowledge(world.report!.id)}><Check size={16} />ĐÃ ĐỌC</button></section>}
    <section><div className="section-heading"><h2>Tu sĩ trong thiên hạ</h2><UserRound size={18} /></div><div className="npc-grid">{world.npcs.map(item => <button className="npc-card" key={item.key} onClick={() => setSelected(item.key)}><img src={assetPath(item.portrait_key ?? "npc/fallback")} alt="" /><div><span className={`npc-state ${item.activity}`}>{activity[item.activity]}</span><h3>{item.name}</h3><p>{item.realm_name} · Tầng {item.stage}</p><small><MapPin size={13} />{item.location}</small></div></button>)}</div></section>
    <section className="world-news"><div className="section-heading"><h2>Tin tức gần đây</h2><ScrollText size={18} /></div><div className="world-filters" role="group" aria-label="Lọc tin tức">{(["all", "npc", "world"] as const).map(value => <button key={value} className={filter === value ? "active" : ""} aria-pressed={filter === value} onClick={() => setFilter(value)}>{value === "all" ? "Tất cả" : value === "npc" ? "NPC" : "Thế giới"}</button>)}</div>{events.length ? <ol className="world-event-list">{events.map(event => <li key={event.id}><span className="event-mark"><Sparkles size={15} /></span><div><p>{event.message}</p><small><Clock3 size={12} />{new Date(event.occurred_at).toLocaleString("vi-VN")}</small></div></li>)}</ol> : <p className="muted world-no-news">Thiên hạ đang yên tĩnh.</p>}{world.next_cursor !== null && <button className="secondary-button world-more" disabled={busy} onClick={onLoadMore}>XEM TIN CŨ HƠN</button>}</section>
  </section>;
}

function NpcProfile({ npc, events, relationship, interaction, busy, error, onOpenPrompt, onChoose, onBack }: { npc: WorldNpc; events: WorldState["events"]; relationship: RelationshipProfile | null; interaction: InteractionResponse["interaction"] | null; busy: boolean; error: string | null; onOpenPrompt: () => void; onChoose: (choice: string) => void; onBack: () => void }) {
  const progress = npc.required_exp ? Math.min(1, npc.cultivation_exp / npc.required_exp) : 1;
  return <section className="npc-profile-page"><button className="back-button" onClick={onBack}><ArrowLeft size={16} />Trở lại Thiên Hạ</button><div className="npc-profile-hero"><img src={assetPath(npc.portrait_key ?? "npc/fallback")} alt="" /><div><p className="eyebrow">HỒ SƠ TU SĨ</p><h1>{npc.name}</h1><p>{npc.description}</p><div className="npc-facts"><span>{npc.spiritual_root}</span><span>{npc.realm_name} · Tầng {npc.stage}</span><span>{activity[npc.activity]}</span><span>{npc.location}</span>{npc.injured_until && <span>Dưỡng thương đến {new Date(npc.injured_until).toLocaleString("vi-VN")}</span>}<span>Cập nhật {new Date(npc.updated_at).toLocaleString("vi-VN")}</span></div></div></div><section className="npc-progress"><div className="progress-label"><span>Tu vi</span><strong>{number(npc.cultivation_exp, 1)} / {number(npc.required_exp)}</strong></div><div className="progress-track"><div style={{ width: percent(progress) }} /></div></section>
    <section className="relationship-panel" aria-label={`Quan hệ với ${npc.name}`}><div className="section-heading"><div><p className="eyebrow">NHÂN DUYÊN</p><h2>Thiện cảm</h2></div><HeartHandshake size={20} /></div>{relationship ? <><div className="affinity-row"><strong>{relationship.affinity} / 100<GainChip amount={relationship.affinity} unit="thiện cảm" /></strong><span>{relationship.address}</span></div><AffinityMeter value={relationship.affinity} label={`Thiện cảm với ${npc.name}`} />{interaction && <Reveal id={interaction.request_id} className="interaction-result" role="status"><strong>{interaction.choice_text}</strong><p>{interaction.response_text}</p><small>{interaction.affinity_delta >= 0 ? "+" : ""}{interaction.affinity_delta} thiện cảm</small></Reveal>}{relationship.prompt ? <div className="interaction-prompt"><p>{relationship.prompt.text}</p><div className="interaction-choices">{relationship.prompt.choices.map(choice => <button className="secondary-button" key={choice.key} disabled={busy} onClick={() => onChoose(choice.key)}>{choice.text}</button>)}</div></div> : relationship.can_interact ? <button className="primary-button" disabled={busy} onClick={onOpenPrompt}><MessageCircle size={17} />{busy ? "ĐANG LẮNG NGHE…" : "TRÒ CHUYỆN"}</button> : <p className="cooldown-note"><Clock3 size={15} />Có thể trò chuyện lại lúc {new Date(relationship.next_available_at!).toLocaleString("vi-VN")}</p>}{relationship.history.length > 0 && <div className="interaction-history"><h3>Lịch sử trò chuyện</h3><ol>{relationship.history.map(item => <li key={item.request_id}><p><strong>Bạn:</strong> {item.choice_text}</p><p><strong>{npc.name}:</strong> {item.response_text}</p><small>{new Date(item.created_at).toLocaleString("vi-VN")} · {item.affinity_delta >= 0 ? "+" : ""}{item.affinity_delta} thiện cảm</small></li>)}</ol></div>}</> : <p role="status">Đang đọc nhân duyên…</p>}{error && <p className="relationship-error" role="alert">{error}</p>}</section>
    <section className="world-news"><div className="section-heading"><h2>Dấu chân gần đây</h2><ScrollText size={18} /></div>{events.length ? <ol className="world-event-list">{events.map(event => <li key={event.id}><span className="event-mark"><Sparkles size={15} /></span><div><p>{event.message}</p><small>{new Date(event.occurred_at).toLocaleString("vi-VN")}</small></div></li>)}</ol> : <p className="muted world-no-news">Chưa có sự kiện đáng chú ý.</p>}</section></section>;
}

const summaryLabels: Record<string, string> = { breakthrough: "đột phá", breakthrough_failed: "đột phá thất bại", opportunity: "cơ duyên", injured: "bị thương", recovered: "bình phục", spiritual_tide: "linh triều", merchant_caravan: "thương đội", beast_aura: "khí tức yêu thú" };

export function WorldReportDetails({ report }: { report: WorldReport }) {
  const details = Object.entries(report.summary).filter(([, count]) => count > 0).map(([kind, count]) => `${count} ${summaryLabels[kind] ?? kind}`);
  return <><p>{report.processed_ticks} nhịp · {report.npc_updates} NPC tiến triển · {report.event_count} tin đáng chú ý</p>{details.length > 0 && <small>{details.join(" · ")}</small>}{report.skipped_seconds > 0 && <small>{number(report.skipped_seconds / 3600, 1)} giờ vượt giới hạn không được mô phỏng.</small>}<small>Bộ luật v{report.rules_version} · {report.rules_fingerprint}</small></>;
}
