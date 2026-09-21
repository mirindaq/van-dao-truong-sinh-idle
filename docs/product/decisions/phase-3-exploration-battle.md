## phase-3-exploration-battle

Outcome: the player can explore a location, resolve auto turn-based battle, and
receive logged rewards.

Risk retired: opportunity, battle log, and loot systems work without realtime
combat.

Not yet: autonomous NPC world changes land in `phase-4-living-world`.

Human decisions: first location reward tables.

Evidence: battle engine is pure and replayable; exploration saves result and
logs.

## 2026-09-18 — phase-3-exploration-battle — feature — Immediate Thanh Vân Sơn run
Decision: The first exploration location resolves immediately. A victory awards
10 Linh Thạch and 1 Tụ Khí Đan; defeat awards nothing but preserves its battle
log. Seeded battle snapshots and request ids make the result replayable.
Why: Prove exploration, auto turn-based combat, loot persistence and recovery
before adding timers, more locations or world simulation.
Recorded in: PRODUCT.md Core Objects and Product Rules;
scopes/phase-3-exploration-battle.md Open decisions, Flow, Resilience, Evidence

Archive note: moved from ROADMAP.md and DECISIONS.md during Phase 4 design.
This rotation preserves the recorded close; it does not certify new test evidence.
