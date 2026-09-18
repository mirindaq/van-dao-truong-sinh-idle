# Roadmap

Bet: a small but persistent Phase 1 loop can prove the idle cultivation feel
before broader xianxia systems are added.

## Status

| Milestone | Scope | Status |
|---|---|---|
| phase-1-core-loop | scopes/phase-1-core-loop.md | closed 2026-09-17 |
| phase-2-breakthrough-items | scopes/phase-2-breakthrough-items.md | open |
| phase-3-exploration-battle | scopes/phase-3-exploration-battle.md | not started |
| phase-4-living-world | scopes/phase-4-living-world.md | not started |

## phase-2-breakthrough-items

Outcome: the player can prepare for breakthrough using persisted support items
and see those items affect a backend-calculated chance.

Risk retired: chance modifiers, failure consequences, and item consumption are
modeled safely.

Not yet: exploration drops and battle rewards land in `phase-3-exploration-battle`.

Human decisions: final failure consequence tuning.

Evidence: breakthrough chance and random roll are deterministic under seed;
failed breakthrough does not kill the player.

## phase-3-exploration-battle

Outcome: the player can explore a location, resolve auto turn-based battle, and
receive logged rewards.

Risk retired: opportunity, battle log, and loot systems work without realtime
combat.

Not yet: autonomous NPC world changes land in `phase-4-living-world`.

Human decisions: first location reward tables.

Evidence: battle engine is pure and replayable; exploration saves result and
logs.

## phase-4-living-world

Outcome: NPCs and world events advance from timestamps and appear in world logs
while the player is offline.

Risk retired: the game world feels alive without background workers.

Not yet: multiplayer, PvP, WebSocket, and external job systems are dropped until
the owner asks for them.

Human decisions: which named NPCs receive portraits and story priority.

Evidence: NPC simulation advances from elapsed time; world log contains notable
events after offline gaps.

## Dropped

- Multiplayer, PvP, Redis, Celery, Kafka, WebSocket, complex auth, and
  microservices are intentionally out of scope.
