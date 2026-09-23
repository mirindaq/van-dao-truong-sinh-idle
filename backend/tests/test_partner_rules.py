from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.game_rules import GameRules
from app.game.cultivation import CultivationEngine, CultivationInput
from app.game.data.alchemy import alchemy_definitions
from app.game.data.partners import partner_stack

EXAMPLE = Path(__file__).parents[1] / ".env.example"


def load(**overrides) -> GameRules:
    return GameRules(_env_file=EXAMPLE, **overrides)


def rate(partner_factor: float = 1, partner_flat: float = 0) -> float:
    now = datetime(2026, 9, 23, tzinfo=timezone.utc)
    result = CultivationEngine().apply_offline_progress(CultivationInput(
        cultivation_exp=0,
        last_cultivation_at=now - timedelta(minutes=1),
        current_time=now,
        base_rate_per_minute=1.2,
        root_modifier=1,
        pet_factor=1.05,
        pet_flat_per_minute=0.2,
        partner_factor=partner_factor,
        partner_flat_per_minute=partner_flat,
    ))
    return result.rate_per_minute


def test_no_partner_keeps_the_pet_rate_and_each_partner_adds_one_share():
    rules = load()
    assert rate() == pytest.approx(1.46)
    combat, factor, flat = partner_stack(rules, 1)
    assert combat == 3
    assert rate(factor, flat) == pytest.approx(1.2 * 1.05 * 1.05 + 0.2 + 0.1)
    combat, factor, flat = partner_stack(rules, 2)
    assert combat == 6
    assert flat == pytest.approx(0.2)
    assert rate(factor, flat) == pytest.approx(1.2 * 1.05 * (1.05 ** 2) + 0.2 + 0.2)
    assert partner_stack(rules, 0) == (0, 1, 0)


def test_batch_recipe_is_six_herbs_for_two_pills():
    recipes = {recipe["key"]: recipe for recipe in alchemy_definitions(load())}
    assert recipes["recipe/qi_pill"]["ingredient_quantity"] == 3
    assert recipes["recipe/qi_pill"]["result_quantity"] == 1
    assert recipes["recipe/qi_pill_batch"]["ingredient_quantity"] == 6
    assert recipes["recipe/qi_pill_batch"]["result_quantity"] == 2


def test_missing_batch_recipe_names_the_variable():
    values = load().model_dump()
    del values["alchemy_recipes"]["recipe/qi_pill_batch"]
    with pytest.raises(ValidationError, match="GAME_ALCHEMY_RECIPES"):
        GameRules(_env_file=None, **values)
