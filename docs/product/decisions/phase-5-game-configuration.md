## phase-5-game-configuration

Outcome: the operator can change every gameplay tuning parameter through a
typed environment file and restart the app to apply the new rules.

Risk retired: balance values stop being scattered through engines, services
and seed data before more systems depend on them.

Not yet: live reload and an admin settings UI are deferred; NPC interaction
lands in `phase-6-npc-relationships` and uses the configured 12-hour cadence.

Evidence: the tuning audit and config checks passed; invalid rules fail before
serving; historical results retain their rule identity. Backend passed 81 tests,
frontend passed lint, typecheck, build and 27 browser tests. Final review: Ready.

## 2026-09-21 — phase-5-game-configuration — roadmap — Cấu hình cân bằng tập trung
Decision: Mở Phase 5 để chuyển mọi tham số ảnh hưởng gameplay sang cấu hình
environment có kiểu và kiểm tra; quan hệ NPC chuyển sang Phase 6 với cooldown
mặc định 12 giờ.
Why: Các hệ thống mới cần một nguồn tham số thống nhất, dễ chỉnh mà không sửa
rải rác engine, service và seed data.
Recorded in: ROADMAP.md phase-5-game-configuration;
scopes/phase-5-game-configuration.md và scopes/phase-6-npc-relationships.md.

## 2026-09-21 — phase-5-game-configuration — contract — Luật mới không viết lại lịch sử
Decision: Sau restart, cấu hình mới chỉ áp dụng cho hành động và phép tính mới;
state, receipt và report đã commit giữ nguyên kết quả cùng phiên bản luật cũ.
Why: Save phải giải thích và phát lại được dù operator thay đổi cân bằng.
Recorded in: PRODUCT.md Source Of Truth và Product Rules;
scopes/phase-5-game-configuration.md Open decisions, Saved for real và Resilience.

## 2026-09-21 — phase-5-game-configuration — contract — Cấu hình sai dừng startup
Decision: Backend từ chối khởi động khi gameplay environment thiếu biến bắt
buộc, sai kiểu/range hoặc có ngưỡng mâu thuẫn, và báo rõ biến/nhóm gây lỗi.
Why: Không cho save chạy dưới bộ luật fallback hoặc cân bằng không xác định.
Recorded in: PRODUCT.md Product Rules;
scopes/phase-5-game-configuration.md Open decisions, The flow và Resilience.

## 2026-09-21 — phase-5-game-configuration — feature — Registry phiên bản luật
Decision: Startup đăng ký mỗi rules version với đúng một fingerprint; thay đổi
gameplay phải dùng version lớn hơn, rollback chỉ dùng lại cặp đã đăng ký.
Why: Hai instance hoặc một deploy quên tăng version không được chạy hai bộ luật
khác nhau dưới cùng định danh.
Recorded in: PRODUCT.md Source Of Truth;
scopes/phase-5-game-configuration.md Configuration inventory và Resilience.

Archive note: moved from ROADMAP.md and DECISIONS.md when Phase 5 closed on
2026-09-21 after its final review returned Ready.
