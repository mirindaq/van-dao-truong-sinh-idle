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
Phase 6 entries are archived in decisions/phase-6-npc-relationships.md.

## 2026-09-22 — phase-7-world-journeys — contract — Hành trình có giờ
Decision: Thanh Vân Sơn vẫn xong ngay. Hậu Sơn, Ngoại Vi và Linh Mạch chờ 5,
10 và 15 phút server. Thưởng một lần: nguyên liệu, trang bị thường, trang bị
tốt hơn bộ khởi đầu.
Why: Owner giữ lượt đang chạy và rút thời gian để thấy kết quả trong một phiên.
Recorded in: PRODUCT.md Product Rules;
scopes/phase-7-world-journeys.md Open decisions, The flow và Resilience.
