## phase-9-alchemy

Outcome: the player can spend saved materials on a recipe and receive a
persisted consumable through a retry-safe crafting action.

Risk retired: resource sinks and crafting work without item duplication.

Not yet: player trading and NPC economy require a later roadmap decision.

Human decisions: first recipes, costs, results and crafting duration.

Evidence: crafting commits ingredients and output atomically; replay returns
the same receipt; reload and redeploy preserve inventory and craft history.
Backend passed 121 tests. Frontend passed lint, typecheck, build and 34
browser tests, including the craft, reload and replay path. Final review: Ready.

## 2026-09-23 — phase-9-alchemy — feature — Luyện một Tụ Khí Đan
Decision: Một công thức, xong ngay: 3 Vân Linh Thảo thành 1 Tụ Khí Đan. Cùng mã không luyện lần hai. Không đủ thảo thì túi không đổi.
Why: Tiêu nguyên liệu phải ghi cùng thành phẩm, không nhân đan khi gửi lại.
Recorded in: PRODUCT.md › Core Objects, Source Of Truth, Product Rules; scopes/phase-9-alchemy.md
