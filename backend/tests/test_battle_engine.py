from app.game.battle import BattleEngine, Combatant
from app.game.random_service import RandomService


def test_seeded_battle_is_replayable_and_pure():
    player = Combatant('Đạo hữu', 70, 18, 5, 8)
    enemy = Combatant('Dã Lang', 30, 8, 2, 5)
    first = BattleEngine().resolve(player, enemy, RandomService(seed=4))
    second = BattleEngine().resolve(player, enemy, RandomService(seed=4))
    assert first == second
    assert first.victory and first.turns and first.player_hp > 0


def test_weak_player_can_lose_with_log():
    result = BattleEngine().resolve(Combatant('Phàm nhân', 12, 1, 0, 1), Combatant('Dã Lang', 30, 20, 2, 5), RandomService(seed=1))
    assert not result.victory
    assert result.turns[-1]['target_hp'] == 0
