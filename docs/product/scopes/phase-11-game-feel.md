# phase-11-game-feel — Động phủ sống, mọi màn rõ ràng

Milestone from ROADMAP.md; rules from PRODUCT.md.
Outcome: Người chơi mở một động phủ "sống", thấy tu vi đang chảy; cả 13 màn có
bố cục rõ trên điện thoại và máy tính; mỗi khoảnh khắc chính đáp lại bằng một
hiệu ứng ngắn, bỏ qua được, và có bản tĩnh khi giảm chuyển động.
Nghiên cứu: `.ai/2026-09-24-game-feel-relayout/research.md` (đọc 2026-09-24).

## Open decisions
- **Settled 2026-09-24 — vị trí:** giai đoạn riêng trong roadmap.
- **Settled 2026-09-24 — công nghệ:** CSS và `<ViewTransition>` của React làm
  nền; thêm `motion` và hiệu ứng hạt nhẹ (`canvas-confetti`) cho khoảnh khắc lớn.
- **Settled 2026-09-24 — cài đặt an toàn:** ghim đúng phiên bản đã phát hành
  ít nhất 7 ngày (`motion@13.4.0`, `canvas-confetti@1.9.4`), commit lockfile,
  `npm audit` = 0 lỗ hổng và `npm audit signatures` hợp lệ sau khi cài.
- **Settled 2026-09-24 (walk) — bố cục Động Phủ:** cảnh sống — tranh thủy mặc
  lớn làm nền, cảnh giới và thanh tu vi đang chạy ở giữa, một nút hành động
  chính, bên dưới là thẻ cơ hội (đột phá, đan, thám hiểm); bỏ chỉ số trùng topbar.
- **Settled 2026-09-24 (walk) — khoảnh khắc có hiệu ứng:** cả bốn nhóm — đột phá
  và offline; luyện đan, trang bị, thám hiểm; thân mật (NPC, đạo lữ, linh thú);
  chuyển màn và modal.
- **Settled 2026-09-24 (walk) — hiệu ứng hạt:** chỉ đột phá thành công và báo
  cáo offline có phần thưởng lớn; mọi nơi khác chỉ chuyển động nhẹ.
- **Settled 2026-09-24 (walk) — báo cáo offline:** màn xuất quan kể ngắn — thời
  gian bế quan, tu vi nhận, sự kiện — số chạy dưới 1s, một nút "Xuất quan".

## The flow
1. Người chơi mở game sau một thời gian vắng. Báo cáo offline hiện đầu tiên:
   thời gian vắng, tu vi nhận, sự kiện. Số chạy tới giá trị thật trong dưới 1s.
   Bấm "Xuất quan" để đóng (luôn xác nhận ngay); bấm vào vùng báo cáo khi số
   đang chạy thì số nhảy thẳng tới cuối.
2. Động Phủ: cảnh giới, thanh tu vi và số tu vi tăng liên tục theo tốc độ hiện
   có, giữa hai lần đồng bộ. Một nút hành động chính. Không chỉ số nào lặp lại
   topbar.
3. Khi đủ tu vi, thẻ đột phá nổi lên. Người chơi đột phá: một nghi thức dưới
   1.5s, thành công có ánh ngọc và hạt; thất bại có sắc son trầm, không hạt.
   Bấm hoặc nhấn Esc là bỏ qua. Kết quả hiện như hiện nay.
4. Người chơi chuyển giữa các màn: màn cũ mờ ra, màn mới vào (View Transitions);
   trình duyệt không hỗ trợ thì đổi ngay, không lỗi.
5. Ở từng hệ thống, hành động có phản hồi riêng: luyện đan hiện tiến trình rồi
   viên đan mới vào túi; mặc/tháo đồ thì ô trang bị đổi có chuyển tiếp; thân
   mật tăng thì mốc thân mật sáng lên; thám hiểm xong thì kết quả trượt vào.
6. Người chơi bật "Giảm chuyển động": mọi bước trên đổi trạng thái tức thì,
   không số chạy, không hạt, không chuyển màn; thông tin vẫn đủ.
7. Trên điện thoại 390px và 320px: mọi màn đọc được không cuộn ngang; nút chạm
   tối thiểu 24×24px; thanh dưới và menu "Thêm" vẫn đến được cả 13 màn.

## Entities
- **Khoảnh khắc:** một sự kiện giao diện sinh từ kết quả API đã có (đột phá,
  offline, luyện đan, trang bị, thân mật, thám hiểm, chuyển màn, modal). Không
  có dữ liệu mới lưu ở server. Identity: loại + biên nhận/mã yêu cầu của kết
  quả — cùng biên nhận thì không phát hiệu ứng lần hai.
- **Tùy chọn giảm chuyển động:** bật/tắt, mặc định theo `prefers-reduced-motion`
  của hệ điều hành; người chơi đổi được trong Cài đặt. Lưu trong trình duyệt
  như hiện nay.
