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
- Inventory: item definitions and quantities owned by a player, including
  Tụ Khí Đan and the non-consumable Thanh Mộc Quyết.
- Equipment: owned items may occupy one of six saved slots. Equipped items do
  not leave inventory; total combat power is the player base value plus the
  bonuses of equipped items. Equip/unequip does not change cultivation or
  breakthrough chance.
- NPC, pet, alchemy, exploration, battle, and
  relationship objects are planned but not in Phase 1.

## Source Of Truth

- PostgreSQL is the source of truth for saved game state.
- Player cultivation state is decided by the `players` record.
- Item quantities are decided only by `owned_items`, keyed by player and item.
  The compatibility player pill count in API responses is derived from inventory.
- Equipped slots and the one-time equipment-pack claim are decided by
  PostgreSQL. The pack grants one Thanh Trúc Kiếm, one Vải Thô Đạo Bào and one
  Thanh Mộc Ngọc Bội to old and new saves, and repeated claims grant nothing.
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
- New Game grants three pills and one manual once, in the player creation
  transaction. Migrating an existing save preserves its remaining pills and
  manual; loading, restarting or repeating a migration grants nothing extra.
- A breakthrough may use zero or one Tụ Khí Đan, for minor or major advancement.
  The pill adds ten percentage points after the root modifier, capped at 95%,
  without reducing an already higher unsupported chance.
- A committed supported success or failure consumes exactly one pill. Failure
  loses 10% of the required cultivation, capped by current cultivation, with
  no death, injury or debuff. Previewing, cancelling or rejection consumes none.
- Item use, progression and receipt commit atomically. Replaying the same request
  returns its receipt; reusing an id with a different payload is rejected.
  Browser pending data only preserves the retry payload, never game ownership.
- Thanh Mộc Quyết is owned, non-consumable and grants no additional bonus in
  this slice. Only the starting pills are supplied; new sources await Phase 3.
- Equipment in this slice grants only +5 sword, +3 robe or +2 amulet combat
  power. Loot, random combat stats, durability, upgrades and detailed battle
  attributes belong to Phase 3.

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
