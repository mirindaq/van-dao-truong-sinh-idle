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
Phase 7 entries are archived in decisions/phase-7-world-journeys.md.
Phase 8 entries are archived in decisions/phase-8-spirit-pets.md.
Phase 9 entries are archived in decisions/phase-9-alchemy.md.
Phase 10 entries are archived in decisions/phase-10-partner-craft.md.

## 2026-09-24 — design-overhaul — feature — Giao diện giấy tuyên sáng
Decision: Chủ dự án chọn giấy ngà, chữ mực, ngọc trầm và son đỏ;
điều hướng chia nhóm, tranh thủy mặc nguyên bản, Noto Serif cục bộ hỗ trợ tiếng Việt.
Giữ luật, API, save và chức năng hiện có; sửa nhãn chưa mở sai trạng thái.
Why: Các hệ thống cần cùng một phong cách, dễ đọc và dùng trên điện thoại.
Recorded in: DESIGN.md — Ngôn ngữ hình ảnh, Bố cục, Kiểm chứng

## 2026-09-24 — phase-11-game-feel — roadmap — Mở giai đoạn trùng tu cảm giác chơi
Decision: Trùng tu layout, hiệu ứng và tương tác toàn bộ game thành giai đoạn riêng phase-11-game-feel, không đổi luật, API hay save.
Why: Việc đụng cả 13 màn cần scope, danh sách kiểm chứng và một lần đóng rõ ràng.
Recorded in: ROADMAP.md — phase-11-game-feel; scopes/phase-11-game-feel.md

## 2026-09-25 — phase-11-game-feel — feature — Chuyển động, khoảnh khắc và cài đặt an toàn
Decision: Dùng CSS + ViewTransition làm nền, thêm motion và canvas-confetti ghim bản đã ra ≥7 ngày kèm overrides cho gói con; Động Phủ dạng cảnh sống; hiệu ứng cho đột phá, xuất quan, đan, đồ, thám hiểm, thân mật, chuyển màn và modal; hạt chỉ cho đột phá thành công và xuất quan sau vắng lâu; mọi khoảnh khắc có bản tĩnh khi giảm chuyển động và chỉ phát một lần mỗi biên nhận. Nút "Xuất quan" luôn xác nhận, bấm vùng báo cáo để nhảy số; modal chỉ chuyển động lúc mở; Nhân Vật bỏ hai chỉ số trùng topbar.
Why: Game cần cảm giác sống mà không làm chậm thao tác lặp, không hại người tắt chuyển động và không mở rủi ro chuỗi cung ứng.
Recorded in: DESIGN.md — Chuyển động; scopes/phase-11-game-feel.md — Open decisions, flow, evidence

