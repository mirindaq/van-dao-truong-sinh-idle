## phase-10-partner-craft

Outcome: the player can meet five additional female cultivators, build affinity
with any of eight NPCs, keep every reached dao partner, see their stacked bonus,
and craft a second recipe without duplicating items.

Risk retired: a larger NPC roster and several partners can affect play, and a
second recipe can exist, without losing old saves, granting items twice or
rewriting old receipts.

Not yet: gifts, quests, pet breeding and NPC trade stay unplaced.

Human decisions: who can be the partner, what the bonus touches, and the
second recipe. Settled 2026-09-23: any number of eight NPCs including five new
female cultivators, both combat and cultivation, and a 6-herb batch.

Evidence: existing saves gain the five NPCs with distinct portraits; each
partner persists across restart and that person's bonus is removed when the
bond ends; the batch recipe commits its own cost and output once per request.
Backend passed 137 tests. Frontend passed lint, typecheck, build and 37
browser tests; a manual pass on the real app covered bonding, stacking,
dismissing, the six-herb batch and eight portraits. Final review: Ready.

## 2026-09-23 — phase-10-partner-craft — feature — Nhiều đạo lữ và mẻ 6 thảo
Decision: Cả ba NPC đạt 8 thiện cảm đều có thể cùng là đạo lữ; mỗi người đang
kết cộng +3 chiến lực, ×1.05 và +0.1 tu vi/phút. Mẻ 6 thảo ra 2 đan tồn tại
cùng mẻ 3 ra 1 và mỗi mã yêu cầu chỉ ghi một lần.
Why: Bonus cần cộng và gỡ độc lập, còn công thức mới không được phá biên nhận cũ.
Recorded in: PRODUCT.md — Core Objects, Source Of Truth, Product Rules

## 2026-09-23 — phase-10-partner-craft — feature — Năm nữ NPC có chân dung riêng
Decision: Thêm Diệp Thanh Trúc, Hồng Liên, Bạch Nguyệt, Lôi Tử Yên và Vân
Nhược Ly; cả năm có hội thoại, thiện cảm, chân dung riêng và có thể kết đạo lữ
ở ngưỡng 8. Save cũ nhận mỗi người đúng một lần.
Why: Roster đạo lữ cần phong phú hơn mà không làm mất NPC, quan hệ hay duyên cũ.
Recorded in: PRODUCT.md — Core Objects; ROADMAP.md — phase-10-partner-craft;
scopes/phase-10-partner-craft.md — flow, entities, resilience, evidence
