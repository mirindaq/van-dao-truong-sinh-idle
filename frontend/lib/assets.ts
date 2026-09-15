const FALLBACKS: Record<string, string> = {
  maps: "/assets/maps/default-ink-landscape.svg",
  characters: "/assets/characters/default-silhouette.svg",
  npcs: "/assets/characters/default-silhouette.svg",
  pets: "/assets/pets/default-spirit-beast.svg",
  monsters: "/assets/monsters/default-monster.svg",
  items: "/assets/items/default-item.svg",
  ui: "/assets/ui/default-rune.svg"
};

export function assetPath(key: string): string {
  const [group] = key.split("/");
  return FALLBACKS[group] ?? "/assets/ui/default-rune.svg";
}

