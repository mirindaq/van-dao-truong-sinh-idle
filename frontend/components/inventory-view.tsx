"use client";

import { useState } from "react";
import { ArrowRight, Backpack } from "lucide-react";
import { assetPath } from "@/lib/assets";
import { number } from "@/lib/format";
import type { GameState } from "@/lib/types";

export function InventoryView({ state, navigate }: { state: GameState; navigate: (view: string) => void }) {
  const [category, setCategory] = useState("all");
  const items = state.inventory.filter(item => category === "all" || item.category === category);
  return <section className="collection-page">
    <div className="page-heading"><div><p className="eyebrow">TÚI CÀN KHÔN</p><h1>Túi Đồ</h1></div><span>{number(state.inventory.filter(i => i.quantity > 0).length)} loại vật phẩm</span></div>
    <div className="filter-row" role="group" aria-label="Loại vật phẩm">
      {[["all", "Tất Cả"], ["pill", "Đan Dược"], ["manual", "Công Pháp"]].map(([id, label]) => <button key={id} className={`filter-pill ${category === id ? "active" : ""}`} aria-pressed={category === id} onClick={() => setCategory(id)}>{label}</button>)}
    </div>
    <div className="owned-inventory">
      {items.map(item => <article className="owned-item" key={item.key} aria-label={item.name}>
        <img src={assetPath(item.asset_key)} alt="" width={64} height={64} onError={e => { e.currentTarget.onerror = null; e.currentTarget.src = assetPath(item.category === "manual" ? "skills/default" : "items/default"); }} />
        <div><span className="eyebrow">{item.category === "pill" ? "ĐAN DƯỢC" : "CÔNG PHÁP"}</span><h2>{item.name}</h2><p>{item.description}</p><span className="muted">{item.quantity === 0 ? "Đã hết" : `Số lượng: ${number(item.quantity)}`}</span></div>
        {item.category === "pill" && <button className="secondary-button" onClick={() => navigate("cultivation")}>Tu luyện<ArrowRight size={16} /></button>}
      </article>)}
    </div>
    {items.length === 0 && <div className="empty-lore"><Backpack size={36} /><h2>Chưa có vật phẩm</h2></div>}
  </section>;
}
