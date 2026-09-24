from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.game_rules import GameRules


EXAMPLE = Path(__file__).parents[1] / ".env.example"


def load(**overrides) -> GameRules:
    return GameRules(_env_file=EXAMPLE, **overrides)


def test_example_defines_every_gameplay_group_and_stable_fingerprint():
    first = load()
    second = load()
    assert first == second
    assert first.fingerprint == second.fingerprint
    assert first.relationship_cooldown_hours == 12
    assert set(first.realm_rules) == {"mortal", "qi_refining", "foundation_establishment", "golden_core", "nascent_soul", "soul_formation", "void_refinement", "body_integration", "mahayana", "tribulation", "human_immortal"}
    assert set(first.npc_rules) == {
        "xie_wuchen", "luo_qinghan", "wandering_cultivator", "ye_qingzhu",
        "hong_lian", "bai_yue", "lei_ziyan", "yun_ruoli",
    }
    assert set(first.pet_rules) == {"thanh_xa", "hoa_ho", "van_tuoc"}
    assert set(first.alchemy_recipes) == {"recipe/qi_pill", "recipe/qi_pill_batch"}


def test_override_changes_only_new_rules_snapshot():
    base = load()
    changed = load(cultivation_base_rate=2.5, rules_version=base.rules_version + 1)
    assert changed.cultivation_base_rate == 2.5
    assert changed.fingerprint != base.fingerprint


@pytest.mark.parametrize("field,value,variable", [
    ("breakthrough_minor_chance", 1.1, "GAME_BREAKTHROUGH_MINOR_CHANCE"),
    ("world_explore_injury_chance", -0.1, "GAME_WORLD_EXPLORE_INJURY_CHANCE"),
    ("relationship_affinity_initial", 101, "GAME_RELATIONSHIP_AFFINITY_INITIAL"),
])
def test_invalid_values_fail_with_actionable_variable(field, value, variable):
    with pytest.raises(ValidationError) as error:
        load(**{field: value})
    assert variable in str(error.value)


def test_missing_required_variable_fails_with_field_name(tmp_path):
    lines = [line for line in EXAMPLE.read_text(encoding="utf-8").splitlines() if not line.startswith("GAME_RULES_VERSION=")]
    incomplete = tmp_path / ".env"
    incomplete.write_text("\n".join(lines), encoding="utf-8")
    with pytest.raises(ValidationError) as error:
        GameRules(_env_file=incomplete)
    assert "rules_version" in str(error.value)


def test_expedition_probabilities_must_sum_to_one():
    with pytest.raises(ValidationError, match=r"GAME_WORLD_EXPLORE_\*_CHANCE"):
        load(world_explore_safe_chance=.5)


def test_breakthrough_major_chance_cannot_exceed_minor_chance():
    with pytest.raises(ValidationError, match="GAME_BREAKTHROUGH_MAJOR_CHANCE"):
        load(breakthrough_major_chance=.9, breakthrough_minor_chance=.8)


def test_equipment_map_must_be_complete():
    values = load().model_dump()
    values["equipment_bonuses"] = {"items/bamboo_sword": 5}
    with pytest.raises(ValidationError, match="GAME_EQUIPMENT_BONUSES"):
        GameRules(_env_file=None, **values)


def test_npc_stage_must_fit_the_seed_realm():
    rules = load()
    npcs = dict(rules.npc_rules)
    npcs["xie_wuchen"] = npcs["xie_wuchen"].model_copy(update={"stage": 10})
    with pytest.raises(ValidationError, match="GAME_NPC_RULES"):
        load(npc_rules=npcs)
