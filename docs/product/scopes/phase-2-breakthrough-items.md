# phase-2-breakthrough-items — Chuẩn bị vật phẩm trước đột phá

Milestone: `phase-2-breakthrough-items` trong ROADMAP.md; luật nền từ PRODUCT.md.
Outcome: Người chơi xem vật phẩm đã lưu, chọn đan hỗ trợ và thấy tác động lên
tỷ lệ đột phá do backend tính; kết quả và tiêu hao được lưu cùng nhau.
Status: Đã triển khai và kiểm chứng đợt đầu. Trạng thái milestone trong roadmap chưa đổi.
Phase 1 chưa được đóng.

## Open decisions

- **Settled 2026-09-16 (walk) — phạm vi vật phẩm:** owner chọn đợt đầu gồm
  túi đồ thật, Tụ Khí Đan hỗ trợ đột phá và Thanh Mộc Quyết dưới dạng vật phẩm
  sở hữu; trang bị là nhánh tiếp theo trong Phase 2, cần bổ sung scope trước
  khi đóng phase. Đợt đầu chưa thêm bonus công pháp.
- **Settled 2026-09-16 (walk) — tác dụng và tiêu hao đan:** owner chọn 0 hoặc 1 Tụ Khí Đan cho
  mỗi lần đột phá, cộng 10 điểm phần trăm sau modifier linh căn, trần 95% khi
  dùng đan nhưng không làm giảm tỷ lệ không dùng đan; mất đan cả khi thành công
  lẫn thất bại đã được lưu. Áp dụng cho tầng nhỏ và đại cảnh giới.
- **Settled 2026-09-16 (walk) — nguồn đan:** owner chọn chỉ có 3 viên khởi đầu; save cũ giữ số còn
  lại, không phát thêm. Hết đan vẫn đột phá được; nguồn loot thuộc Phase 3.
- **Settled 2026-09-16 (walk) — hậu quả thất bại:** owner chọn giữ Phase 1:
  mất 10% ngưỡng
  tu vi của lần đột phá, không vượt tu vi đang có; không chết, không thêm thương
  tích hoặc debuff. Các con số là dữ liệu cân bằng có thể chỉnh.

Không còn quyết định mở cho đợt đầu; nhánh trang bị cần bổ sung scope riêng.

## The flow

1. Người chơi mở save mới hoặc cũ, thấy số linh thạch và túi đồ từ backend.
   Save mới có 3 Tụ Khí Đan, 1 Thanh Mộc Quyết và 10 linh thạch như mở đầu.
2. Mở túi đồ, xem tên, loại, số lượng, mô tả và điều kiện dùng. Thanh Mộc
   Quyết là vật phẩm không tiêu hao; chưa có thao tác học thêm hoặc cộng bonus.
3. Vào Tu Luyện, mở chuẩn bị đột phá: thấy cảnh giới đích, tu vi cần, tỷ lệ
   gốc, modifier linh căn, hỗ trợ vật phẩm, tỷ lệ cuối và hậu quả thất bại.
4. Chọn không dùng đan hoặc dùng 1 viên đang sở hữu. Backend trả preview mới;
   lựa chọn và xem preview chưa tiêu hao đan. Thiếu tu vi vẫn xem được lý do.
5. Xác nhận đột phá. Backend kiểm tra trạng thái và vật phẩm hiện tại, quyết
   định kết quả bằng RNG có seed, lưu tiến độ, tiêu hao và biên nhận cùng nhau.
6. Thấy kết quả, tu vi thay đổi, vật phẩm đã dùng và số lượng còn lại. Nhật ký
   lưu lần đột phá; hết đan có thể tiếp tục tu luyện và đột phá không hỗ trợ.
7. Refresh hoặc mở lại trình duyệt: túi đồ, nhân vật và kết quả đã lưu khớp nhau.

## Entities

- **Item definition:** key ổn định, tên, loại (đan/công pháp), mô tả, asset key,
  tác dụng và điều kiện dùng; dữ liệu do game cung cấp, không do trình duyệt đặt.
  Identity: item key, không phải tên hiển thị.
- **Owned item:** chủ sở hữu, item key, số lượng nguyên không âm, đều bắt buộc.
  Identity: cặp người chơi + item key cho vật phẩm cộng dồn trong đợt này.
