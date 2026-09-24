# Thiết kế giao diện

Chủ dự án chọn giấy tuyên sáng, cổ phong thanh nhã ngày 2026-09-24.

## Ngôn ngữ hình ảnh
- Nền giấy ngà `#f5f2e9`, bề mặt `#fcfaf4`, chữ mực `#303c35`.
- Ngọc trầm `#294c3e` cho thao tác chính; son `#a74735` cho dấu ấn và đột phá.
- Noto Serif lưu cục bộ cho tiêu đề tiếng Việt; Segoe UI/sans-serif cho số và nội dung. Font đi kèm SIL OFL trong thư mục asset.
- Tranh thủy mặc nguyên bản `frontend/public/assets/maps/qingyun-paper.png` tạo bằng imagegen tích hợp. Không dùng artwork của game tham khảo.
- Chi tiết mảnh, ít bóng, khoảng trắng; chữ quan trọng đứng trên vùng giấy sáng, không phụ thuộc màu để truyền đạt trạng thái.

## Bố cục
- Điều hướng nhóm Tu hành / Nhân duyên / Thiên hạ; giữ đường dẫn đến mọi hệ thống hiện có.
- Động phủ ưu tiên cảnh giới, tiến độ, tốc độ tu vi, thời gian còn lại và một hành động chính; căn nguyên, đồng hành và nhật ký đặt cạnh hoặc dưới trên điện thoại.
- Thẻ, modal, trang khởi đầu, kết nối lỗi và kết quả offline cùng bảng màu sáng.
- Mobile dùng điều hướng dưới và menu Thêm. Hỗ trợ rộng 320px, bàn phím, focus rõ và giảm chuyển động.
- Luật chơi, API, dữ liệu lưu và cơ chế offline không thay đổi. Chỉ Bí Cảnh hiện chưa mở; không gắn nhãn chưa mở vào tính năng đã hoạt động.

## Nguồn nghiên cứu
Đọc ngày 2026-09-24; đây là tham khảo, không phải tuyên bố cải thiện retention.
- [Tale of Immortal](https://store.steampowered.com/app/1468810/_/): bối cảnh tu luyện/thần thoại.
- [Amazing Cultivation Simulator](https://store.steampowered.com/app/955900/Amazing_Cultivation_Simulator/): tham khảo game có nhiều hệ thống tu hành.
- [Melvor Idle — hướng dẫn giao diện](https://wiki.melvoridle.com/index.php?title=Beginners_Guide): điều hướng, trạng thái và kỹ năng theo ngữ cảnh.
- [W3C về tương phản](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) và [vùng tương tác](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html): căn cứ kiểm tra khả năng đọc và thao tác.

## Chuyển động (phase-11, 2026-09-25)
- Nền: CSS và `<ViewTransition>` của React (đổi màn phải nằm trong `startTransition`). Khoảnh khắc lớn dùng `motion` (LazyMotion + `m`) và `canvas-confetti` nạp động.
- Gói ghim đúng bản đã ra ít nhất 7 ngày: `motion` 13.4.0, `canvas-confetti` 1.9.4, `@types/canvas-confetti` 1.9.0; `overrides` giữ `framer-motion` 13.4.0, `motion-dom` 13.3.0, `motion-utils` 13.3.0. Sau mỗi lần cài: `npm audit` = 0, `npm audit signatures` hợp lệ (npm ≥ 11; npm 10.2.5 báo sai về SLSA provenance v1).
- Giảm chuyển động: mặc định theo hệ điều hành, đổi được trong Cài đặt. Khi bật: không animation/transition CSS (kể cả `::backdrop`, `::view-transition-*`), không đổi màn bằng transition, `motion` chạy thời lượng 0, không hạt; số hiện giá trị cuối ngay.
- Khoảnh khắc: xuất quan (số chạy 900ms, bấm vùng báo cáo để nhảy tới cuối, hạt khi vắng ≥1 giờ), đột phá (nghi thức 1.4s, bấm hoặc Esc để bỏ qua; thành công ánh ngọc + hạt, thất bại vòng son, không hạt), luyện đan (tiến trình, "+N"), trang bị (đồ trượt vào, tổng chiến lực nhảy), thám hiểm (kết quả trượt vào), thân mật (mốc kết duyên sáng lên), chuyển màn và modal (chỉ lúc mở).
- Mỗi khoảnh khắc phát một lần theo loại + mã biên nhận (`played-moments` trong trình duyệt); reload hiện trạng thái cuối.
- Nội dung đã có sẵn khi mở một màn (vào lại, reload) hiện tĩnh; chỉ thứ đến sau khi màn đã mở mới trượt vào.
- Hạt vẽ trên canvas bên trong modal, vì modal nằm ở top layer.
- Động Phủ: tu vi chiếu tới giữa hai lần đồng bộ theo tốc độ server; phần chiếu tới dừng ở ngưỡng tầng, nhưng tu vi dư server đang giữ luôn hiện đủ; dừng khi có modal/báo cáo offline/tab ẩn; server vẫn là nguồn sự thật.
- Chip "+N" chỉ để trang trí (ẩn khỏi cây truy cập), đặt ngoài ô số.
- Vùng chạm ≥24×24px ở 320px; viền focus son 2px, lệch 2px.

## Kiểm chứng
- `npm run lint`, `npm run typecheck`, `npm run build`, `npm test` trong frontend.
- `tests/design.spec.ts`: cả 13 điểm đến ở 320/390/768/1440px, ảnh tải đủ, không lỗi JavaScript/tràn ngang; keyboard modal, reduced motion, link và sidebar thu gọn.
- `tests/motion.spec.ts`: giảm chuyển động, chuyển màn, xuất quan, đột phá, Động Phủ sống, mốc thân mật; `design.spec` thêm vùng chạm và viền focus.
- Chụp và xem trực tiếp desktop/mobile, màn Thiên Hạ, khởi đầu và modal; các bài hồi quy hiện có kiểm tra backend và save bằng schema thử riêng.

## Prompt tranh
Built-in imagegen; stylized-concept, original wide shan shui landscape on warm ivory xuan paper. Muted sage and blue-grey ink, misty layered karst mountains, small Taoist pavilion on the right, pine branches upper right, distant cranes. Left half and lower center airy paper/mist for UI. Dry-brush detail, subtle fibers, calm daylight. No text, calligraphy, seals, watermark, people, UI, borders, fantasy glow or dark background.
