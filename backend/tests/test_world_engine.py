from datetime import datetime, timezone

from app.core.game_rules import game_rules
from app.game.world import NpcSnapshot, WorldEngine


def npc(**changes):
    values = dict(key="test", name="Thử", realm_key="qi_refining", stage=1, cultivation_exp=0,
                  cultivation_rate=6, activity="cultivating", location="Thanh Vân Sơn", injured_until=None)
    values.update(changes)
    return NpcSnapshot(**values)


def test_world_engine_is_deterministic_per_tick_and_source():
    engine = WorldEngine(); now = datetime(2026, 9, 18, tzinfo=timezone.utc)
    first = engine.advance_npc(npc(), 12, now, 1408)
    second = engine.advance_npc(npc(), 12, now, 1408)
    assert first == second
    assert engine.world_event(12, 1408) == engine.world_event(12, 1408)


def test_world_engine_covers_expedition_and_recovery_states():
    engine = WorldEngine(); now = datetime(2026, 9, 18, tzinfo=timezone.utc)
    outcomes = [engine.advance_npc(npc(activity="exploring"), tick, now, 99) for tick in range(1, 200)]
    assert any(result.npc.activity == "injured" for result in outcomes)
    assert any(any(event["kind"] == "opportunity" for event in result.events) for result in outcomes)
    recovered = engine.advance_npc(npc(activity="injured", injured_until=now), 1, now, 99)
    assert recovered.npc.activity in ("cultivating", "exploring")
    assert recovered.events[0]["kind"] == "recovered"


def test_world_engine_breakthrough_success_and_failure_exist_for_seeded_ticks():
    engine = WorldEngine(); now = datetime(2026, 9, 18, tzinfo=timezone.utc)
    ready = npc(cultivation_exp=engine.required_exp(1), cultivation_rate=0)
    results = [engine.advance_npc(ready, tick, now, 77) for tick in range(1, 100)]
    kinds = {event["kind"] for result in results for event in result.events}
    assert {"breakthrough", "breakthrough_failed"} <= kinds


def test_split_and_single_pass_tick_sequences_match():
    engine = WorldEngine(); now = datetime(2026, 9, 18, tzinfo=timezone.utc)
    def advance(current, ticks):
        for tick in ticks:
            current = engine.advance_npc(current, tick, now, 404).npc
        return current
    single = advance(npc(), range(1, 13))
    split = advance(advance(npc(), range(1, 5)), range(5, 13))
    assert split == single


def test_npc_can_cross_a_major_realm_and_opportunity_can_trigger_it():
    engine = WorldEngine(); now = datetime(2026, 9, 18, tzinfo=timezone.utc)
    ready = npc(stage=9, cultivation_exp=engine.required_exp(9), cultivation_rate=0)
    results = [engine.advance_npc(ready, tick, now, 12) for tick in range(1, 300)]
    assert any(result.npc.realm_key == "foundation_establishment" and result.npc.stage == 1 for result in results)
    exploring = npc(stage=1, activity="exploring", cultivation_exp=engine.required_exp(1) * .95, cultivation_rate=0)
    results = [engine.advance_npc(exploring, tick, now, 31) for tick in range(1, 500)]
    assert any(any(event["kind"] == "opportunity" for event in result.events) and
               any(event["kind"] == "breakthrough" for event in result.events) for result in results)


def test_npc_at_final_realm_cap_keeps_cultivating_without_breakthrough():
    engine = WorldEngine(); now = datetime(2026, 9, 18, tzinfo=timezone.utc)
    capped = npc(realm_key="human_immortal", stage=9, cultivation_exp=engine.required_exp(9, "human_immortal"), cultivation_rate=6)
    result = engine.advance_npc(capped, 3, now, 12)
    assert (result.npc.realm_key, result.npc.stage) == ("human_immortal", 9)


def test_world_engine_uses_injected_timing_and_outcome_rules():
    rules = game_rules.model_copy(update={
        "world_tick_minutes": 5,
        "world_max_offline_hours": 2,
        "world_explore_safe_chance": 1,
        "world_explore_opportunity_chance": 0,
        "world_explore_injury_chance": 0,
        "world_event_chance": 0,
    })
    engine = WorldEngine(rules)

    result = engine.advance_npc(npc(activity="exploring"), 1, datetime.now(timezone.utc), 99)

    assert engine.tick_minutes == 5
    assert engine.max_ticks == 24
    assert result.npc.activity == "cultivating"
    assert result.npc.injured_until is None
    assert engine.world_event(1, 99) is None
    assert not any(event["kind"].startswith("breakthrough") for event in result.events)
