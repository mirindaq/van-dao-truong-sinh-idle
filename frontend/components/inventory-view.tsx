"use client";

import { useState } from "react";
import { ArrowRight, Backpack } from "lucide-react";
import { assetPath } from "@/lib/assets";
import { number } from "@/lib/format";
import type { GameState } from "@/lib/types";
import { Reveal } from "./moment-ui";

export function InventoryView({ state, navigate, onClaim, disabled }: { state: GameState; navigate: (view: string) => void; onClaim: () => void; disabled: boolean }) {
  const [category, setCategory] = useState("all");
  const items = state.inventory.filter(item => category === "all" || item.category === category);
  return <section className="collection-page">
    <div className="page-heading"><div><p className="eyebrow">TÚI CÀN KHÔN</p><h1>Túi Đồ</h1></div><span>{number(state.inventory.filter(i => i.quantity > 0).length)} loại vật phẩm</span></div>
    <section className="equipment-pack" aria-label="Gói trang bị khởi đầu"><div><h2>Hành trang vấn đạo</h2><p>Một Thanh Trúc Kiếm, một Vải Thô Đạo Bào và một Thanh Mộc Ngọc Bội. Mỗi hành trình nhận một lần.</p></div>{state.equipment_pack_claimed ? <span className="muted">Đã nhận trang bị</span> : <button className="primary-button" disabled={disabled} onClick={onClaim}>NHẬN TRANG BỊ</button>}</section>
    <div className="filter-row" role="group" aria-label="Loại vật phẩm">
      {[["all", "Tất Cả"], ["pill", "Đan Dược"], ["manual", "Công Pháp"], ["equipment", "Trang Bị"]].map(([id, label]) => <button key={id} className={`filter-pill ${category === id ? "active" : ""}`} aria-pressed={category === id} onClick={() => setCategory(id)}>{label}</button>)}
    </div>
    <Reveal id={category} className="owned-inventory">
      {items.map(item => <article className="owned-item" key={item.key} aria-label={item.name}>
        <img src={assetPath(item.asset_key)} alt="" width={64} height={64} onError={e => { e.currentTarget.onerror = null; e.currentTarget.src = assetPath(item.category === "manual" ? "skills/default" : "items/default"); }} />
        <div><span className="eyebrow">{item.category === "pill" ? "ĐAN DƯỢC" : item.category === "equipment" ? "TRANG BỊ" : "CÔNG PHÁP"}</span><h2>{item.name}</h2><p>{item.description}</p><span className="muted">{item.quantity === 0 ? "Đã hết" : `Số lượng: ${number(item.quantity)}`}{state.equipment.some(e => e.item_key === item.key) && " · Đang mặc"}</span></div>
        {item.category === "pill" && <button className="secondary-button" onClick={() => navigate("cultivation")}>Tu luyện<ArrowRight size={16} /></button>}
        {item.category === "equipment" && <button className="secondary-button" onClick={() => navigate("equipment")}>Trang bị<ArrowRight size={16} /></button>}
      </article>)}
    </Reveal>
    {items.length === 0 && <div className="empty-lore"><Backpack size={36} /><h2>Chưa có vật phẩm</h2></div>}
  </section>;
}
