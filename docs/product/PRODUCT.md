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
- Spirit pet: one bond per save, chosen from Thanh Xà, Hỏa Hồ or Vân Tước.
  While active it adds its own combat-power amount and changes cultivation
  speed. NPC relationships, pending
  prompts and interaction receipts are saved per save.
- Dao partner: one saved row per save and NPC. Any of the three existing NPCs
  at affinity 8 may be active at once; dismissing one preserves every other row.

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
- PostgreSQL decides each NPC relationship, pending conversation and immutable
  interaction receipt. Browser storage only preserves a request payload for
  retry; browser time never opens a conversation turn.
- PostgreSQL decides the one spirit pet bond and whether it is active.
  The typed rules object decides each species' combat amount, cultivation
  factor and flat per minute. The frontend only displays them.
- PostgreSQL decides each alchemy receipt and the inventory quantities it
  changes. The typed rules object decides that the two recipes spend 3 herbs
  for 1 pill or 6 herbs for 2 pills. The frontend only displays the recipes.
- PostgreSQL decides each dao-partner row, keyed by save and NPC. The typed
  rules object decides the affinity threshold and each active partner's bonus.

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
  power. Journey loot is a configured location reward. Random combat stats,
  durability and upgrades remain deferred.
- Thanh Vân Sơn exploration resolves immediately. Under default rules it has a
  20% empty encounter; victory awards 10 Linh Thạch and 1 Tụ Khí Đan. Hậu Sơn,
  Ngoại Vi and Linh Mạch are timed journeys of 5, 10 and 15 minutes. One journey
  may be in progress. Completion grants that place's reward once. Seeded
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
- NPC affinity changes dialogue, forms of address and NPC news. Reaching 8 only
  permits the player to form a dao-partner bond; affinity itself grants no bonus.
- An active spirit pet adds its combat amount once, separate from equipment.
  Cultivation per minute is base × root × that pet's factor, plus that pet's
  flat amount, each part once. Resting or having no pet uses factor 1 and flat
  0. Turning the pet on or off settles cultivation first and does not remove
  settled cultivation. It does not change breakthrough chance, inventory,
  equipment slots or NPC affinity.
- Crafting one Tụ Khí Đan spends 3 Vân Linh Thảo and grants 1 pill in the same
  saved write, immediately. The same request returns that receipt and does not
  craft again. Fewer than 3 herbs changes nothing. Crafting does not change
  combat power, cultivation speed, equipment or the spirit pet.
- The batch recipe `recipe/qi_pill_batch` spends 6 Vân Linh Thảo and grants 2
  Tụ Khí Đan in one saved write. The 3-for-1 recipe remains available, and each
  request id commits at most one recipe once.
- Each active dao partner adds +3 combat power, multiplies cultivation by 1.05
  and adds 0.1 cultivation per minute. Bonuses stack per active partner; no
  partner uses factor 1 and flat 0. Dismissing one removes only that share and
  never changes breakthrough chance or already settled cultivation.

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
