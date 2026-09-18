# phase-3-exploration-battle — Thám hiểm và chiến đấu

Milestone from ROADMAP.md; rules from PRODUCT.md.
Outcome: Người chơi chọn một địa điểm, giải quyết trận auto turn-based và nhận
phần thưởng được lưu cùng nhật ký.

## Open decisions
- Settled 2026-09-18 (owner): Thanh Vân Sơn thưởng 10 Linh Thạch và 1 Tụ Khí
  Đan; trang bị/đồ hiếm vẫn do gói Phase 2.
- Settled 2026-09-18 (owner): một lượt xử lý ngay, không tiêu hao; thời gian
  offline để Phase 4.

## The flow
1. Người chơi mở Thám Hiểm và thấy địa điểm Thanh Vân Sơn, cấp nguy hiểm,
   thời gian xử lý và nút bắt đầu.
2. Người chơi bắt đầu một lượt; backend tạo một encounter đang xử lý và khóa
   không cho tạo lượt thứ hai.
3. Backend resolve encounter: không gặp địch hoặc gặp một quái vật, sau đó
   chạy auto turn-based battle nếu cần.
4. Người chơi thấy kết quả, battle log theo lượt, phần thưởng hoặc lý do thất
   bại; state và nhật ký được lưu.
5. Người chơi mở lại sau refresh/restart và thấy kết quả, loot và nhật ký cũ.

## Entities
- Location: key, tên, nguy hiểm, danh sách encounter; identity là key.
- Exploration run: player, location, request id, state, kết quả, thời điểm;
  identity player + request id.
- Combatant: tên, HP, attack, defense, speed; dữ liệu battle snapshot, không
  đọc lại chỉ số đang đổi của player sau khi trận bắt đầu.
- Battle log: thứ tự lượt, hành động, sát thương, HP còn lại, kết quả.
- Reward: item/resource key và quantity; phần thưởng đã nhận gắn với run.

## States
```
Exploration run: ready → resolving → victory / defeat / empty (backend).
resolving là ngắn hạn; mọi kết quả cuối là terminal và được đọc lại từ DB.
Source of truth: exploration run và reward records; frontend chỉ hiển thị.
```

## Saved for real
- Run, kết quả, battle log, reward và nhật ký sống qua refresh, browser mới,
  restart và deploy.
- Retry cùng request id trả đúng kết quả cũ; không battle lại, không phát thưởng
  lần hai. Run khác tạo encounter mới.
- Player inventory và chiến lực cập nhật cùng transaction với reward cuối.

## Resilience
| Case | Decided behaviour |
|---|---|
| Bấm bắt đầu hai lần | Một run được tạo; request lặp trả run đó. |
| Refresh khi đang resolve | Đọc trạng thái cuối từ backend; không tạo run mới. |
| Mất reply sau commit | Mở lại/đồng bộ trả đúng kết quả và reward đã lưu. |
| Battle thất bại | Không nhận reward; battle log và lý do vẫn được lưu. |
| Không gặp địch | Run kết thúc `empty`, không tạo battle giả; reward theo bảng địa điểm. |
| Hai tab tranh lượt | Khóa save; chỉ một run resolving hợp lệ. |
| RNG lỗi trước commit | Không reward, không run terminal; retry cùng request id an toàn. |
| Thiếu asset quái vật | Dùng fallback local, log và kết quả không đổi. |

## Deferred
- Nhiều địa điểm, loot từ quest/cửa hàng và chiến đấu realtime → Phase 4 hoặc
  roadmap decision trước khi mở rộng.
- Encounter NPC, pet, đạo lữ, world event → phase-4-living-world.
- PvP, multiplayer, WebSocket, background workers → Dropped trong roadmap.

## Evidence
Automated:
- [x] E-1: Location và encounter seed đọc được; empty run lưu đúng.
- [x] E-2: Battle engine pure, seed tái hiện cùng log/result.
- [x] E-3: Victory cập nhật reward/inventory/log cùng transaction.
- [x] E-4: Defeat không nhận reward nhưng lưu battle log và lý do.
- [x] E-5: Duplicate/concurrent request chỉ có một run, một battle, một reward.
- [x] E-6: Retry sau lỗi/mất reply trả receipt cũ; restart giữ nguyên state.
- [x] E-7: Full backend/frontend tests và migration pass.
Manual, at close:
- [x] E-8: Mở địa điểm, chạy battle, xem log và loot trên desktop/mobile; 320px
  không overflow, keyboard và fallback asset hoạt động.
- [x] E-9: Reload/clear storage/reopen sau victory và defeat; reward không nhân.

## Closed
Hoàn tất 2026-09-18. Backend 47 test và frontend 23 test pass; exploration
Playwright 3 test pass, gồm desktop/mobile/320px và mất reply; browser kiểm tra
route Thám Hiểm, nút bắt đầu, kết quả lưu và console/errors không có lỗi.

Boundary: retry giữ cùng request id trong localStorage; backend vẫn là source of
truth nếu localStorage bị xoá và lượt gần nhất được đồng bộ lại.
