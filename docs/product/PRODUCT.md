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
- Exploration run: a persisted location attempt with an immutable battle log,
  result and reward receipt.
- Inventory: item definitions and quantities owned by a player, including
  Tụ Khí Đan and the non-consumable Thanh Mộc Quyết.
- Equipment: owned items may occupy one of six saved slots. Equipped items do
  not leave inventory; total combat power is the player base value plus the
  bonuses of equipped items. Equip/unequip does not change cultivation or
  breakthrough chance.
- NPC: a saved simulated cultivator with realm progress, activity, location,
  injury state and an event history; identity is save plus stable NPC key.
- World state: one per save, with a deterministic seed, rules version and the
  last processed 10-minute tick. World events and unread return reports derive
  from its committed ticks.
- Pet, alchemy and relationship objects remain planned.

## Source Of Truth

- PostgreSQL is the source of truth for saved game state.
- Player cultivation state is decided by the `players` record.
- Item quantities are decided only by `owned_items`, keyed by player and item.
  The compatibility player pill count in API responses is derived from inventory.
- Equipped slots and the one-time equipment-pack claim are decided by
  PostgreSQL. The pack grants the configured quantity of Thanh Trúc Kiếm, Vải
  Thô Đạo Bào and Thanh Mộc Ngọc Bội; repeated claims grant nothing.
- Realm progression is decided by seeded realm records, not hard-coded branches
  scattered through the app.
- Offline progress is decided by stored UTC timestamps and applied when state is
  loaded or an action is taken.
- Offline return reports and breakthrough receipts are decided by backend
  service metadata on game logs.
- Frontend state is display-only. Backend actions decide random rolls, rewards,
  progression, and persistence.
- NPC state, world time, world events and return reports are decided by
  PostgreSQL. Opening or syncing advances them under the same single-save lock;
  browser time and browser storage never advance the world.
- A typed game-rules object loaded from environment is the source of runtime
  gameplay parameters. PostgreSQL remains the source of committed state and
  receipts; changing rules never rewrites a historical result.
- PostgreSQL registers each rules version with exactly one fingerprint before
  the backend accepts requests. A changed fingerprint needs a greater unused
  version; rollback may reuse an already registered matching pair.

## Product Rules

- Under the default rules, the player starts under Thanh Vân Sơn, finds the
  abandoned cave, receives one Thanh Mộc Quyết, 10 linh thạch and 3 Tụ Khí Đan,
  then enters Luyện Khí stage 1 after root inspection. Configured starting
  values replace those defaults only for a newly created save.
- Idle systems must not run continuous timers. They calculate elapsed time from
  saved timestamps.
- Randomness must go through a seedable random service.
- Game engines must be testable without HTTP.
- New Game grants the configured pills and manuals once, in the player creation
  transaction. Migrating an existing save preserves its remaining inventory;
  loading, restarting or repeating a migration grants nothing extra.
- A breakthrough may use zero or one Tụ Khí Đan, for minor or major advancement.
  Under default rules the pill adds ten percentage points after the root
  modifier, capped at 95%, without reducing an already higher unsupported chance.
- A committed supported success or failure consumes exactly one pill. Failure
  loses 10% of the required cultivation, capped by current cultivation, with
  no death, injury or debuff. Previewing, cancelling or rejection consumes none.
- Item use, progression and receipt commit atomically. Replaying the same request
  returns its receipt; reusing an id with a different payload is rejected.
  Browser pending data only preserves the retry payload, never game ownership.
- Thanh Mộc Quyết is owned, non-consumable and grants no additional bonus in
  this slice. Only the starting pills are supplied; new sources await Phase 3.
- Under default rules, equipment grants +5 sword, +3 robe or +2 amulet combat
  power. Loot, random combat stats, durability and upgrades remain deferred.
- Exploration resolves immediately. Under default rules Thanh Vân Sơn has a
  20% empty encounter; victory awards 10 Linh Thạch and 1 Tụ Khí Đan. Seeded
  randomness and request-id replay prevent a second battle or reward.
- Under default rules, the living world advances in deterministic 10-minute
  ticks and processes at most 24 hours per return without a background worker.
- Phase 4 starts Tạ Vô Trần, Lạc Thanh Hàn and one unnamed wanderer exactly once
  per save. Their cultivation, expeditions, opportunities and injuries affect
  only NPC state and world news; they never grant player loot, buffs or debuffs.
- Every probability, duration, cap, reward, starting quantity, stat modifier,
  progression curve and seeded gameplay stat is configured through environment.
  Configuration is typed and validated at startup; changes require restart and
  a new rules version. Display copy, stable keys and asset paths are content,
  not gameplay parameters.

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
