"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ArrowRight, Check, CloudOff, Flame, Leaf, LockKeyhole, Mountain, RefreshCw, Sparkles, X } from "lucide-react";
import { gameApi, GameApiError } from "@/lib/api";
import { assetPath } from "@/lib/assets";
import { duration, number, percent } from "@/lib/format";
import type { BreakthroughPreview, BreakthroughResult, GameState } from "@/lib/types";
import { GameShell, destinations } from "./game-shell";
import { GameModal, GameTimeline, SpiritualRootBadge, StatRow } from "./game-ui";
import { CultivationView } from "./cultivation-view";
import { CharacterView, SkillsView } from "./character-view";
import { EquipmentView } from "./equipment-view";
import { ExplorationView } from "./exploration-view";
import { InventoryView } from "./inventory-view";
import { clearPending, readPending, writePending } from "@/lib/pending-breakthrough";
import type { BreakthroughRequest, EquipmentSlot, Exploration, WorldState } from "@/lib/types";
import { WorldReportDetails, WorldView } from "./world-view";
import { clearPendingExploration, readPendingExploration, writePendingExploration } from "@/lib/pending-exploration";

type Modal = "breakthrough" | "settings" | "reveal" | null;

export function GameHome() {
  const [state, setState] = useState<GameState | null>(null);
  const [loading, setLoading] = useState(true);
  const [noSave, setNoSave] = useState(false);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [disconnected, setDisconnected] = useState(false);
  const [view, setView] = useState("home");
  const [modal, setModal] = useState<Modal>(null);
  const [preview, setPreview] = useState<BreakthroughPreview | null>(null);
  const [result, setResult] = useState<BreakthroughResult | null>(null);
  const [name, setName] = useState("");
  const [elapsed, setElapsed] = useState(0);
  const [reducedMotion, setReducedMotion] = useState(false);
  const lock = useRef(false);
  const paused = useRef(false);
  const loadedAt = useRef(0);
  const pending = useRef<BreakthroughRequest | null>(null);
  const [recovering, setRecovering] = useState(false);
  const [equipmentUncertain, setEquipmentUncertain] = useState(false);
  const [explorationResult, setExplorationResult] = useState<Exploration | null>(null);
  const [worldState, setWorldState] = useState<WorldState | null>(null);
  const [usePill, setUsePill] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);
  const previewSequence = useRef(0);

  const acceptState = useCallback((next: GameState) => {
    setState(next); setNoSave(false); setDisconnected(false);
    loadedAt.current = performance.now(); setElapsed(0);
  }, []);

  const sync = useCallback(async () => {
    try {
      const next = await gameApi.state();
      acceptState(next);
      setEquipmentUncertain(false);
      try { setExplorationResult((await gameApi.latestExploration()).exploration); } catch (e) { if (!(e instanceof GameApiError && e.code === "exploration_not_found")) throw e; }
      setWorldState(await gameApi.world());
      const pendingExploration = readPendingExploration(next.player.id);
      if (pendingExploration) {
        try {
          const recovered = await gameApi.getExploration(pendingExploration);
          setExplorationResult(recovered.exploration); acceptState(recovered.state);
          clearPendingExploration(next.player.id);
        } catch (e) {
          if (!(e instanceof GameApiError && (e.code === "exploration_not_found" || e.code === "connection"))) throw e;
        }
      }
      const saved = readPending(next.player.id);
      if (saved) {
        pending.current = saved; setRecovering(true); setPreview(next.breakthrough); setModal("breakthrough");
      }
    }
    catch (e) {
      if (e instanceof GameApiError && e.code === "no_save") { setNoSave(true); setState(null); return; }
      setDisconnected(true); throw e;
    } finally { setLoading(false); }
  }, [acceptState]);

  const execute = useCallback(async (label: string, operation: () => Promise<void>) => {
    if (lock.current) return;
    lock.current = true; setBusy(label); setError(null);
    try { await operation(); }
    catch (e) { setError(e instanceof Error ? e.message : "Linh khí gián đoạn. Hãy thử lại."); }
    finally { lock.current = false; setBusy(""); }
  }, []);

  useEffect(() => {
    void execute("load", sync);
    const onHash = () => {
      const id = location.hash.slice(1);
      setView(destinations.some(d => d.id === id) ? id : "home");
    };
    onHash();
    const setting = localStorage.getItem("reduce-motion") === "true";
    setReducedMotion(setting); document.documentElement.dataset.reduceMotion = String(setting);
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, [execute, sync]);

  useEffect(() => { paused.current = modal !== null || Boolean(state?.offline_report) || noSave; }, [modal, state?.offline_report, noSave]);
  useEffect(() => {
    const refresh = () => {
      if (!document.hidden && !paused.current) void execute("sync", sync);
    };
    const poll = window.setInterval(refresh, 30000);
    const clock = window.setInterval(() => setElapsed(Math.max(0, (performance.now() - loadedAt.current) / 1000)), 1000);
    document.addEventListener("visibilitychange", refresh);
    window.addEventListener("online", refresh);
    return () => { clearInterval(poll); clearInterval(clock); document.removeEventListener("visibilitychange", refresh); window.removeEventListener("online", refresh); };
  }, [execute, sync]);

  const navigate = (id: string) => { setView(id); if (location.hash !== `#${id}`) location.hash = id; window.scrollTo({ top: 0 }); };
  const updateEquipment = (operation: () => Promise<GameState>) => void execute("equipment", async () => {
    if (equipmentUncertain) return;
    try { acceptState(await operation()); }
    catch (e) { setEquipmentUncertain(true); setDisconnected(true); throw e; }
  });
  const equip = (slot: EquipmentSlot, key: string | null) => updateEquipment(() => gameApi.equip(slot, key));
  const explore = () => void execute("exploration", async () => {
    if (!state) return;
    const requestId = readPendingExploration(state.player.id) ?? crypto.randomUUID();
    writePendingExploration(state.player.id, requestId);
    const response = await gameApi.explore(requestId);
    acceptState(response.state); setExplorationResult(response.exploration); clearPendingExploration(state.player.id);
  });
  const acknowledgeWorld = (id: number) => void execute("world", async () => {
    await gameApi.acknowledgeWorldReport(id); setWorldState(await gameApi.world());
  });
  const loadMoreWorld = () => void execute("world", async () => {
    if (!worldState?.next_cursor) return;
    const next = await gameApi.worldEvents(worldState.next_cursor);
    const known = new Set(worldState.events.map(event => event.id));
    setWorldState({ ...worldState, events: [...worldState.events, ...next.events.filter(event => !known.has(event.id))], next_cursor: next.next_cursor });
  });
  const showPreview = () => void execute("preview", async () => {
    setResult(null);
    if (state) {
      const saved = readPending(state.player.id);
      if (saved) { pending.current = saved; setRecovering(true); setPreview(state.breakthrough); setModal("breakthrough"); return; }
    }
    pending.current = null; setRecovering(false); setUsePill(false);
    setPreview(await gameApi.preview()); setModal("breakthrough");
  });
  const attempt = () => void execute("attempt", async () => {
    if (!preview || !state || previewLoading || (!recovering && preview.quantity !== Number(usePill))) return;
    const payload = readPending(state.player.id) ?? pending.current ?? {
      request_id: crypto.randomUUID(), revision: preview.revision, item_key: preview.item_key, quantity: preview.quantity,
    };
    writePending(state.player.id, payload);
    pending.current = payload; setRecovering(true);
    try {
      setResult(await gameApi.attempt(payload));
      clearPending(state.player.id); pending.current = null; setRecovering(false);
    }
    catch (e) {
      if (e instanceof GameApiError && e.code !== "connection") {
        clearPending(state.player.id); pending.current = null; setRecovering(false);
        setUsePill(false); setPreview(await gameApi.preview());
      }
      throw e;
    }
    await sync();
  });
  const changePill = async (checked: boolean) => {
    const sequence = ++previewSequence.current;
    setUsePill(checked); setPreviewLoading(true); setError(null);
    try {
      const next = await gameApi.preview(checked);
      if (sequence === previewSequence.current) setPreview(next);
    } catch (e) {
      if (sequence === previewSequence.current) setError(e instanceof Error ? e.message : "Không thể xem cơ hội đột phá.");
    } finally {
      if (sequence === previewSequence.current) setPreviewLoading(false);
    }
  };
  const closeModal = () => { ++previewSequence.current; setPreviewLoading(false); setModal(null); setError(null); };
  const errorBanner = error && <div className="error-banner" role="alert"><CloudOff size={18} /><span>{error}</span><button className="icon-button" onClick={() => setError(null)} aria-label="Ẩn thông báo" title="Ẩn thông báo"><X size={17} /></button></div>;

  if (loading) return <main className="loading-screen" aria-busy="true" aria-label="Đang tìm lại động phủ"><Mountain size={38} /><h1>Vạn Đạo Trường Sinh</h1><p>Đang tìm lại động phủ…</p><div className="skeleton hero-skeleton" /><div className="skeleton line-skeleton" /><div className="skeleton line-skeleton short" /></main>;

  if (!state && !noSave) return <main className="opening" style={{ backgroundImage: `url(${assetPath("maps/qingyun_mountain")})` }}><div className="opening-content"><CloudOff size={38} /><p className="eyebrow">VẠN ĐẠO TRƯỜNG SINH</p><h1>Đường về chìm trong sương</h1><p role="alert">{error ?? "Chưa thể tìm lại động phủ của bạn."}</p><button className="primary-button" disabled={!!busy} onClick={() => void execute("load", sync)}><RefreshCw size={18} />{busy ? "Đang tìm lại…" : "THỬ LẠI"}</button></div></main>;

  if (!state) return <main className="opening" style={{ backgroundImage: `url(${assetPath("maps/qingyun_mountain")})` }}><div className="opening-content"><Mountain size={42} /><p className="eyebrow">MỘT ĐỜI PHÀM NHÂN · MỘT NIỆM TRƯỜNG SINH</p><h1>Vạn Đạo<br />Trường Sinh</h1><p>Thiên địa linh khí suy kiệt.</p><p>Bạn vốn là một phàm nhân dưới chân Thanh Vân Sơn. Một ngày lên núi hái thuốc, bạn tìm thấy một động phủ bị dây leo che phủ.</p><p>Sau cánh cửa đá, một con đường chưa từng biết đang chờ…</p><form onSubmit={e => { e.preventDefault(); void execute("new", async () => { try { const next = await gameApi.newGame(name.trim()); acceptState(next); setWorldState(await gameApi.world()); setModal("reveal"); } catch (e) { if (e instanceof GameApiError && e.code === "save_exists") { await sync(); return; } throw e; } }); }}><label htmlFor="player-name">Danh xưng của đạo hữu</label><input id="player-name" value={name} onChange={e => setName(e.target.value)} maxLength={40} required autoComplete="off" placeholder="Nhập tên nhân vật" disabled={!!busy} /><button className="primary-button" disabled={!!busy || !name.trim()}><Sparkles size={18} />{busy ? "Đang khai mở tiên lộ…" : "BẮT ĐẦU VẤN ĐẠO"}<ArrowRight size={18} /></button></form>{errorBanner}</div></main>;

  const eta = state.cultivation.seconds_until_next_stage === null ? null : Math.max(0, state.cultivation.seconds_until_next_stage - elapsed);
  const offline = state.offline_report;
  const selected = destinations.find(d => d.id === view) ?? destinations[0];
  return <GameShell state={state} view={view} navigate={navigate} refreshing={!!busy} disconnected={disconnected} onRefresh={() => void execute("sync", sync)} onSettings={() => setModal("settings")}>
    {!modal && !offline && errorBanner}
    {equipmentUncertain && <div className="equipment-recovery" role="status"><p>Chưa xác nhận được thay đổi trang bị. Đồng bộ để xem trạng thái đã lưu trước khi thao tác tiếp.</p><button className="secondary-button" disabled={!!busy} onClick={() => void execute("sync", sync)}>Đồng bộ trang bị</button></div>}
    {disconnected && <p className="connection-note" role="status">Đang hiển thị lần lưu gần nhất. Tu vi sẽ được đồng bộ khi kết nối trở lại.</p>}
    {!modal && !offline && view !== "world" && worldState?.report && <section className="world-report" aria-label="Trong lúc bạn vắng mặt"><div><p className="eyebrow">TRONG LÚC BẠN VẮNG MẶT</p><h2>Thiên hạ đã chuyển mình</h2><WorldReportDetails report={worldState.report} /></div><div className="world-report-actions"><button className="secondary-button" onClick={() => navigate("world")}><ArrowRight size={16} />XEM THIÊN HẠ</button><button className="secondary-button" disabled={!!busy} onClick={() => acknowledgeWorld(worldState.report!.id)}><Check size={16} />ĐÃ ĐỌC</button></div></section>}
    {view === "home" || view === "cultivation" ? <CultivationView state={state} detailed={view === "cultivation"} eta={eta} navigate={navigate} onBreakthrough={showPreview} busy={!!busy} /> : view === "exploration" ? <ExplorationView state={state} result={explorationResult} busy={!!busy} onExplore={explore} /> : view === "world" ? <WorldView world={worldState} busy={!!busy} onSync={() => void execute("sync", sync)} onAcknowledge={acknowledgeWorld} onLoadMore={loadMoreWorld} /> : view === "character" ? <CharacterView state={state} navigate={navigate} /> : view === "inventory" ? <InventoryView state={state} navigate={navigate} onClaim={() => updateEquipment(gameApi.claimEquipment)} disabled={!!busy || equipmentUncertain} /> : view === "skills" ? <SkillsView state={state} navigate={navigate} /> : view === "equipment" ? <EquipmentView state={state} navigate={navigate} onEquip={equip} disabled={!!busy || equipmentUncertain} /> : view === "journal" ? <section className="journal-page"><div className="page-heading"><div><p className="eyebrow">DẤU CHÂN TRÊN TIÊN LỘ</p><h1>Nhật Ký</h1></div><span>Ghi chép gần đây</span></div><GameTimeline logs={state.recent_logs} /></section> : <section className="locked-page" style={{ backgroundImage: `url(${assetPath("maps/qingyun_mountain")})` }}><selected.icon size={40} /><p className="eyebrow">TIÊN DUYÊN CHƯA TỚI</p><h1>{selected.name}</h1><span className="locked-tag"><LockKeyhole size={14} />Chưa mở</span><p>{view === "pets" ? "Bạn chưa ký khế ước với bất kỳ linh thú nào." : view === "partner" ? "Tiên lộ dài đằng đẵng. Hiện tại chưa có người cùng bạn đồng hành." : view === "rift" ? "Sau màn sương, một cánh cửa cổ vẫn đang ngủ yên." : "Một chương mới trên tiên lộ vẫn còn đang khép lại."}</p><button className="secondary-button" onClick={() => navigate("cultivation")}><Leaf size={17} />Trở về tu luyện<ArrowRight size={16} /></button></section>}
    {modal === "reveal" && <GameModal title="Trắc Linh Thạch"><div className="reveal-stone"><Leaf size={55} /></div><p className="center muted">Linh thạch khẽ sáng. Một luồng sinh khí lan tỏa.</p><SpiritualRootBadge root={state.spiritual_root} /><StatRow label="Hệ số tu luyện" value={`×${number(state.spiritual_root.cultivation_modifier, 2)}`} /><StatRow label="Hệ số đột phá" value={`×${number(state.spiritual_root.breakthrough_modifier, 2)}`} /><button className="primary-button full-width" onClick={() => { closeModal(); navigate("home"); }}>BƯỚC VÀO TIÊN LỘ<ArrowRight size={18} /></button></GameModal>}
    {modal === "breakthrough" && preview && <GameModal title={result ? result.success ? "Đột phá thành công" : "Đột phá thất bại" : "Đột phá cảnh giới"} onClose={closeModal} busy={!!busy}>
      {result ? <div className={`breakthrough-result ${result.success ? "success" : "failure"}`}>
        <div className="probability-ring">{result.success ? <Sparkles size={50} /> : <Flame size={50} />}</div>
        <h3>{result.realm.name} · Tầng {result.realm.stage}</h3><p>{result.message}</p>
        {result.cultivation_lost > 0 && <StatRow label="Tu vi tổn thất" value={`−${number(result.cultivation_lost, 2)}`} />}
        <StatRow label="Tụ Khí Đan đã dùng" value={number(result.items_consumed)} />
        {disconnected && <button className="secondary-button full-width" disabled={!!busy} onClick={() => void execute("sync", sync)}><RefreshCw size={17} />Đồng bộ lại hành trình</button>}
        <button className="primary-button full-width" disabled={!!busy} onClick={closeModal}><Check size={18} />TIẾP TỤC TIÊN LỘ</button>
      </div> : recovering ? <>
        <p className="center muted">Lần đột phá trước đang chờ xác nhận kết quả.</p>
        <button className="primary-button full-width" disabled={!!busy} onClick={attempt}><RefreshCw size={18} />KIỂM TRA KẾT QUẢ</button>
      </> : <>
        <p className="realm-transition">{state.realm.name} · Tầng {state.realm.stage}<ArrowRight size={17} /><strong>{preview.target ? `${preview.target.name} · Tầng ${preview.target.stage}` : "Viên mãn"}</strong></p>
        <div className="probability-ring"><strong>{percent(preview.final_chance)}</strong><span>Cơ hội thành công</span></div>
        <StatRow label="Tỷ lệ cơ bản" value={percent(preview.base_chance)} />
        <StatRow label="Linh căn" value={`+${percent(preview.root_bonus)}`} />
        <label className="setting-row pill-selection"><span>Dùng 1 Tụ Khí Đan <small>Đang có: {number(preview.pills_owned)}</small></span><input type="checkbox" checked={usePill} disabled={!!busy || (preview.pills_owned === 0 && !usePill)} onChange={e => void changePill(e.target.checked)} /></label>
        {previewLoading && <p role="status">Đang tính lại cơ hội đột phá…</p>}
        <StatRow label="Đan hỗ trợ" value={`+${percent(preview.item_bonus)}`} />
        <StatRow label="Tổng tỷ lệ" value={percent(preview.final_chance)} accent />
        <p className="warning">Thất bại tổn thất {number(preview.failure_loss, 2)} tu vi.{preview.quantity === 1 && " Tiêu hao 1 Tụ Khí Đan dù thành công hay thất bại."}</p>
        {!preview.available && <p className="center muted">{preview.target ? `Cần ${number(preview.required_exp)} tu vi để đột phá.` : "Bạn đã tới tận cùng tiên lộ hiện tại."}</p>}
        <button className="primary-button full-width" disabled={!!busy || previewLoading || preview.quantity !== Number(usePill) || !preview.available || preview.quantity > preview.pills_owned} onClick={attempt}><Flame size={18} />{busy ? "ĐANG CHUẨN BỊ…" : "BẮT ĐẦU ĐỘT PHÁ"}</button>
      </>}{errorBanner}
    </GameModal>}
    {modal === "settings" && <GameModal title="Cài đặt" onClose={closeModal}><label className="setting-row"><span>Giảm chuyển động</span><input type="checkbox" checked={reducedMotion} onChange={e => { setReducedMotion(e.target.checked); document.documentElement.dataset.reduceMotion = String(e.target.checked); localStorage.setItem("reduce-motion", String(e.target.checked)); }} /></label><StatRow label="Hành trình" value={disconnected ? "Chờ kết nối" : "Đã lưu"} /><StatRow label="Lần đồng bộ" value={new Date(state.server_time).toLocaleTimeString("vi-VN")} /><button className="secondary-button full-width" disabled={!!busy} onClick={() => void execute("sync", sync)}><RefreshCw size={17} />Đồng bộ hành trình</button>{errorBanner}</GameModal>}
    {!modal && offline && <GameModal title="Bế Quan Kết Thúc" busy={!!busy}><div className="offline-mark"><Mountain size={44} /></div><p className="center muted">Bạn đã bế quan {duration(offline.elapsed_seconds)}.</p><div className="offline-reward"><Sparkles size={24} /><strong>+{number(offline.earned_exp, 2)}</strong><span>Tu vi</span></div><p className="center muted">Đạo hạnh đã được ghi vào hành trình.</p><button className="primary-button full-width" disabled={!!busy} onClick={() => void execute("ack", async () => { await gameApi.acknowledgeOffline(offline.id); await sync(); })}><Check size={18} />{busy ? "ĐANG XÁC NHẬN…" : "NHẬN TU VI"}</button>{errorBanner}</GameModal>}
  </GameShell>;
}
