# Roadmap

Bet: a small but persistent Phase 1 loop can prove the idle cultivation feel
before broader xianxia systems are added.

## Status

| Milestone | Scope | Status |
|---|---|---|
| phase-1-core-loop | scopes/phase-1-core-loop.md | closed 2026-09-17 |
| phase-2-breakthrough-items | scopes/phase-2-breakthrough-items.md | closed 2026-09-18 |
| phase-3-exploration-battle | scopes/phase-3-exploration-battle.md | closed 2026-09-18 |
| phase-4-living-world | scopes/phase-4-living-world.md | closed 2026-09-21 |
| phase-5-game-configuration | scopes/phase-5-game-configuration.md | closed 2026-09-21 |
| phase-6-npc-relationships | scopes/phase-6-npc-relationships.md | closed 2026-09-22 |
| phase-7-world-journeys | scopes/phase-7-world-journeys.md | closed 2026-09-22 |
| phase-8-spirit-pets | scopes/phase-8-spirit-pets.md | open |
| phase-9-alchemy | scopes/phase-9-alchemy.md | not started |

## phase-8-spirit-pets

Outcome: the player can obtain, keep and activate one spirit pet whose saved
bonus is visible in the relevant game calculation.

Risk retired: companions can affect gameplay without duplicating equipment or
corrupting player progression.

Not yet: breeding and pet combat are deferred; alchemy lands in
`phase-9-alchemy`.

Human decisions: first pets, acquisition rules and bonus boundary.

Evidence: acquisition is idempotent; one active pet persists across restart;
its bonus is applied exactly once and removed when deactivated.

## phase-9-alchemy

Outcome: the player can spend saved materials on a recipe and receive a
persisted consumable through a retry-safe crafting action.

Risk retired: resource sinks and crafting work without item duplication.

Not yet: player trading and NPC economy require a later roadmap decision.

Human decisions: first recipes, costs, results and crafting duration.

Evidence: crafting commits ingredients and output atomically; replay returns
the same receipt; reload and redeploy preserve inventory and craft history.

## Dropped

- Multiplayer, PvP, Redis, Celery, Kafka, WebSocket, complex auth, and
  microservices are intentionally out of scope.
- Permanent NPC death and realtime combat are intentionally out of scope.
