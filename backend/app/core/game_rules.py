from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path

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


class PetRule(BaseModel):
    combat_bonus: int
    cultivation_factor: float
    cultivation_flat_per_minute: float

    @model_validator(mode="after")
    def bonus_is_a_real_change(self) -> "PetRule":
        flat = self.cultivation_flat_per_minute
        factor = self.cultivation_factor
        if self.combat_bonus <= 0 or flat <= 0 or factor <= 0 or factor == 1:
            raise ValueError(
                "GAME_PET_RULES combat bonus and cultivation flat must be above 0, and cultivation factor must not be 1"
            )
        return self


class AlchemyRecipe(BaseModel):
    ingredient_key: str
    ingredient_quantity: int
    result_key: str
    result_quantity: int

    @model_validator(mode="after")
    def quantities_change_the_bag(self) -> "AlchemyRecipe":
        if self.ingredient_quantity <= 0 or self.result_quantity <= 0:
            raise ValueError("GAME_ALCHEMY_RECIPES quantities must be above 0")
        return self


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
    pet_rules: dict[str, PetRule]
    alchemy_recipes: dict[str, AlchemyRecipe]
    dao_partner_affinity: int = Field(gt=0)
    dao_partner_combat: int = Field(gt=0)
    dao_partner_factor: float = Field(gt=0)
    dao_partner_flat: float = Field(gt=0)
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
        required_pets = {"thanh_xa", "hoa_ho", "van_tuoc"}
        if set(self.pet_rules) != required_pets:
            raise ValueError("GAME_PET_RULES must define thanh_xa, hoa_ho and van_tuoc")
        snake, fox, bird = self.pet_rules["thanh_xa"], self.pet_rules["hoa_ho"], self.pet_rules["van_tuoc"]
        if not snake.combat_bonus > fox.combat_bonus > bird.combat_bonus:
            raise ValueError("GAME_PET_RULES combat bonuses must rank thanh_xa above hoa_ho above van_tuoc")
        if not bird.cultivation_factor > fox.cultivation_factor > snake.cultivation_factor:
            raise ValueError("GAME_PET_RULES cultivation factors must rank van_tuoc above hoa_ho above thanh_xa")
        if not bird.cultivation_flat_per_minute > fox.cultivation_flat_per_minute > snake.cultivation_flat_per_minute:
            raise ValueError("GAME_PET_RULES cultivation flats must rank van_tuoc above hoa_ho above thanh_xa")
        required_recipes = {"recipe/qi_pill", "recipe/qi_pill_batch"}
        if set(self.alchemy_recipes) != required_recipes:
            raise ValueError("GAME_ALCHEMY_RECIPES must define recipe/qi_pill and recipe/qi_pill_batch")
        for recipe in self.alchemy_recipes.values():
            if recipe.ingredient_key != "items/cloud_mist_herb" or recipe.result_key != "items/qi_gathering_pill":
                raise ValueError("GAME_ALCHEMY_RECIPES must spend cloud mist herb and produce a qi gathering pill")
        if self.dao_partner_factor == 1:
            raise ValueError("GAME_DAO_PARTNER_FACTOR must not be 1")
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
    env_file = Path(".env")
    if not env_file.is_file():
        env_file = Path(__file__).resolve().parents[2] / ".env.example"
    return GameRules(_env_file=env_file)


game_rules = get_game_rules()
