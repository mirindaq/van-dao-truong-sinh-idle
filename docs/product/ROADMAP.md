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
| phase-6-npc-relationships | scopes/phase-6-npc-relationships.md | open |
| phase-7-world-journeys | scopes/phase-7-world-journeys.md | not started |
| phase-8-spirit-pets | scopes/phase-8-spirit-pets.md | not started |
| phase-9-alchemy | scopes/phase-9-alchemy.md | not started |

## phase-6-npc-relationships

Outcome: the player can meet a living-world NPC, choose a response, and return
later to see the saved relationship and conversation history.

Risk retired: Phase 4 NPCs become characters the player can know rather than
status cards that only advance on their own.

Not yet: quests, NPC combat, gifts, romance/dao partners and relationship
rewards land in a later relationship expansion; multiple maps and equipment
loot land in `phase-7-world-journeys`; pets land in `phase-8-spirit-pets`;
crafting lands in `phase-9-alchemy`.

Human decisions: first interaction format, encounter cadence, and whether
affinity changes anything beyond dialogue/news in this slice.

Evidence: a player choice produces one saved interaction and affinity change;
duplicate/retried choices do not apply twice; the NPC profile and history
survive reload, restart and a lost response.

## phase-7-world-journeys

Outcome: the player can choose among several locations, complete a timed
journey, and receive location-specific equipment or materials.

Risk retired: exploration can support progression beyond one immediate battle.

Not yet: pet capture lands in `phase-8-spirit-pets`; material crafting lands
in `phase-9-alchemy`; realtime combat remains dropped.

Human decisions: locations, journey durations and loot tables.

Evidence: journeys persist through closing the browser; retry cannot duplicate
their battle or reward; each location visibly produces its own encounters.

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