- **Player:** id, cảnh giới/tầng, tu vi, linh thạch và linh căn hiện có.
  Identity: id save; linh thạch vẫn là tài nguyên, không tạo bản sao trong túi.
- **Breakthrough receipt:** người chơi, mã yêu cầu, cảnh giới/tầng nguồn và đích,
  lựa chọn vật phẩm, tỷ lệ thực dùng, kết quả, tổn thất tu vi, số vật phẩm tiêu
  hao và thời điểm. Identity: người chơi + mã yêu cầu; kết quả đã lưu bất biến.

## States

- Owned item: chưa có -> có số lượng (backend cấp mở đầu/chuyển save cũ);
  có -> giảm 1 -> hết (backend lưu lần đột phá có đan). Số lượng không âm.
- Chuẩn bị: không chọn <-> chọn đan (người chơi); đóng/refresh trước gửi bỏ
  lựa chọn, không đổi kho. Đây là lựa chọn UI, không phải vật phẩm đã đặt giữ.
- Đột phá: chuẩn bị -> bị từ chối (backend: dữ liệu cũ/không đủ điều kiện),
  hoặc -> thành công/thất bại đã lưu (backend). Hai kết quả đã lưu là kết thúc;
  thử lần mới cần preview mới và mã yêu cầu mới. Gửi lại không tạo lần mới.
- Source of truth: PostgreSQL lưu trạng thái game; backend quyết định RNG,
  tỷ lệ và tiêu hao. Túi đồ sở hữu là nguồn số lượng duy nhất; số hiển thị cũ
  nếu còn cần tương thích phải được suy ra từ đó. Biên nhận nằm trong metadata
  nhật ký backend như PRODUCT.md; frontend chỉ hiển thị kết quả.

## Saved for real

- Túi đồ, tiến độ và biên nhận phải sống qua refresh, đóng/mở browser, xóa
  browser storage, restart backend và triển khai bản mới trên cùng PostgreSQL.
- Chuyển save Phase 1 giữ đúng số `qi_gathering_pills` hiện có và quyền sở hữu
  công pháp từ `manual_key`; không reset tiến độ, không cấp lại phần thưởng.
- Lặp lại khởi động/chuyển đổi không nhân đôi vật phẩm. Save không có sẵn
  không được tự sinh nhân vật hoặc phát thưởng trước thao tác New Game.
- Kết quả, trừ vật phẩm và biên nhận cùng được lưu hoặc cùng không được lưu.
  Không dùng bộ nhớ frontend làm kho chính, không sửa schema trực tiếp.

## Resilience

| Case | Decided behaviour |
|---|---|
| Preview/đổi lựa chọn/đóng modal | Không trừ hay đặt giữ vật phẩm; tỷ lệ do backend tính lại. |
| Kho hết đan | Hiển thị hết và không cho chọn; đột phá không đan vẫn hoạt động. |
| Item lạ, sai loại, số lượng sai, không sở hữu | Backend từ chối, không roll, không trừ vật phẩm. |
| Thiếu tu vi hoặc không có cảnh giới kế | Từ chối kèm lý do; không tiêu hao đan. |
| Preview cũ do tab khác thay đổi kho/cảnh giới/lựa chọn | Từ chối, yêu cầu xem preview mới; không tự bỏ đan hoặc đổi mức hỗ trợ. |
| Hai tab dùng viên cuối với mã yêu cầu khác nhau | Chỉ lần hợp lệ được lưu có thể tiêu hao; lần còn lại bị từ chối, kho không âm. |
| Gửi hai lần cùng mã và cùng lựa chọn | Trả cùng biên nhận, một lần RNG và một lần tiêu hao. |
| Dùng lại mã với lựa chọn khác | Từ chối xung đột; không sửa biên nhận hoặc tạo kết quả khác. |
| Mất mạng/refresh sau khi gửi | Khôi phục mã yêu cầu đang chờ và tra/gửi lại cùng thao tác; không tự tạo mã mới trước khi biết kết quả. |
| Lỗi lưu giữa chừng | Không có trạng thái trừ đan mà thiếu kết quả, hoặc ngược lại; thử lại an toàn. |
| Restart/deploy/chuyển save lại | Đọc đúng kho và biên nhận cũ, không phát lại 3 viên hoặc công pháp. |
| Phản hồi preview đến muộn | Bỏ phản hồi của lựa chọn cũ; khóa xác nhận khi đang tải. |
| Storage lỗi hoặc pending sai | Không gửi lần đột phá mới; giữ dữ liệu retry để xử lý. |
| Đồng bộ lỗi sau kết quả | Giữ kết quả đã xác nhận và cho đồng bộ lại. |
| Thiếu ảnh vật phẩm | Fallback local theo loại; tên, số lượng và thao tác vẫn dùng được. |

