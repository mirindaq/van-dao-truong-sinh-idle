from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from hashlib import sha256

from app.game.breakthrough import BreakthroughEngine
from app.game.data.realms import REALM_DEFINITIONS, required_exp_for_stage
from app.game.random_service import RandomService


@dataclass(frozen=True)
class NpcSnapshot:
    key: str
    name: str
    realm_key: str
    stage: int
    cultivation_exp: float
    cultivation_rate: float
    activity: str
    location: str
    injured_until: datetime | None = None


@dataclass(frozen=True)
class TickResult:
    npc: NpcSnapshot
    events: tuple[dict, ...]


class WorldEngine:
    tick_minutes = 10
    max_ticks = 144

    @staticmethod
    def _rng(seed: int, tick_index: int, source: str) -> RandomService:
        digest = sha256(f"{seed}:{tick_index}:{source}".encode()).digest()
        return RandomService(int.from_bytes(digest[:8], "big"))

    def __init__(self) -> None:
        self.breakthrough = BreakthroughEngine()
        self.realms = {realm["key"]: realm for realm in REALM_DEFINITIONS}
        self.realm_order = sorted(REALM_DEFINITIONS, key=lambda realm: realm["rank_order"])

    def required_exp(self, stage: int, realm_key: str = "qi_refining") -> int:
        realm = self.realms[realm_key]
        return required_exp_for_stage(realm["base_required_exp"], realm["growth_factor"], stage)

    def realm_name(self, realm_key: str) -> str:
        return self.realms[realm_key]["name"]

    def _target(self, npc: NpcSnapshot) -> tuple[str, int] | None:
        realm = self.realms[npc.realm_key]
        if npc.stage < realm["max_stage"]:
            return npc.realm_key, npc.stage + 1
        next_realm = next((candidate for candidate in self.realm_order if candidate["rank_order"] == realm["rank_order"] + 1), None)
        return (next_realm["key"], 1) if next_realm else None

    def _attempt_breakthrough(self, current: NpcSnapshot, rng: RandomService, events: list[dict]) -> NpcSnapshot:
        required = self.required_exp(current.stage, current.realm_key)
        target = self._target(current)
        if current.cultivation_exp < required or target is None:
            return current
        major = target[0] != current.realm_key
        odds = self.breakthrough.preview(major=major, root_modifier=1.0, required_exp=required)
        if self.breakthrough.attempt(odds, rng):
            current = replace(current, realm_key=target[0], stage=target[1], cultivation_exp=current.cultivation_exp - required)
            events.append(self._event("breakthrough", current, f"{current.name} đã đột phá {self.realm_name(current.realm_key)} tầng {current.stage}."))
        else:
            lost = min(current.cultivation_exp, odds.failure_loss)
            current = replace(current, cultivation_exp=current.cultivation_exp - lost)
            events.append(self._event("breakthrough_failed", current, f"{current.name} đột phá thất bại và tĩnh tâm điều tức."))
        return current

    def advance_npc(self, npc: NpcSnapshot, tick_index: int, tick_time: datetime, seed: int) -> TickResult:
        rng = self._rng(seed, tick_index, npc.key)
        events: list[dict] = []
        current = npc
        if current.activity == "injured":
            if current.injured_until is None or tick_time < current.injured_until:
                return TickResult(current, ())
            current = replace(current, activity="cultivating", injured_until=None, location="Thanh Vân Sơn")
            events.append(self._event("recovered", current, f"{current.name} đã bình phục và trở lại tu luyện."))

        if current.activity == "exploring":
            outcome = rng.roll()
            if outcome < .6:
                current = replace(current, activity="cultivating", location="Thanh Vân Sơn")
            elif outcome < .85:
                gained = self.required_exp(current.stage, current.realm_key) * .1
                current = replace(current, activity="cultivating", location="Thanh Vân Sơn",
                                  cultivation_exp=current.cultivation_exp + gained)
                events.append(self._event("opportunity", current, f"{current.name} tìm được một cơ duyên nhỏ."))
            else:
                current = replace(current, activity="injured", injured_until=tick_time + timedelta(hours=1))
                events.append(self._event("injured", current, f"{current.name} bị thương khi thám du."))
                return TickResult(current, tuple(events))
            current = self._attempt_breakthrough(current, rng, events)
            return TickResult(current, tuple(events))

        current = replace(current, cultivation_exp=current.cultivation_exp + current.cultivation_rate)
        current = self._attempt_breakthrough(current, rng, events)
        if rng.roll() >= .8:
            current = replace(current, activity="exploring", location="Ngoại vi Thanh Vân Sơn")
        return TickResult(current, tuple(events))

    def world_event(self, tick_index: int, seed: int) -> dict | None:
        rng = self._rng(seed, tick_index, "world")
        if rng.roll() >= .05:
            return None
        kind, message = rng.choice((
            ("spiritual_tide", "Linh khí quanh Thanh Vân Sơn chợt hội tụ."),
            ("merchant_caravan", "Một thương đội tu sĩ ghé qua chân núi."),
            ("beast_aura", "Trong rừng sâu xuất hiện khí tức yêu thú."),
        ))
        return {"kind": kind, "source_key": "world", "message": message}

    @staticmethod
    def _event(kind: str, npc: NpcSnapshot, message: str) -> dict:
        return {"kind": kind, "source_key": npc.key, "message": message}
