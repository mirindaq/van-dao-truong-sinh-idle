# Decisions

<!--
Append-only, newest last. One entry per decision that moved a rule, a scope, or
a deferral — written by the plan step that records it, not from memory at the
end. The `Recorded in` line is what keeps this log from being the only place a
rule lives: the rule itself goes into PRODUCT.md, ROADMAP.md, or the scope, and
this entry points there.

This file holds ONE milestone's worth — the "tail" every task reads IS the
file. Closing a milestone rotates its entries to decisions/<milestone-id>.md,
so the file never grows past a milestone and history stays greppable per
milestone. Nothing operational is lost in the move: the rules themselves
already live where `Recorded in` points. History is SEARCHED, never read
whole — the fixed entry heading is the index; grep decisions/ for the word,
then read only the file the hit names. A rotation the close missed is
finished by the next session's Before-any-task tripwire, before routing.
Delete this comment once the first entry lands.

Entry shape:

## <date> — <milestone id> — <kind: feature | bug | roadmap | contract> — <title>
Decision: <one or two sentences>
Why: <the reason, in one>
Recorded in: <file and section> | none — reply only
-->

Phase 3 entries are archived in decisions/phase-3-exploration-battle.md.
Phase 4 entries are archived in decisions/phase-4-living-world.md.
Phase 5 entries are archived in decisions/phase-5-game-configuration.md.

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
