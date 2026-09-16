# Product Contract

## Product

Van Dao Truong Sinh Idle is a single-player local xianxia idle game. The bet is
that long-term cultivation progression plus offline world simulation can make
the world feel alive without click-heavy play.

## Actors

- Player: the only real human actor.
- NPC: simulated cultivators, merchants, elders, dao partners, enemies, and
  wanderers controlled by game systems.
- World: the simulation layer that advances offline systems from timestamps.

## Core Objects

- Player profile: name, realm, cultivation, resources, roots, current activity.
- Realm: data-driven cultivation ladder and stage thresholds.
- Spiritual root: long-term affinity and cultivation modifier.
- Game log: durable event feed for player and world events.
- Breakthrough attempt: backend-decided realm/stage advancement attempt with
  preview chance, random roll, result, and persisted receipt.
- NPC, pet, inventory, equipment, alchemy, exploration, battle, and
  relationship objects are planned but not in Phase 1.

## Source Of Truth

- PostgreSQL is the source of truth for saved game state.
- Player cultivation state is decided by the `players` record.
- Realm progression is decided by seeded realm records, not hard-coded branches
  scattered through the app.
- Offline progress is decided by stored UTC timestamps and applied when state is
  loaded or an action is taken.
- Offline return reports and breakthrough receipts are decided by backend
  service metadata on game logs.
- Frontend state is display-only. Backend actions decide random rolls, rewards,
  progression, and persistence.

## Product Rules

- The player starts as a phàm nhân under Thanh Vân Sơn, finds the abandoned
  cave, receives Thanh Mộc Quyết, 10 linh thạch, and 3 Tụ Khí Đan, then enters
  Luyện Khí stage 1 after root inspection.
- Idle systems must not run continuous timers. They calculate elapsed time from
  saved timestamps.
- Randomness must go through a seedable random service.
- Game engines must be testable without HTTP.

## Access And Money

- Local single-player only.
- No real-money economy, user accounts, PvP, or multiplayer rules in the
  current product.

## Glossary

- Realm: a major cultivation rank such as Phàm Nhân, Luyện Khí, Trúc Cơ, or Kim
  Đan.
- Stage: a minor layer within a realm where the realm supports layers.
- Offline progress: advancement calculated from elapsed UTC timestamps rather
  than background timers.
- Opportunity: a rare, not fully predictable event or reward.

## Open

- OPEN - owner: exact Vietnamese display names are authoritative in UI copy;
  default is to use the names from `PROJECT_CONTEXT.md`.
