const FALLBACKS: Record<string, string> = {
  maps: "/assets/maps/default-ink-landscape.svg",
  characters: "/assets/characters/default-silhouette.svg",
  npcs: "/assets/characters/default-silhouette.svg",
  npc: "/assets/characters/default-silhouette.svg",
  skills: "/assets/ui/default-rune.svg",
  manual: "/assets/ui/default-rune.svg",
  effects: "/assets/ui/default-rune.svg",
  pets: "/assets/pets/default-spirit-beast.svg",
  monsters: "/assets/monsters/default-monster.svg",
  items: "/assets/items/default-item.svg",
  ui: "/assets/ui/default-rune.svg"
};

const ASSETS: Record<string, string> = {
  "maps/qingyun_mountain": "/assets/maps/qingyun-paper.png",
  "characters/player/default": "/assets/characters/player-default.png",
  "npc/xie_wuchen": "/assets/characters/xie-wuchen.png",
  "npc/luo_qinghan": "/assets/characters/luo-qinghan.png",
  "npc/fallback": "/assets/characters/wandering-cultivator.png",
  "npc/wandering_cultivator": "/assets/characters/wandering-cultivator.png",
  "npc/ye_qingzhu": "/assets/characters/ye-qingzhu.png",
  "npc/hong_lian": "/assets/characters/hong-lian.png",
  "npc/bai_yue": "/assets/characters/bai-yue.png",
  "npc/lei_ziyan": "/assets/characters/lei-ziyan.png",
  "npc/yun_ruoli": "/assets/characters/yun-ruoli.png",
  "pets/thanh_xa": "/assets/pets/thanh-xa.png",
  "pets/hoa_ho": "/assets/pets/hoa-ho.png",
  "pets/van_tuoc": "/assets/pets/van-tuoc.png"
};

export function assetPath(key: string): string {
  const [group] = key.split("/");
  return ASSETS[key] ?? FALLBACKS[group] ?? "/assets/ui/default-rune.svg";
}

export const resolveAsset = assetPath;
