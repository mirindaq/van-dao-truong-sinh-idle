from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.game_rules import GameRules
from app.game.data.alchemy import alchemy_definitions

EXAMPLE = Path(__file__).parents[1] / ".env.example"


def load(**overrides) -> GameRules:
    return GameRules(_env_file=EXAMPLE, **overrides)


def test_example_recipe_spends_three_herbs_for_one_pill():
    recipe = alchemy_definitions(load())[0]
    assert recipe["key"] == "recipe/qi_pill"
    assert recipe["ingredient_quantity"] == 3
    assert recipe["result_quantity"] == 1
    assert recipe["ingredient_name"] == "Vân Linh Thảo"
    assert recipe["result_name"] == "Tụ Khí Đan"


@pytest.mark.parametrize("change", [
    {"drop": "recipe/qi_pill"},
    {"field": "ingredient_quantity", "value": 0},
    {"field": "ingredient_key", "value": "items/unknown"},
])
def test_invalid_alchemy_rules_name_the_variable(change):
    values = load().model_dump()
    if "drop" in change:
        del values["alchemy_recipes"][change["drop"]]
    else:
        values["alchemy_recipes"]["recipe/qi_pill"][change["field"]] = change["value"]
    with pytest.raises(ValidationError, match="GAME_ALCHEMY_RECIPES"):
        GameRules(_env_file=None, **values)