## Deferred

- Mặc/tháo trang bị, bonus công pháp và nguồn nhận trang bị -> nhánh tiếp theo
  của `phase-2-breakthrough-items`; bổ sung scope cho nhánh này trước khi đóng phase.
- Nguồn đan/trang bị từ thám hiểm, loot và chiến đấu -> `phase-3-exploration-battle`.
- Bonus từ NPC, đạo lữ, linh thú và sự kiện thế giới -> `phase-4-living-world`.
- Không thêm cửa hàng, luyện đan, vứt/bán/chuyển vật phẩm trong đợt này;
  các cơ chế chưa có milestone phải được đặt vào roadmap trước khi lập scope riêng.

## Evidence

Automated (chạy lại trong các plan triển khai):
- [x] E-1: New Game tạo đúng quà mở đầu; đọc/lặp request không nhân đôi quà.
- [x] E-2: Save Phase 1 với 0 và số đan dương chuyển đổi giữ đúng số lượng,
  công pháp và tiến độ; chạy lại chuyển đổi/khởi động không thay đổi các giá trị.
- [x] E-3: Preview có/không đan cho cả tầng nhỏ/đại cảnh giới đúng từng modifier
  và trần đã chốt; xem hoặc hủy nhiều lần không đổi số lượng.
- [x] E-4: Seed cố định tái hiện thành công/thất bại; mỗi lần có đan hợp lệ mất
  đúng 1 viên; tổn thất đúng luật; không đan không trừ vật phẩm.
- [x] E-5: Các đầu vào sai, thiếu tu vi, cảnh giới cuối và preview cũ bị từ chối;
  không roll hoặc tiêu hao đan; đổi lựa chọn yêu cầu preview tương ứng.
- [x] E-6: PostgreSQL kiểm chứng gửi trùng, mã trùng khác lựa chọn và hai request
  tranh viên cuối: biên nhận không đổi, không nhân đôi kết quả, kho không âm.
- [x] E-7: Giả lập lỗi trước commit và mất phản hồi sau commit: retry cùng mã
  chỉ có một kết quả được lưu, tiêu hao và kết quả không tách rời.
- [x] E-8: Restart app với PostgreSQL đã có dữ liệu giữ nguyên kho/biên nhận;
  state hiển thị số đan nhất quán từ nguồn sở hữu duy nhất.
- [x] E-9: Backend tests và frontend lint/typecheck/build/Playwright pass,
  gồm hồi quy New Game, offline ack và đột phá không hỗ trợ của Phase 1.

Manual, at close (UI qua tk-ui-check, desktop và mobile):
- [x] E-10: Mở túi, xem đan/công pháp, bật/tắt đan trong preview; tỷ lệ và
  số lượng khớp backend, không overflow, ảnh thật hoặc fallback local hiển thị.
- [x] E-11: Dùng save kiểm thử đủ tu vi, thử có đan/không đan và kho hết;
  kết quả, số lượng còn lại, nhật ký và lý do bị chặn khớp nhau.
- [x] E-12: Ngắt phản hồi lúc gửi rồi refresh/mở lại: khôi phục cùng kết quả,
  không trừ lần hai; đóng browser, xóa storage rồi mở lại vẫn thấy kho đã lưu.
- [x] E-13: Deploy bản mới trên cùng DB với save Phase 1 và save đã dùng đan;
  không cấp lại quà, không mất công pháp, số lượng và tiến độ được giữ đúng.

## Closed

Kiểm chứng 2026-09-17: backend pytest 30 pass; frontend lint/typecheck/build pass,
Playwright 17 pass. UI desktop/mobile/320px và diễn tập migration schema riêng đạt.
Chưa đóng Phase 1 hoặc Phase 2; nhánh trang bị vẫn cần scope riêng.
