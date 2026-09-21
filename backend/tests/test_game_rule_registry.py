import pytest
from sqlalchemy import func, select

from app.core.game_rule_registry import GameRuleVersionError, ensure_game_rule_version
from app.core.game_rules import game_rules
from app.models.game_rule_version import GameRuleVersion
from app.models.player import Player
from tests.test_game_api import game  # noqa: F401


async def test_registry_rejects_reused_version_and_allows_registered_rollback(game):
    _, sessions = game
    changed = game_rules.model_copy(update={
        "rules_version": game_rules.rules_version + 1,
        "cultivation_base_rate": game_rules.cultivation_base_rate + 0.5,
    })
    reused = game_rules.model_copy(update={
        "cultivation_base_rate": game_rules.cultivation_base_rate + 1,
    })

    async with sessions() as session:
        await ensure_game_rule_version(session, game_rules)
        await ensure_game_rule_version(session, game_rules)
        await ensure_game_rule_version(session, changed)
        await ensure_game_rule_version(session, game_rules)
        assert await session.scalar(select(func.count()).select_from(GameRuleVersion)) == 2

        with pytest.raises(GameRuleVersionError, match="GAME_RULES_VERSION"):
            await ensure_game_rule_version(session, reused)
        assert await session.scalar(select(func.count()).select_from(Player)) == 0


async def test_registry_rejects_new_version_without_gameplay_change(game):
    _, sessions = game
    renumbered = game_rules.model_copy(update={
        "rules_version": game_rules.rules_version + 1,
    })

    async with sessions() as session:
        await ensure_game_rule_version(session, game_rules)
        with pytest.raises(GameRuleVersionError, match="fingerprint did not"):
            await ensure_game_rule_version(session, renumbered)
