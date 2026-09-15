from datetime import datetime, timedelta, timezone

from app.game.cultivation import CultivationEngine, CultivationInput


def test_apply_offline_progress_uses_elapsed_timestamp() -> None:
    engine = CultivationEngine()
    start = datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)

    result = engine.apply_offline_progress(
        CultivationInput(
            cultivation_exp=10,
            last_cultivation_at=start,
            current_time=start + timedelta(minutes=30),
            base_rate_per_minute=2,
            root_modifier=1.5,
        )
    )

    assert result.elapsed_seconds == 1800
    assert result.rate_per_minute == 3
    assert result.earned_exp == 90
    assert result.cultivation_exp == 100


def test_negative_elapsed_time_does_not_remove_progress() -> None:
    engine = CultivationEngine()
    now = datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)

    result = engine.apply_offline_progress(
        CultivationInput(
            cultivation_exp=20,
            last_cultivation_at=now + timedelta(minutes=5),
            current_time=now,
            base_rate_per_minute=2,
            root_modifier=1,
        )
    )

    assert result.elapsed_seconds == 0
    assert result.earned_exp == 0
    assert result.cultivation_exp == 20

