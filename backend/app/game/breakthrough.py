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


class BreakthroughEngine:
    def preview(self, *, major: bool, root_modifier: float, required_exp: int) -> BreakthroughOdds:
        base = MAJOR_CHANCE if major else MINOR_CHANCE
        total = min(1.0, max(0.0, base * root_modifier))
        return BreakthroughOdds(base, total - base, total, required_exp * FAILURE_LOSS_FRACTION)

    def attempt(self, odds: BreakthroughOdds, rng: RandomService) -> bool:
        return rng.roll() < odds.total
