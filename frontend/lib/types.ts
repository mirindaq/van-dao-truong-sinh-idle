export type GameState = {
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
  offline_report: { id: number; elapsed_seconds: number; earned_exp: number } | null;
  breakthrough: BreakthroughPreview;
  inventory: InventoryItem[];
  equipment: Array<{ slot: EquipmentSlot; item_key: string }>;
  equipment_pack_claimed: boolean;
};

export type EquipmentSlot = "weapon" | "head" | "body" | "feet" | "ring" | "amulet";
export type Exploration = {
  id: number; request_id: string; location_key: string; state: "resolving" | "victory" | "defeat" | "empty";
  message: string; victory: boolean | null; reward_stones: number; reward_pills: number;
  battle_log: Array<{ turn: number; actor: string; damage: number; target_hp: number }>;
  created_at: string;
};
export type ExplorationResponse = { state: GameState; exploration: Exploration };

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
  realm: Realm;
};
