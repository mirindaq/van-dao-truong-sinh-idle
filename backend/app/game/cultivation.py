from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CultivationInput:
    cultivation_exp: float
    last_cultivation_at: datetime
    current_time: datetime
    base_rate_per_minute: float
    root_modifier: float


@dataclass(frozen=True)
class CultivationResult:
    cultivation_exp: float
    earned_exp: float
    elapsed_seconds: int
    rate_per_minute: float


class CultivationEngine:
    def apply_offline_progress(self, data: CultivationInput) -> CultivationResult:
        elapsed_seconds = max(int((data.current_time - data.last_cultivation_at).total_seconds()), 0)
        rate_per_minute = data.base_rate_per_minute * data.root_modifier
        earned_exp = (elapsed_seconds / 60) * rate_per_minute

        return CultivationResult(
            cultivation_exp=data.cultivation_exp + earned_exp,
            earned_exp=earned_exp,
            elapsed_seconds=elapsed_seconds,
            rate_per_minute=rate_per_minute,
        )

    def seconds_until_next_stage(
        self,
        current_exp: float,
        required_exp: float,
        rate_per_minute: float,
    ) -> int | None:
        if current_exp >= required_exp:
            return 0
        if rate_per_minute <= 0:
            return None
        remaining = required_exp - current_exp
        return int((remaining / rate_per_minute) * 60)

