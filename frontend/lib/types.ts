export type GameState = {
  rules_version: number;
  rules_fingerprint: string;
  player: {
    id: number;
    name: string;
    spirit_stones: number;
    qi_gathering_pills: number;
    combat_power: number;
    base_combat_power: number;
    equipment_bonus: number;
    manual_key: string;
    current_activity: string;
  };
  realm: {
    key: string;
    name: string;
    stage: number;
    max_stage: number;
  };
  spiritual_root: {
    key: string;
    name: string;
    elements: string[];
    quality: string;
    cultivation_modifier: number;
    breakthrough_modifier: number;
  };
  cultivation: {
    current_exp: number;
    required_exp: number;
    rate_per_minute: number;
    seconds_until_next_stage: number | null;
    last_cultivation_at: string;
    base_rate_per_minute: number;
    root_bonus_per_minute: number;
  };
  active_pet: string | null;
  dao_partner: string | null;
  recent_logs: Array<{
    id: number;
    scope: string;
    message: string;
    created_at: string;
  }>;
  server_time: string;
  offline_report: {
    id: number; elapsed_seconds: number; earned_exp: number;
    rules_version: number; rules_fingerprint: string;
  } | null;
  breakthrough: BreakthroughPreview;
  inventory: InventoryItem[];
  equipment: Array<{ slot: EquipmentSlot; item_key: string }>;
  equipment_pack_claimed: boolean;
};

export type EquipmentSlot = "weapon" | "head" | "body" | "feet" | "ring" | "amulet";
export type Exploration = {
  id: number; request_id: string; location_key: string; state: "resolving" | "traveling" | "victory" | "defeat" | "empty";
  message: string; victory: boolean | null; reward_stones: number; reward_pills: number;
  reward_item_key: string | null; reward_item_quantity: number; available_at: string | null;
  battle_log: Array<{ turn: number; actor: string; damage: number; target_hp: number }>;
  rules_version: number; rules_fingerprint: string;
  created_at: string;
};
export type ExplorationResponse = { state: GameState; exploration: Exploration };

export type WorldNpc = {
  key: string; name: string; description: string; spiritual_root: string;
  realm_key: string; realm_name: string; stage: number; cultivation_exp: number;
  required_exp: number; activity: "cultivating" | "exploring" | "injured";
  location: string; portrait_key: string | null; injured_until: string | null; updated_at: string;
};
export type WorldEvent = { id: number; kind: string; source_key: string; message: string; occurred_at: string };
export type WorldReport = {
  id: number; started_at: string; ended_at: string; processed_ticks: number; skipped_seconds: number;
  event_count: number; npc_updates: number; rules_version: number; rules_fingerprint: string;
  summary: Record<string, number>; pending: boolean;
};
export type WorldState = {
  updated_at: string; tick_minutes: number; max_offline_hours: number;
  rules_version: number; rules_fingerprint: string;
  npcs: WorldNpc[]; events: WorldEvent[]; next_cursor: number | null; report: WorldReport | null;
};
export type WorldEventPage = { events: WorldEvent[]; next_cursor: number | null };

export type InteractionChoice = { key: string; text: string };
export type InteractionPrompt = {
  key: string; version: number; text: string; choices: InteractionChoice[]; created_at: string;
};
export type InteractionReceipt = {
  request_id: string; npc_key: string; prompt_key: string; prompt_version: number;
  prompt_text: string; choice_key: string; choice_text: string; response_text: string;
  affinity_delta: number; resulting_affinity: number; created_at: string;
};
export type RelationshipProfile = {
  npc_key: string; npc_name: string; affinity: number; address: string;
  last_interaction_at: string | null; next_available_at: string | null;
  can_interact: boolean; prompt: InteractionPrompt | null; history: InteractionReceipt[];
};
export type InteractionRequest = {
  request_id: string; prompt_key: string; prompt_version: number; choice_key: string;
};
export type InteractionResponse = {
  profile: RelationshipProfile; interaction: InteractionReceipt;
};

export type InventoryItem = {
  key: string; name: string; category: string; description: string; asset_key: string; quantity: number;
  equipment_slot: EquipmentSlot | null; combat_bonus: number;
};

export type BreakthroughRequest = {
  request_id: string; revision: string; item_key: string | null; quantity: number;
};

export type Realm = GameState["realm"];
export type BreakthroughPreview = {
  available: boolean;
  target: Realm | null;
  required_exp: number;
  base_chance: number;
  root_bonus: number;
  final_chance: number;
  failure_loss: number;
  revision: string;
  item_key: string | null;
  quantity: number;
  item_bonus: number;
  pills_owned: number;
};

export type BreakthroughResult = {
  success: boolean;
  message: string;
  cultivation_lost: number;
  items_consumed: number;
  final_chance: number | null;
  rules_version: number;
  rules_fingerprint: string;
  realm: Realm;
};
