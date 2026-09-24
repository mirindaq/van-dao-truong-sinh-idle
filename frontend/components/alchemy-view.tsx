"use client";

import { useEffect, useState } from "react";
import { ArrowRight, Flame, FlaskConical } from "lucide-react";
import { assetPath } from "@/lib/assets";
import { number } from "@/lib/format";
import type { AlchemyRecipe, GameState } from "@/lib/types";
import { StatRow } from "./game-ui";
import { GainChip, Pop } from "./moment-ui";

export function AlchemyView({ state, recipes, busy, onCraft }: {
  state: GameState;
  recipes: AlchemyRecipe[] | null;
  busy: boolean;
  onCraft: (recipe: AlchemyRecipe) => void;
}) {
  const first = recipes?.[0];
  const herbs = state.inventory.find(item => item.key === first?.ingredient_key)?.quantity ?? 0;
  const pills = state.inventory.find(item => item.key === first?.result_key)?.quantity ?? 0;
  const [crafting, setCrafting] = useState<string | null>(null);
  useEffect(() => { if (!busy) setCrafting(null); }, [busy]);
  return <section className="collection-page">
    <div className="page-heading"><div><p className="eyebrow">ĐAN PHÒNG</p><h1>Luyện Đan</h1></div><span>{recipes ? `${recipes.length} công thức` : "Đang mở lò"}</span></div>
    <div className="equipment-summary">
      <StatRow label="Vân Linh Thảo" value={<Pop value={herbs}>{number(herbs)}</Pop>} />
      <StatRow label="Tụ Khí Đan" value={<Pop value={pills}>{number(pills)}</Pop>} />
      {recipes && <GainChip amount={pills} unit="Tụ Khí Đan" />}
      <StatRow label="Giá luyện" value={recipes ? recipes.map(recipe => number(recipe.ingredient_quantity)).join(" hoặc ") + " thảo" : "…"} />
    </div>
    <div className="equipment-grid">{(recipes ?? []).map(recipe => {
      const affordable = herbs >= recipe.ingredient_quantity;
      const displayName = recipe.result_quantity > 1 ? `Mẻ ${recipe.name}` : recipe.name;
      const brewing = crafting === recipe.key;
      return <article className={`equipment-panel recipe-card ${brewing ? "brewing" : ""}`} aria-label={displayName} key={recipe.key}>
      <div className="section-heading"><h2>{displayName}</h2><FlaskConical size={20} /></div>
      <div className="equipped-detail"><img src={assetPath(recipe.result_key)} alt="" width={48} height={48} /><div><strong>{number(recipe.ingredient_quantity)} {recipe.ingredient_name}</strong><p>ra {number(recipe.result_quantity)} {recipe.result_name}. Xong ngay.</p></div></div>
      <div className="recipe-flow" aria-hidden="true"><span>{number(recipe.ingredient_quantity)} thảo</span><ArrowRight size={14} /><Flame size={16} className="recipe-fire" /><ArrowRight size={14} /><span>{number(recipe.result_quantity)} đan</span></div>
      {brewing && <div className="brew-progress" aria-hidden="true"><span /></div>}
      <button className="primary-button" disabled={busy || !affordable} onClick={() => { setCrafting(recipe.key); onCraft(recipe); }}>{affordable ? `Luyện ${displayName}` : "Chưa đủ Vân Linh Thảo"}</button>
    </article>;
    })}</div>
  </section>;
}
