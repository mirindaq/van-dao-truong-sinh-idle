from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.game_rules import GameRules
from app.game.cultivation import CultivationEngine, CultivationInput
from app.game.data.pets import pet_definitions

EXAMPLE = Path(__file__).parents[1] / ".env.example"


def load(**overrides) -> GameRules:
    return GameRules(_env_file=EXAMPLE, **overrides)


def _rate(factor: float, flat: float) -> float:
    now = datetime(2026, 9, 23, tzinfo=timezone.utc)
    result = CultivationEngine().apply_offline_progress(CultivationInput(
        cultivation_exp=0,
        last_cultivation_at=now - timedelta(minutes=1),
        current_time=now,
        base_rate_per_minute=1.2,
        root_modifier=1,
        pet_factor=factor,
        pet_flat_per_minute=flat,
    ))
    return result.rate_per_minute


def test_active_thanh_xa_uses_factor_and_flat_once():
    pet = load().pet_rules["thanh_xa"]
    assert _rate(pet.cultivation_factor, pet.cultivation_flat_per_minute) == pytest.approx(1.46)


def test_missing_pet_terms_keep_the_old_rate():
    assert _rate(1, 0) == pytest.approx(1.2)
    now = datetime(2026, 9, 23, tzinfo=timezone.utc)
    result = CultivationEngine().apply_offline_progress(CultivationInput(
        cultivation_exp=0,
        last_cultivation_at=now - timedelta(minutes=1),
        current_time=now,
        base_rate_per_minute=1.2,
        root_modifier=1,
    ))
    assert result.rate_per_minute == pytest.approx(1.2)


def test_example_pets_keep_the_agreed_leans_and_names():
    rules = load()
    pets = pet_definitions(rules)
    assert [pet["key"] for pet in pets] == ["thanh_xa", "hoa_ho", "van_tuoc"]
    assert [pet["name"] for pet in pets] == ["Thanh Xà", "Hỏa Hồ", "Vân Tước"]
    assert rules.pet_rules["thanh_xa"].combat_bonus == 6
    assert rules.pet_rules["hoa_ho"].cultivation_factor == pytest.approx(1.1)
    assert rules.pet_rules["van_tuoc"].cultivation_flat_per_minute == pytest.approx(0.8)


@pytest.mark.parametrize("change", [
    {"drop": "van_tuoc"},
    {"key": "thanh_xa", "field": "cultivation_factor", "value": 1},
    {"key": "hoa_ho", "field": "cultivation_flat_per_minute", "value": 0},
])
def test_invalid_pet_rules_name_the_variable(change):
    values = load().model_dump()
    if "drop" in change:
        del values["pet_rules"][change["drop"]]
    else:
        values["pet_rules"][change["key"]][change["field"]] = change["value"]
    with pytest.raises(ValidationError, match="GAME_PET_RULES"):
        GameRules(_env_file=None, **values)
