"use client";

import { useState } from "react";
import { Mountain, Orbit, UserRound, BookOpen, Sword, Backpack, FlaskConical, PawPrint, Heart, Compass, Eclipse, Globe2, ScrollText, Settings, PanelLeftClose, PanelLeftOpen, Gem, MoreHorizontal, LockKeyhole, Check, RefreshCw } from "lucide-react";
import type { GameState } from "@/lib/types";
import { number } from "@/lib/format";
import { assetPath } from "@/lib/assets";
import { GameModal } from "./game-ui";

export const destinations = [
  { id: "home", name: "Động Phủ", icon: Mountain },
  { id: "cultivation", name: "Tu Luyện", icon: Orbit },
  { id: "character", name: "Nhân Vật", icon: UserRound },
  { id: "skills", name: "Công Pháp", icon: BookOpen },
  { id: "equipment", name: "Trang Bị", icon: Sword },
  { id: "inventory", name: "Túi Đồ", icon: Backpack },
  { id: "alchemy", name: "Luyện Đan", icon: FlaskConical },
  { id: "pets", name: "Linh Thú", icon: PawPrint },
  { id: "partner", name: "Đạo Lữ", icon: Heart },
  { id: "exploration", name: "Thám Hiểm", icon: Compass },
  { id: "rift", name: "Bí Cảnh", icon: Eclipse },
  { id: "world", name: "Thiên Hạ", icon: Globe2 },
  { id: "journal", name: "Nhật Ký", icon: ScrollText },
];
const ready = new Set(["home", "cultivation", "character", "skills", "equipment", "inventory", "exploration", "world", "journal", "pets", "alchemy", "partner"]);
const mobileMain = ["home", "cultivation", "exploration", "character"];
const navigationGroups = [
  { label: "TU HÀNH", ids: ["home", "cultivation", "character", "skills", "equipment", "inventory", "alchemy"] },
  { label: "NHÂN DUYÊN", ids: ["pets", "partner"] },
  { label: "THIÊN HẠ", ids: ["exploration", "world", "rift", "journal"] },
];

export function GameShell({ state, view, navigate, children, refreshing, disconnected, onRefresh, onSettings }: {
  state: GameState; view: string; navigate: (view: string) => void; children: React.ReactNode;
  refreshing: boolean; disconnected: boolean; onRefresh: () => void; onSettings: () => void;
}) {
  const [collapsed, setCollapsed] = useState(false);
  const [more, setMore] = useState(false);
  const current = destinations.find(d => d.id === view) ?? destinations[0];
  const link = (item: typeof destinations[number], mobile = false) => <a key={item.id} href={`#${item.id}`} onClick={() => { navigate(item.id); setMore(false); }} aria-current={view === item.id ? "page" : undefined} title={collapsed && !mobile ? item.name : undefined} className={`nav-link ${view === item.id ? "active" : ""}`}><item.icon size={19} /><span>{item.name}</span>{!mobile && !ready.has(item.id) && <LockKeyhole size={11} className="nav-lock" aria-label="Chưa mở" />}</a>;
  return <div className={`game-shell ${collapsed ? "sidebar-collapsed" : ""}`}>
    <a className="skip-link" href="#main-content">Tới nội dung chính</a>
    <aside className="sidebar">
      <a href="#home" className="brand" onClick={() => navigate("home")} aria-label="Vạn Đạo Trường Sinh, Động Phủ"><div className="brand-seal" aria-hidden="true">Vạn<br />Đạo</div><span>Vạn Đạo<em>Trường Sinh</em><small>MỘT NIỆM TRƯỜNG SINH</small></span></a>
      <nav aria-label="Tiên lộ">{navigationGroups.map(group => <div className="nav-group" key={group.label}><div className="nav-caption">{group.label}</div>{group.ids.map(id => link(destinations.find(d => d.id === id)!))}</div>)}</nav>
      <div className="sidebar-bottom"><div className="sidebar-player"><img src={assetPath("characters/player/default")} width={40} height={48} alt="" /><span><strong>{state.player.name}</strong><small>{state.realm.name} · Tầng {state.realm.stage}</small></span></div><div className="sidebar-controls"><button className="nav-link" onClick={onSettings} title="Cài đặt" aria-label="Cài đặt"><Settings size={17} /><span>Cài đặt</span></button><button className="icon-button collapse-button" onClick={() => setCollapsed(!collapsed)} aria-label={collapsed ? "Mở thanh bên" : "Thu gọn thanh bên"} title={collapsed ? "Mở thanh bên" : "Thu gọn thanh bên"}>{collapsed ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />}</button></div><div role="status" className={`save-status ${disconnected ? "offline" : ""}`}><Check size={13} /><span>{disconnected ? "Chờ kết nối" : "Hành trình đã lưu"}</span></div></div>
    </aside>
    <div className="game-body"><header className="topbar"><div className="breadcrumb"><Mountain size={16} /><span>Thanh Vân Sơn</span><span className="separator">/</span><strong>{current.name}</strong></div><div className="top-resources"><span title="Linh thạch"><Gem size={16} /><strong>{number(state.player.spirit_stones)}</strong><span className="resource-label">Linh thạch</span></span><span title="Chiến lực"><Sword size={16} /><strong>{number(state.player.combat_power)}</strong><span className="resource-label">Chiến lực</span></span><button className="icon-button" onClick={onRefresh} disabled={refreshing} title="Đồng bộ hành trình" aria-label="Đồng bộ hành trình"><RefreshCw size={16} className={refreshing ? "spin" : ""} /></button></div></header>
    <main id="main-content" tabIndex={-1}>{children}</main><footer className="game-footer"><span>Vạn Đạo Trường Sinh</span><span>{state.realm.name} · Tầng {state.realm.stage}</span><span>Tiên lộ còn dài.</span></footer></div>
    <nav className="mobile-nav" aria-label="Điều hướng chính">{mobileMain.map(id => link(destinations.find(d => d.id === id)!, true))}<button className={`nav-link ${!mobileMain.includes(view) ? "active" : ""}`} onClick={() => setMore(true)} aria-expanded={more}><MoreHorizontal size={21} /><span>Thêm</span></button></nav>
    {more && <GameModal title="Tiên lộ" onClose={() => setMore(false)}><nav className="more-menu" aria-label="Các vùng tiên lộ">{destinations.filter(d => !mobileMain.includes(d.id)).map(d => link(d, true))}<button className="nav-link" onClick={() => { setMore(false); onSettings(); }}><Settings size={19} /><span>Cài đặt</span></button></nav></GameModal>}
  </div>;
}
