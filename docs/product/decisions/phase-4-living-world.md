## phase-4-living-world

Outcome: NPCs and world events advance from timestamps and appear in saved world
news while the player is offline.

Risk retired: the game world feels alive without background workers.

Not yet: NPC relationships, dialogue, quests, permanent death, NPC economy,
custom portraits, multiplayer, PvP, WebSocket and external job systems.

Evidence: deterministic 10-minute simulation, persistent NPC/news/report state,
legacy-save migration and recovery paths passed 62 backend tests and 26 browser
tests; lint, typecheck and production build passed. Final review: Ready.

## 2026-09-18 — phase-4-living-world — feature — Dàn NPC khởi đầu
Decision: Owner chọn Tạ Vô Trần, Lạc Thanh Hàn và một tán tu; dùng chân dung
dự phòng trong bản đầu.
Why: Ưu tiên nhân vật từ bối cảnh đã có và thử các diễn biến khác nhau.
Recorded in: scopes/phase-4-living-world.md Open decisions và Entities.

## 2026-09-18 — phase-4-living-world — feature — Nhịp và tác động mô phỏng
Decision: Owner chọn nhịp 10 phút, bù tối đa 24 giờ/lần quay lại; sự kiện chỉ
thay đổi NPC và tin tức, không cấp loot hoặc buff/debuff cho player.
Why: Dùng nhịp nhanh hơn theo lựa chọn owner, kiểm chứng thế giới trước khi đổi
cân bằng player.
Recorded in: scopes/phase-4-living-world.md Open decisions, Simulation and content,
Resilience và Evidence.

## 2026-09-18 — phase-4-living-world — feature — Luật mô phỏng bản đầu
Decision: “Ok triển khai” phê duyệt các mặc định còn lại trong scope: hoạt động
80/20, kết quả thám du 60/25/15, tin thế giới 5%, cơ duyên cộng 10% yêu cầu tầng.
Why: Các thông số deterministic nhỏ đủ chứng minh thế giới sống trước khi thêm
quan hệ, loot, kinh tế hoặc gặp player.
Recorded in: PRODUCT.md Core Objects, Source Of Truth và Product Rules;
scopes/phase-4-living-world.md Simulation and content.

Archive note: moved from ROADMAP.md and DECISIONS.md when Phase 4 closed on
2026-09-21 after its final review returned Ready.
