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
  };
  active_pet: string | null;
  dao_partner: string | null;
  recent_logs: Array<{
    id: number;
    scope: string;
    message: string;
    created_at: string;
  }>;
};

