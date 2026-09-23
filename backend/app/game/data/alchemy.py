from app.core.game_rules import GameRules

RECIPES = ("recipe/qi_pill", "recipe/qi_pill_batch")


def alchemy_definitions(rules: GameRules) -> list[dict]:
    return [
        dict(
            key=key,
            name="Tụ Khí Đan",
            ingredient_key=rules.alchemy_recipes[key].ingredient_key,
            ingredient_name="Vân Linh Thảo",
            ingredient_quantity=rules.alchemy_recipes[key].ingredient_quantity,
            result_key=rules.alchemy_recipes[key].result_key,
            result_name="Tụ Khí Đan",
            result_quantity=rules.alchemy_recipes[key].result_quantity,
        )
        for key in RECIPES
    ]
