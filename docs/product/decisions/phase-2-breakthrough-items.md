## phase-2-breakthrough-items

Outcome: the player can prepare for breakthrough using persisted support items
and see those items affect a backend-calculated chance.

Risk retired: chance modifiers, failure consequences, item consumption, and
equipment persistence work without changing the core cultivation loop.

Not yet: exploration drops, battle rewards, detailed battle stats, and combat
resolution land in `phase-3-exploration-battle`.

Human decisions: one-time equipment pack for old and new saves; equipment adds
only combat power, not cultivation or breakthrough chance.

Evidence: backend 39 passed; frontend lint/typecheck/build passed; Playwright
20 passed; desktop/mobile/320px browser checks and migration/retry checks passed.

## 2026-09-17 — phase-2-breakthrough-items — feature — Persisted breakthrough items
Decision: Inventory owns Thanh Mộc Quyết and Tụ Khí Đan. A breakthrough uses zero
or one pill, adding ten percentage points with a 95% cap without lowering the
unsupported chance; a committed success or failure consumes one pill.
Why: Support preparation while preserving old saves and making retries safe.
Recorded in: PRODUCT.md; scopes/phase-2-breakthrough-items.md

## 2026-09-18 — phase-2-breakthrough-items — feature — One-time equipment pack
Decision: Each old or new save may claim one sword (+5), robe (+3), and amulet
(+2). Equipped slots persist and add only combat power; repeated claims or slot
requests do not duplicate ownership or bonuses.
Why: Give the inventory branch a persistent preparation action while leaving loot
and detailed battle design to Phase 3.
Recorded in: PRODUCT.md; scopes/phase-2-equipment.md
