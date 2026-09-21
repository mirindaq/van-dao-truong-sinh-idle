from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.game_rules import GameRules, game_rules
from app.db.session import async_session_factory
from app.models.game_rule_version import GameRuleVersion


class GameRuleVersionError(RuntimeError):
    pass


async def ensure_game_rule_version(session: AsyncSession, rules: GameRules) -> None:
    existing = await session.get(GameRuleVersion, rules.rules_version)
    if existing is not None:
        if existing.fingerprint != rules.fingerprint:
            raise GameRuleVersionError(
                "GAME_RULES_VERSION is already registered with a different fingerprint"
            )
        return

    fingerprint_version = await session.scalar(
        select(GameRuleVersion.version).where(
            GameRuleVersion.fingerprint == rules.fingerprint
        )
    )
    if fingerprint_version is not None:
        raise GameRuleVersionError(
            "GAME_RULES_VERSION changed but the gameplay fingerprint did not"
        )

    latest = await session.scalar(select(func.max(GameRuleVersion.version)))
    if latest is not None and rules.rules_version <= latest:
        raise GameRuleVersionError(
            f"GAME_RULES_VERSION must be greater than {latest} for new gameplay rules"
        )

    session.add(
        GameRuleVersion(
            version=rules.rules_version,
            fingerprint=rules.fingerprint,
        )
    )
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        existing = await session.get(GameRuleVersion, rules.rules_version)
        if existing is None or existing.fingerprint != rules.fingerprint:
            raise GameRuleVersionError(
                "GAME_RULES_VERSION conflicts with rules registered by another instance"
            ) from error


async def register_game_rules(rules: GameRules = game_rules) -> None:
    async with async_session_factory() as session:
        await ensure_game_rule_version(session, rules)
