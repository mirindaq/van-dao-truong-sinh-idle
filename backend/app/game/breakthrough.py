from dataclasses import dataclass

from app.core.game_rules import GameRules, game_rules
from app.game.random_service import RandomService


@dataclass(frozen=True)
class BreakthroughOdds:
    base: float
    root_bonus: float
    total: float
    failure_loss: float
    item_bonus: float = 0.0


class BreakthroughEngine:
    def __init__(self, rules: GameRules = game_rules):
        self.rules = rules

    def preview(self, *, major: bool, root_modifier: float, required_exp: int, use_pill: bool = False) -> BreakthroughOdds:
        base = self.rules.breakthrough_major_chance if major else self.rules.breakthrough_minor_chance
        total = min(1.0, max(0.0, base * root_modifier))
        supported = max(total, min(self.rules.breakthrough_supported_cap, total + self.rules.breakthrough_pill_bonus)) if use_pill else total
        return BreakthroughOdds(base, total - base, supported, required_exp * self.rules.breakthrough_failure_loss, supported - total)

    def attempt(self, odds: BreakthroughOdds, rng: RandomService) -> bool:
        return rng.roll() < odds.total
