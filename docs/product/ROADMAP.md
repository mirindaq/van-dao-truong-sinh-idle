# Roadmap

Bet: a small but persistent Phase 1 loop can prove the idle cultivation feel
before broader xianxia systems are added.

## Status

| Milestone | Scope | Status |
|---|---|---|
| phase-1-core-loop | scopes/phase-1-core-loop.md | open |
| phase-2-breakthrough-items | scopes/phase-2-breakthrough-items.md | not started |
| phase-3-exploration-battle | scopes/phase-3-exploration-battle.md | not started |
| phase-4-living-world | scopes/phase-4-living-world.md | not started |

## phase-1-core-loop

Outcome: the player can open the game, see a persisted cultivator, receive
offline cultivation progress, and inspect realm/root state from one game-state
endpoint.

Risk retired: the core idle model, persistence boundary, and backend/frontend
split are proven before adding wider systems.

Not yet: breakthrough, inventory, equipment, alchemy, exploration, battle, NPC
simulation, pets, dao partners, and complex world events land in later
milestones.

Human decisions: exact balancing numbers remain adjustable seed data.

Evidence: backend tests prove deterministic idle progress; `/game/state`
returns an initialized player; frontend renders the home state without putting
authoritative game logic in the browser.

## phase-2-breakthrough-items

Outcome: the player can prepare for and attempt breakthrough using persisted
items and backend-calculated chance.

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

