# phase-1-core-loop Scope

## Open Decisions

- OPEN - owner: exact balance values for realm thresholds; default: use seed
  values that are easy to tune and deterministic in tests.

## Flow

1. Player opens the app.
2. Frontend requests `GET /game/state`.
3. Backend creates the initial player if none exists.
4. Backend applies offline cultivation from `last_cultivation_at`.
5. Backend returns one aggregate state with player, realm, spiritual root,
   cultivation rate, next-stage estimate, resources, active pet, dao partner,
   current activity, and recent logs.
6. Frontend renders the home screen with cultivation as the primary action
   surface.

## Entities

- Player: one local save profile, identified by its database id.
- Realm: seeded progression data, identified by its key.
- Spiritual root: seeded root profile assigned at start.
- Game log: timestamped event visible to the player.

## States

- Player cultivation state lives on the player record.
- Realm progression lives in realm seed data.
- Logs are append-only game records.

## Saved For Real

State must survive application restart and browser refresh through PostgreSQL.
No authoritative game value may live only in frontend memory.

## Resilience

| Case | Expected result |
|---|---|
| First launch with empty database | Seed data and initial player are created. |
| Browser refresh | `/game/state` returns the same saved player with updated offline progress. |
| Long offline gap | Progress is calculated from timestamps and capped only by realm data rules. |
| Missing asset | Frontend resolves to a local fallback asset key. |

## Deferred

- Breakthrough and failure consequences -> `phase-2-breakthrough-items`.
- Inventory, equipment, pills, and manuals as real item records ->
  `phase-2-breakthrough-items`.
- Exploration, loot, and battle -> `phase-3-exploration-battle`.
- NPC simulation, relationships, pets, and world events ->
  `phase-4-living-world`.

## Evidence

Automated:

- `pytest` passes backend engine and service tests.
- `GET /health` returns ok.
- `GET /game/state` returns initialized player state after database seed.

Manual:

- Start Docker Compose, open the frontend, and confirm the home screen shows
  name, realm, stage, cultivation, cultivation per minute, estimated next
  stage, spirit stones, combat power, pet, dao partner, and current activity.

## Closed

Open.