- **Số hiển thị đang chạy:** giá trị suy ra từ số liệu server + tốc độ ×
  thời gian trôi; không bao giờ vượt giá trị server trả ở lần đồng bộ kế.

## States
```
Khoảnh khắc: chờ → đang phát (giao diện) ; đang phát → xong (hết giờ, bấm, Esc).
Bắt đầu ở chờ. Xong là kết thúc. Giảm chuyển động: chờ → xong ngay.
Nguồn sự thật: server (PostgreSQL) cho mọi số liệu và kết quả; hiệu ứng chỉ là
cách trình bày kết quả đã được server xác nhận.
```

## Saved for real
- Không có gì mới lưu ở server. Luật, API, save và cơ chế offline không đổi.
- Tùy chọn giảm chuyển động sống qua reload và mở lại trình duyệt.
- Reload giữa lúc hiệu ứng đang phát: kết quả đã chốt vẫn hiện đúng, không phát
  lại hiệu ứng của biên nhận cũ.

## Resilience
| Case | Decided behaviour |
|---|---|
| Refresh giữa nghi thức đột phá | Mở lại thấy kết quả đã chốt ở trạng thái tĩnh; không phát lại |
| Bấm hành động hai lần khi hiệu ứng đang phát | Lần hai bị chặn như hiện nay; hiệu ứng không làm chậm hay che nút khóa |
| Số đang chạy lệch server khi đồng bộ | Nhảy mềm về giá trị server, không bao giờ giảm quá giá trị đã hiện rồi tăng lại giật |
| Trình duyệt không hỗ trợ View Transitions | Đổi màn tức thì, không lỗi console |
| Máy yếu / tab ẩn | Tab ẩn thì dừng số chạy và hạt; hiện lại thì nhảy tới giá trị đúng |
| Giảm chuyển động bật | Không `motion`, không hạt, không `::view-transition`; trạng thái cuối hiện ngay |
| Gói hạt không tải được | Bỏ qua hạt, phần còn lại của nghi thức vẫn chạy |
| Đổi cỡ màn hình qua mốc điện thoại | Bố cục đổi ngay, không trượt; chuyển động thanh bên chỉ chạy ngay sau khi bấm thu gọn |
| Server giữ tu vi dư quá ngưỡng tầng | Động Phủ hiện đúng số server; chỉ phần chiếu tới bị chặn ở ngưỡng |
| Vào lại một màn hoặc reload | Nội dung có sẵn hiện tĩnh, không trượt vào lần nữa |
| Modal đóng | Đóng tức thì (chỉ chuyển động lúc mở) để không có hai hộp thoại cùng lúc |
| 42 bài test hiện có | Giữ role/name của nút và heading; đổi cái nào thì sửa test trong cùng thay đổi và ghi lý do |

## Deferred
- Âm thanh và nhạc nền → chưa đặt (roadmap: phase-11 Not yet).
- Tranh mới cho từng vật phẩm → chưa đặt; giai đoạn này chỉ thay icon nền tối
  bằng bản hợp giấy sáng.
- Mở Bí Cảnh → chưa đặt; giữ trang khóa.

## Evidence
Automated:
- [ ] E-1: Cả 13 màn ở 320/390/768/1440px: không cuộn ngang, ảnh tải đủ, không lỗi JS.
- [ ] E-2: Đột phá thành công và thất bại: nghi thức hiện rồi kết quả đúng; Esc bỏ qua; kết quả giống trước.
- [ ] E-3: Báo cáo offline: số cuối bằng số server; bấm vùng báo cáo khi đang chạy thì nhảy tới cuối; một nút "Xuất quan".
- [ ] E-4: Giảm chuyển động bật: không phần tử `motion` đang chạy, không canvas hạt, không `::view-transition`; trạng thái cuối hiện ngay.
- [ ] E-5: Reload sau một kết quả đã chốt không phát lại hiệu ứng của biên nhận đó.
- [ ] E-6: Bàn phím đến được mọi nút hành động và đóng mọi modal; focus nhìn thấy trên nền giấy (≥2px, ≥3:1).
- [ ] E-9: Mọi nút/link/input hiển thị ≥24×24px ở 320px trên cả 13 màn; mốc thân mật sáng khi đạt 8.
- [ ] E-7: `npm audit` = 0 lỗ hổng; `motion` và `canvas-confetti` ghim đúng bản; lockfile đã commit.
- [ ] E-8: lint, typecheck, build và toàn bộ bộ test trình duyệt qua.

Manual, at close:
- [ ] E-10: Trên app thật: vắng vài phút, mở lại, xem báo cáo offline, đột phá một lần, bật giảm chuyển động và lặp lại.
- [ ] E-11: Điện thoại 390px: đi hết 13 màn bằng thanh dưới và menu "Thêm", mỗi màn một hành động chính có phản hồi.

## Closed
