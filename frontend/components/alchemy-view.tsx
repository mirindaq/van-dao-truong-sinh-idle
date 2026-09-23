"use client";

import { FlaskConical } from "lucide-react";
import { assetPath } from "@/lib/assets";
import { number } from "@/lib/format";
import type { AlchemyRecipe, GameState } from "@/lib/types";
import { StatRow } from "./game-ui";

export function AlchemyView({ state, recipes, busy, onCraft }: {
  state: GameState;
  recipes: AlchemyRecipe[] | null;
  busy: boolean;
  onCraft: (recipe: AlchemyRecipe) => void;
}) {
  const first = recipes?.[0];
  const herbs = state.inventory.find(item => item.key === first?.ingredient_key)?.quantity ?? 0;
  const pills = state.inventory.find(item => item.key === first?.result_key)?.quantity ?? 0;
  return <section className="collection-page">
    <div className="page-heading"><div><p className="eyebrow">ĐAN PHÒNG</p><h1>Luyện Đan</h1></div><span>{recipes ? `${recipes.length} công thức` : "Đang mở lò"}</span></div>
    <div className="equipment-summary">
      <StatRow label="Vân Linh Thảo" value={number(herbs)} />
      <StatRow label="Tụ Khí Đan" value={number(pills)} />
      <StatRow label="Giá luyện" value={recipes ? recipes.map(recipe => number(recipe.ingredient_quantity)).join(" hoặc ") + " thảo" : "…"} />
    </div>
    <div className="equipment-grid">{(recipes ?? []).map(recipe => {
      const affordable = herbs >= recipe.ingredient_quantity;
      const displayName = recipe.result_quantity > 1 ? `Mẻ ${recipe.name}` : recipe.name;
      return <article className="equipment-panel" aria-label={displayName} key={recipe.key}>
      <div className="section-heading"><h2>{displayName}</h2><FlaskConical size={20} /></div>
      <div className="equipped-detail"><img src={assetPath(recipe.result_key)} alt="" width={48} height={48} /><div><strong>{number(recipe.ingredient_quantity)} {recipe.ingredient_name}</strong><p>ra {number(recipe.result_quantity)} {recipe.result_name}. Xong ngay.</p></div></div>
      <button className="primary-button" disabled={busy || !affordable} onClick={() => onCraft(recipe)}>{affordable ? `Luyện ${displayName}` : "Chưa đủ Vân Linh Thảo"}</button>
    </article>;
    })}</div>
  </section>;
}
