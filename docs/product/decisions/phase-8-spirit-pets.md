## phase-8-spirit-pets

Outcome: the player can obtain, keep and activate one spirit pet whose saved
bonus is visible in the relevant game calculation.

Risk retired: companions can affect gameplay without duplicating equipment or
corrupting player progression.

Not yet: breeding and pet combat are deferred; alchemy lands in
`phase-9-alchemy`.

Human decisions: first pets, acquisition rules and bonus boundary.

Evidence: acquisition is idempotent; one active pet persists across restart;
its bonus is applied exactly once and removed when deactivated. Backend passed
112 tests. Frontend passed lint, typecheck, build and 32 browser tests,
including the pet bond, rest, reload and recall path. Final review: Ready.

## 2026-09-23 — phase-8-spirit-pets — feature — Một linh thú có chiến lực và tốc độ tu vi
Decision: Mỗi save kết một trong ba loài Thanh Xà, Hỏa Hồ, Vân Tước. Đang theo thì chiến lực cộng khoản riêng, tốc độ = gốc × linh căn × hệ số + lượng mỗi phút. Cho nghỉ thì hết bonus, tu vi đã chốt không rút. Số khởi đầu: Thanh Xà 6 / 1.05 / 0.2, Hỏa Hồ 4 / 1.10 / 0.4, Vân Tước 2 / 1.20 / 0.8.
Why: Linh thú phải ảnh hưởng chơi mà không thành ô trang bị và không sửa đột phá.
Recorded in: PRODUCT.md › Core Objects, Source Of Truth, Product Rules; scopes/phase-8-spirit-pets.md
