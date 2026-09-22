from __future__ import annotations

import hashlib
import json
from functools import lru_cache

from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RealmRule(BaseModel):
    max_stage: int = Field(gt=0)
    base_required_exp: int = Field(gt=0)
    growth_factor: float = Field(gt=0)


class RootRule(BaseModel):
    cultivation_modifier: float = Field(gt=0)
    breakthrough_modifier: float = Field(gt=0)


class NpcRule(BaseModel):
    stage: int = Field(gt=0)
    cultivation_exp: float = Field(ge=0)
    cultivation_rate: float = Field(gt=0)


class GameRules(BaseSettings):
    rules_version: int = Field(gt=0)

    starting_spirit_stones: int = Field(ge=0)
    starting_pills: int = Field(ge=0)
    starting_manuals: int = Field(ge=0)
    starting_combat_power: int = Field(gt=0)
    starting_realm_key: str = Field(min_length=1)
    starting_stage: int = Field(gt=0)
    starting_root_key: str = Field(min_length=1)
    equipment_pack_quantity: int = Field(gt=0)

    cultivation_base_rate: float = Field(gt=0)
    cultivation_realm_bonus: float = Field(ge=0)
    cultivation_stage_bonus: float = Field(ge=0)

    breakthrough_minor_chance: float
    breakthrough_major_chance: float
    breakthrough_failure_loss: float
    breakthrough_pill_bonus: float
    breakthrough_supported_cap: float
    breakthrough_combat_multiplier: float = Field(gt=0)
    breakthrough_combat_flat: int = Field(ge=0)
    offline_report_min_seconds: int = Field(ge=0)

    exploration_empty_chance: float
    exploration_reward_stones: int = Field(ge=0)
    exploration_reward_pills: int = Field(ge=0)

    battle_player_hp_base: int = Field(gt=0)
    battle_player_attack_base: int = Field(gt=0)
    battle_player_attack_power_divisor: int = Field(gt=0)
    battle_player_defense_base: int = Field(ge=0)
    battle_player_defense_power_divisor: int = Field(gt=0)
    battle_player_speed: int = Field(gt=0)
    battle_enemy_hp: int = Field(gt=0)
    battle_enemy_attack: int = Field(gt=0)
    battle_enemy_defense: int = Field(ge=0)
    battle_enemy_speed: int = Field(gt=0)
    battle_max_rounds: int = Field(gt=0)
    battle_damage_variance: int = Field(ge=0)

    world_tick_minutes: int = Field(gt=0)
    world_max_offline_hours: int = Field(gt=0)
    world_cultivate_continue_chance: float
    world_explore_safe_chance: float
    world_explore_opportunity_chance: float
    world_explore_injury_chance: float
    world_opportunity_gain: float = Field(gt=0)
    world_injury_hours: float = Field(gt=0)
    world_event_chance: float
    world_seed_base: int = Field(ge=0)

    relationship_cooldown_hours: int = Field(gt=0)
    relationship_affinity_min: int
    relationship_affinity_max: int
    relationship_affinity_initial: int

    journey_hau_son_minutes: int = Field(gt=0)
    journey_ngoai_vi_minutes: int = Field(gt=0)
    journey_linh_mach_minutes: int = Field(gt=0)
    journey_material_quantity: int = Field(gt=0)

    realm_rules: dict[str, RealmRule]
    root_rules: dict[str, RootRule]
    equipment_bonuses: dict[str, int]
    npc_rules: dict[str, NpcRule]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="GAME_",
        extra="ignore",
        frozen=True,
    )

    @model_validator(mode="after")
    def validate_relationships(self) -> "GameRules":
        probabilities = {
            "GAME_BREAKTHROUGH_MINOR_CHANCE": self.breakthrough_minor_chance,
            "GAME_BREAKTHROUGH_MAJOR_CHANCE": self.breakthrough_major_chance,
            "GAME_BREAKTHROUGH_FAILURE_LOSS": self.breakthrough_failure_loss,
            "GAME_BREAKTHROUGH_PILL_BONUS": self.breakthrough_pill_bonus,
            "GAME_BREAKTHROUGH_SUPPORTED_CAP": self.breakthrough_supported_cap,
            "GAME_EXPLORATION_EMPTY_CHANCE": self.exploration_empty_chance,
            "GAME_WORLD_CULTIVATE_CONTINUE_CHANCE": self.world_cultivate_continue_chance,
            "GAME_WORLD_EXPLORE_SAFE_CHANCE": self.world_explore_safe_chance,
            "GAME_WORLD_EXPLORE_OPPORTUNITY_CHANCE": self.world_explore_opportunity_chance,
            "GAME_WORLD_EXPLORE_INJURY_CHANCE": self.world_explore_injury_chance,
            "GAME_WORLD_EVENT_CHANCE": self.world_event_chance,
        }
        invalid = [name for name, value in probabilities.items() if not 0 <= value <= 1]
        if invalid:
            raise ValueError(f"probabilities must be between 0 and 1: {', '.join(invalid)}")
        expedition_total = (
            self.world_explore_safe_chance
            + self.world_explore_opportunity_chance
            + self.world_explore_injury_chance
        )
        if abs(expedition_total - 1) > 1e-9:
            raise ValueError("GAME_WORLD_EXPLORE_*_CHANCE values must sum to 1")
        if self.breakthrough_major_chance > self.breakthrough_minor_chance:
            raise ValueError(
                "GAME_BREAKTHROUGH_MAJOR_CHANCE must not exceed GAME_BREAKTHROUGH_MINOR_CHANCE"
            )
        if not self.relationship_affinity_min <= self.relationship_affinity_initial <= self.relationship_affinity_max:
            raise ValueError("GAME_RELATIONSHIP_AFFINITY_INITIAL must be within min/max")
        if any(value < 0 for value in self.equipment_bonuses.values()):
            raise ValueError("GAME_EQUIPMENT_BONUSES values must be non-negative")
        required_equipment = {
            "items/bamboo_sword",
            "items/cloth_robe",
            "items/wood_amulet",
            "items/spirit_vein_sword",
        }
        if set(self.equipment_bonuses) != required_equipment:
            raise ValueError("GAME_EQUIPMENT_BONUSES must define every equipment item")
        if self.equipment_bonuses["items/spirit_vein_sword"] <= self.equipment_bonuses["items/bamboo_sword"]:
            raise ValueError("GAME_EQUIPMENT_BONUSES items/spirit_vein_sword must exceed items/bamboo_sword")
        required_realms = {"mortal", "qi_refining", "foundation_establishment", "golden_core", "nascent_soul", "soul_formation", "void_refinement", "body_integration", "mahayana", "tribulation", "human_immortal"}
        if set(self.realm_rules) != required_realms:
            raise ValueError("GAME_REALM_RULES must define the complete realm ladder")
        if self.starting_realm_key not in self.realm_rules:
            raise ValueError("GAME_STARTING_REALM_KEY must exist in GAME_REALM_RULES")
        if self.starting_stage > self.realm_rules[self.starting_realm_key].max_stage:
            raise ValueError("GAME_STARTING_STAGE exceeds the starting realm max stage")
        if self.starting_root_key not in self.root_rules:
            raise ValueError("GAME_STARTING_ROOT_KEY must exist in GAME_ROOT_RULES")
        required_npcs = {"xie_wuchen", "luo_qinghan", "wandering_cultivator"}
        if set(self.npc_rules) != required_npcs:
            raise ValueError("GAME_NPC_RULES must define all initial NPCs")
        npc_max_stage = self.realm_rules["qi_refining"].max_stage
        if any(npc.stage > npc_max_stage for npc in self.npc_rules.values()):
            raise ValueError("GAME_NPC_RULES stage exceeds the qi_refining max stage")
        return self

    @property
    def fingerprint(self) -> str:
        payload = self.model_dump(mode="json", exclude={"rules_version"})
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


@lru_cache
def get_game_rules() -> GameRules:
    return GameRules()


game_rules = get_game_rules()
