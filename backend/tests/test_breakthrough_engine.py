from app.game.breakthrough import BreakthroughEngine
from app.game.random_service import RandomService


def test_odds_and_failure_cost():
    odds = BreakthroughEngine().preview(major=True, root_modifier=1.02, required_exp=100)
    assert round(odds.total, 3) == 0.459
    assert odds.failure_loss == 10
    assert odds.base + odds.root_bonus == odds.total


def test_seeded_success_and_failure():
    engine = BreakthroughEngine()
    odds = engine.preview(major=False, root_modifier=1.02, required_exp=120)
    assert engine.attempt(odds, RandomService(seed=1)) is True
    assert engine.attempt(odds, RandomService(seed=2)) is False


def test_chance_is_bounded():
    assert BreakthroughEngine().preview(major=False, root_modifier=5, required_exp=120).total == 1
