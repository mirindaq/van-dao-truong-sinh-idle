from dataclasses import dataclass
from app.core.game_rules import GameRules, game_rules
from app.game.random_service import RandomService


@dataclass(frozen=True)
class Combatant:
    name: str
    hp: int
    attack: int
    defense: int
    speed: int


@dataclass(frozen=True)
class BattleResult:
    victory: bool
    turns: list[dict]
    player_hp: int
    enemy_hp: int


class BattleEngine:
    def __init__(self, rules: GameRules = game_rules):
        self.rules = rules

    def resolve(self, player: Combatant, enemy: Combatant, rng: RandomService) -> BattleResult:
        player_hp, enemy_hp, turns = player.hp, enemy.hp, []
        order = (("player", player), ("enemy", enemy)) if player.speed >= enemy.speed else (("enemy", enemy), ("player", player))
        for turn in range(1, self.rules.battle_max_rounds + 1):
            for side, actor in order:
                if player_hp <= 0 or enemy_hp <= 0:
                    break
                raw = max(1, actor.attack - (enemy.defense if side == "player" else player.defense))
                damage = raw + rng.randint(0, self.rules.battle_damage_variance)
                if side == "player":
                    enemy_hp = max(0, enemy_hp - damage)
                    target_hp = enemy_hp
                else:
                    player_hp = max(0, player_hp - damage)
                    target_hp = player_hp
                turns.append({"turn": turn, "actor": actor.name, "damage": damage, "target_hp": target_hp})
            if player_hp <= 0 or enemy_hp <= 0:
                break
        return BattleResult(player_hp > 0 and enemy_hp == 0, turns, player_hp, enemy_hp)
