## phase-6-npc-relationships

Outcome: the player can meet a living-world NPC, choose a response, and return
later to see the saved relationship and conversation history.

Risk retired: Phase 4 NPCs become characters the player can know rather than
status cards that only advance on their own.

Not yet: quests, NPC combat, gifts, romance/dao partners and relationship
rewards land in a later relationship expansion; multiple maps and equipment
loot land in `phase-7-world-journeys`; pets land in `phase-8-spirit-pets`;
crafting lands in `phase-9-alchemy`.

Evidence: a player choice produces one saved interaction and affinity change;
duplicate/retried choices do not apply twice; the NPC profile and history
survive reload, restart and a lost response. Backend passed 95 tests, frontend
passed lint, typecheck, build and 30 browser tests. Final review: Ready.

## 2026-09-21 — phase-6-npc-relationships — roadmap — Mở quan hệ NPC
Decision: Phase 6 đề xuất vòng gặp gỡ, lựa chọn hội thoại và thiện cảm lưu bền;
mở rộng thám hiểm, linh thú và luyện đan lần lượt nằm ở Phase 7–9.
Why: Quan hệ NPC dùng trực tiếp thế giới sống vừa hoàn tất mà chưa trộn thêm
loot, sức mạnh hoặc kinh tế vào cùng một milestone.
Recorded in: ROADMAP.md phase-6 đến phase-9;
scopes/phase-6-npc-relationships.md.

## 2026-09-21 — phase-6-npc-relationships — feature — Hội thoại ba lựa chọn
Decision: Mỗi lượt gặp NPC là một tình huống ngắn với ba lựa chọn lời đáp;
backend lưu lựa chọn, phản hồi và thay đổi thiện cảm trong cùng receipt.
Why: Tạo quyết định đủ rõ để NPC có cá tính nhưng vẫn giữ vòng tương tác nhỏ.
Recorded in: scopes/phase-6-npc-relationships.md Open decisions, The flow,
Entities và Resilience.

## 2026-09-21 — phase-6-npc-relationships — contract — Thiện cảm chỉ đổi nội dung
Decision: Thiện cảm chỉ thay đổi hội thoại, cách xưng hô và tin NPC; không cấp
vật phẩm, sức mạnh, buff, quest hoặc mở quan hệ thưởng trong Phase 6.
Why: Giữ vòng gặp gỡ tập trung vào nhân vật và chứng minh persistence trước khi
gắn thêm hệ thống phần thưởng.
Recorded in: PRODUCT.md Source Of Truth và Product Rules;
scopes/phase-6-npc-relationships.md Open decisions, Deferred và Evidence.
