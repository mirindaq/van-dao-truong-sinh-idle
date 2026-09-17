from dataclasses import dataclass

from app.game.random_service import RandomService

MINOR_CHANCE = 0.85
MAJOR_CHANCE = 0.45
FAILURE_LOSS_FRACTION = 0.10


@dataclass(frozen=True)
class BreakthroughOdds:
    base: float
    root_bonus: float
    total: float
    failure_loss: float
    item_bonus: float = 0.0


class BreakthroughEngine:
    def preview(self, *, major: bool, root_modifier: float, required_exp: int, use_pill: bool = False) -> BreakthroughOdds:
        base = MAJOR_CHANCE if major else MINOR_CHANCE
        total = min(1.0, max(0.0, base * root_modifier))
        supported = max(total, min(0.95, total + 0.10)) if use_pill else total
        return BreakthroughOdds(base, total - base, supported, required_exp * FAILURE_LOSS_FRACTION, supported - total)

    def attempt(self, odds: BreakthroughOdds, rng: RandomService) -> bool:
        return rng.roll() < odds.total
