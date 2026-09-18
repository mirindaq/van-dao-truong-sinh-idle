# phase-2-equipment — Mặc đồ và tăng chiến lực

Milestone: phase-2-breakthrough-items; bổ sung scopes/phase-2-breakthrough-items.md.
Outcome: Nhận gói đồ một lần, mặc/tháo đồ sở hữu và thấy chiến lực được lưu đúng.

## Open decisions
- Settled 2026-09-17 (owner): Gói nhận một lần trong Túi Đồ cho cả save cũ/mới,
  gồm Thanh Trúc Kiếm, Vải Thô Đạo Bào và Thanh Mộc Ngọc Bội; không cấp lại.
- Settled 2026-09-17 (owner): Chỉ cộng chiến lực; giữ tu luyện và tỷ lệ đột phá.
- Giá trị khởi đầu có thể chỉnh: kiếm +5, áo +3, ngọc bội +2.

## The flow
1. Mở Túi Đồ, thấy gói trang bị có thể nhận nếu save chưa nhận.
2. Nhận gói: có một mỗi món, quyền nhận chuyển thành đã nhận.
3. Mở Trang Bị: sáu ô vũ khí/mũ/áo/giày/nhẫn/ngọc bội, ban đầu trống.
4. Mặc món sở hữu: đúng ô hiển thị tên và bonus; tổng chiến lực tăng tương ứng.
5. Tháo hoặc thay món cùng ô: bonus thay theo món mới, không cộng dồn.
6. Mở Nhân Vật/túi, refresh hoặc mở lại: slot và tổng chiến lực khớp backend.

## Entities
- Item: key, tên, mô tả, loại, slot hợp lệ, bonus chiến lực; identity là key.
- Owned item: player + item, số lượng; mặc không tiêu hao và vẫn thuộc túi.
- Equipped slot: player + slot, item đang mặc hoặc trống; một món tối đa một ô.
- Pack claim: thuộc save; chưa nhận/đã nhận, không thể đảo lại bằng browser.

## States
- Gói: chưa nhận -> đã nhận (người chơi), cùng transaction với ba món được cấp.
- Ô: trống -> món A -> món B hoặc trống (người chơi).
- PostgreSQL quyết định sở hữu/slot/quyền nhận. Chiến lực tổng được backend
  suy ra từ chiến lực nền + bonus đang mặc; đột phá chỉ tăng chiến lực nền.

## Saved for real
- Save cũ/mới đều có thể nhận một lần. Migration không tự cấp hoặc tự mặc đồ.
- Refresh, xóa storage, mở browser khác, restart/redeploy giữ slot/quyền nhận.
- Kho đan, công pháp, tiến độ và biên nhận cũ không thay đổi khi nâng cấp.

## Resilience
| Case | Decided behaviour |
|---|---|
| Nhận gói lặp/hai tab | Cấp đúng một bộ, trả state đã nhận. |
| Mặc/tháo lặp | Đặt trạng thái ô, không toggle hay cộng dồn bonus. |
| Đồ sai ô/không sở hữu/pill/manual | Từ chối, giữ slot và chiến lực. |
| Hai tab sửa cùng ô | Khóa save; thao tác hợp lệ xử lý sau là trạng thái cuối. |
| Mất reply | Đồng bộ lại trước thao tác mới, không tự gửi lệnh đảo ngược. |
| Lỗi commit | Không có gói nhận dở hoặc slot và chiến lực lệch nhau. |
| Đột phá khi đang mặc đồ | Chỉ tăng chiến lực nền; bonus trang bị cộng sau. |
| Thiếu ảnh | Fallback local, tên/bonus/thao tác vẫn hiển thị. |

## Deferred
- Loot, chỉ số chiến đấu chi tiết, combat -> Phase 3.
- Bonus công pháp, cường hóa/độ bền/random stats không thuộc đợt này;
  muốn thêm cần định phạm vi trong roadmap trước.

## Evidence
Automated:
- [x] E-1: Migration 0004 -> head giữ save/kho/receipt, chưa nhận đồ; chạy lại ổn.
- [x] E-2: Gói nhận một lần qua request lặp/đồng thời; rollback không cấp dở.
- [x] E-3: Mặc/tháo/thay đúng bonus, giữ số lượng, restart giữ ô.
- [x] E-4: Sai slot/đồ không sở hữu bị từ chối; hai request không nhân bonus.
- [x] E-5: Đột phá chỉ tăng nền, tu luyện và xác suất không đổi do trang bị.
- [x] E-6: Full backend/frontend tests và lint/typecheck/build đạt.
Manual, at close:
- [x] E-7: Nhận/mặc/tháo trên desktop/mobile, không overflow ở 320px, ảnh và keyboard ổn.
- [x] E-8: Ngắt reply sau commit, đồng bộ lại; reload/context mới giữ đồ và slot.

## Closed
Closed 2026-09-18 — Codex. Backend 39 passed, Playwright 20 passed,
lint/typecheck/build passed; browser trực tiếp đã kiểm tra gói, slot, retry,
keyboard và 320px. Không còn deferred item trong scope này ngoài Phase 3.
