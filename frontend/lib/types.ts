export type GameState = {
  player: {
    id: number;
    name: string;
    spirit_stones: number;
    qi_gathering_pills: number;
    combat_power: number;
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
};

export type BreakthroughResult = {
  success: boolean;
  message: string;
  cultivation_lost: number;
  realm: Realm;
};
