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
import pytest


@pytest.mark.parametrize('major,root,expected', [(False, 1.02, .95), (True, 1.02, .559), (False, 1.2, 1.0)])
def test_pill_bonus_cap_and_high_base(major, root, expected):
    from app.game.breakthrough import BreakthroughEngine
    engine = BreakthroughEngine()
    base = engine.preview(major=major, root_modifier=root, required_exp=120)
    supported = engine.preview(major=major, root_modifier=root, required_exp=120, use_pill=True)
    assert supported.total == pytest.approx(expected)
    assert supported.total >= base.total
    assert supported.item_bonus == pytest.approx(supported.total - base.total)
    assert supported.failure_loss == 12
