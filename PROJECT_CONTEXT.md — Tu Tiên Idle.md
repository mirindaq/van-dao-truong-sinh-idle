# TU TIÊN IDLE — PROJECT MASTER CONTEXT

## 1. Project vision

Đây là game Tu Tiên Idle single-player.

Người chơi là người thật duy nhất. Toàn bộ tu sĩ, đạo lữ, thương nhân, trưởng lão, ma tu và các nhân vật khác đều là NPC/bot được game simulation.

Mục tiêu là tạo cảm giác:

"Cho dù người chơi offline, thế giới tu tiên vẫn tiếp tục vận hành."

Game tập trung vào:

Tu luyện → tăng tu vi → đột phá → mạnh hơn → khám phá → chiến đấu → cơ duyên → công pháp/trang bị → linh thú → NPC/đạo lữ → cảnh giới cao hơn.

Game phải ưu tiên cảm giác progression lâu dài, khám phá và "cơ duyên", thay vì gameplay click liên tục.

---

# 2. Technology

Backend:

Python 3.12+
FastAPI
SQLAlchemy 2 async
Pydantic v2
Alembic

Database:

PostgreSQL

Frontend:

Next.js
TypeScript
TailwindCSS
shadcn/ui

Development:

Docker Compose

Game hiện tại là single-player local.

KHÔNG triển khai:

multiplayer
PvP người thật
Redis
Celery
Kafka
microservices
WebSocket
authentication phức tạp

Không thêm những công nghệ này nếu chưa được yêu cầu.

---

# 3. Architecture

Backend:

API Route
↓
Service
↓
Repository
↓
PostgreSQL

Game logic:

app/game/

Các engine/service quan trọng:

CultivationEngine
BreakthroughEngine
BattleEngine
LootEngine
ExplorationEngine
EventEngine
NPCSimulationEngine
PetEngine
RelationshipEngine
RandomService

Không đặt game logic trong API routes.

Các game engine quan trọng phải test độc lập với HTTP.

---

# 4. Offline-first simulation

KHÔNG chạy timer liên tục.

KHÔNG update cultivation mỗi giây.

Mọi hệ thống idle sử dụng timestamp.

Ví dụ:

player có:

cultivation_exp
last_cultivation_at

Khi load:

elapsed = now - last_cultivation_at

earned =
elapsed_seconds * calculate_cultivation_rate(player)

Áp dụng cùng nguyên tắc cho:

cultivation
alchemy
exploration
pets
NPC
dao partners
missions
world simulation

Database lưu UTC.

Frontend hiển thị local time.

---

# 5. Cultivation realms

Progression chính:

Phàm Nhân

Luyện Khí
Trúc Cơ
Kim Đan
Nguyên Anh
Hóa Thần
Luyện Hư
Hợp Thể
Đại Thừa
Độ Kiếp
Nhân Tiên

Các đại cảnh giới có 9 tầng khi phù hợp.

Realm progression phải data-driven.

Không hard-code progression rải rác trong source code.

---

# 6. Main systems

Game cuối cùng sẽ có:

Cultivation
Breakthrough
Spiritual Roots
Stats
Skills
Cultivation Manuals
Equipment
Inventory
Alchemy
Exploration
Battle
Monsters
Loot
Pets / Spirit Beasts
NPC
Relationships
Dao Partners
Random Events
World Simulation
Game Logs

Nhưng phải implement từng phase.

Không xây tất cả cùng lúc.

---

# 7. Player fantasy

Player bắt đầu là phàm nhân bình thường.

Không phải thiên tuyển chi tử ngay từ đầu.

Opening:

Người chơi sống dưới chân Thanh Vân Sơn.

Trong một lần lên núi hái thuốc, người chơi tìm thấy động phủ bị bỏ hoang.

Trong động phủ có hài cốt của một tu sĩ cổ.

Di vật còn lại:

Thanh Mộc Quyết
10 Linh Thạch
3 Tụ Khí Đan

Người chơi kiểm tra linh căn.

Sau đó chính thức bước vào:

Luyện Khí tầng 1.

---

# 8. Spiritual roots

Elements:

Kim
Mộc
Thủy
Hỏa
Thổ

Variants:

Lôi
Băng
Phong
Quang
Ám

Quality ảnh hưởng:

cultivation speed
breakthrough
elemental affinity
skill compatibility

Linh căn phải ảnh hưởng build lâu dài.

---

# 9. Breakthrough philosophy

Đột phá không chỉ là nút "level up".

Player phải chuẩn bị:

cultivation
pill
dao heart
manual
equipment
environment
partner bonuses

UI phải cho xem:

Base Chance
Modifiers
Final Chance

Thất bại KHÔNG permadeath.

Có thể:

mất cultivation
bị thương
nhận Dao Wound
temporary debuff

---

# 10. NPC simulation

NPC là một trong những hệ thống quan trọng nhất.

NPC có thể:

tu luyện
đột phá
tìm cơ duyên
nhặt vật phẩm
bị thương
thay đổi quan hệ
gặp player
chết
trở nên nổi tiếng

NPC không update realtime.

Khi cần simulate:

elapsed =
now - npc.last_simulated_at

NPCSimulationEngine xử lý khoảng thời gian đó.

World log có thể xuất hiện:

"Kiếm tu Tạ Vô Trần đã bước vào Trúc Cơ tầng 8."

"Lạc Thanh Hàn tìm được cơ duyên tại Hàn Nguyệt Cốc."

"Một tán tu đã chết tại Huyết Sắc Cốc."

"Vạn Yêu Sơn xuất hiện khí tức của Giao Long."

Mục tiêu:

thế giới phải có cảm giác sống ngay cả khi player offline.

---

# 11. Dao Partners

NPC có:

personality
spiritual root
realm
talents
affection
relationship
memories/events

Relationship:

Xa Lạ
Quen Biết
Bạn Hữu
Tri Kỷ
Đạo Lữ

Không phải NPC nào cũng có thể trở thành đạo lữ.

Relationship tăng thông qua:

events
conversation
gifts
exploration
helping NPC
shared battles

Đạo lữ có gameplay bonus nhưng cũng phải có personality/story.

---

# 12. Spirit beasts

Spirit Beast có:

species
bloodline
rarity
realm
level
skills
bond
evolution path

Ví dụ:

Thanh Xà
→ Huyền Thanh Xà
→ Giao Long
→ Thanh Long

Pet có thể:

combat
exploration
gathering
cultivation support

Không biến pet thành một equipment slot đơn thuần.

---

# 13. Exploration

Player có thể tới:

Thanh Vân Sơn
Hắc Phong Lâm
Huyết Sắc Cốc
Vạn Yêu Sơn
Hàn Nguyệt Cốc
Thiên Kiếm Bí Cảnh

Exploration tạo:

battle
loot
NPC encounter
pet encounter
random event
secret area
rare opportunity

"Cơ duyên" phải là một phần quan trọng của game.

Không phải tất cả reward đều predictable.

---

# 14. Battle

Battle là auto turn-based.

BattleEngine phải là pure game logic.

Có:

HP
Attack
Defense
Speed
Crit
Skills
Elements
Buff
Debuff

Battle phải có battle log để frontend có thể replay/show kết quả.

Không cần realtime combat server.

---

# 15. Random system

Mọi randomness phải đi qua:

RandomService

RandomService hỗ trợ seed.

Không gọi random trực tiếp rải rác trong project.

RandomService dùng cho:

battle
loot
breakthrough
NPC events
pet encounters
exploration
world events

Tests phải deterministic.

---

# 16. Database philosophy

PostgreSQL là source of truth.

Dùng relational tables cho dữ liệu có structure.

JSONB chỉ dành cho dữ liệu thực sự dynamic.

Phải có:

foreign keys
indexes
constraints
timestamps

Dùng Alembic migration.

Không sửa database schema thủ công.

---

# 17. API philosophy

Frontend không được chứa authoritative game logic.

Frontend gửi action.

Backend quyết định result.

Ví dụ frontend KHÔNG tự random breakthrough.

Frontend:

POST /breakthrough/attempt

Backend:

calculate chance
roll RNG
apply result
save DB
return result

---

# 18. Game state

Có endpoint:

GET /game/state

Đây là endpoint chính khi mở game.

Nó aggregate:

player
realm
cultivation
breakthrough availability
equipment
active pet
dao partner
current exploration
alchemy
world events
recent logs

Không bắt frontend request hàng chục endpoint để render home.

---

# 19. Visual identity

Game mang phong cách:

Chinese Xianxia
dark fantasy
ink painting
ancient scroll
mystical mountains
immortal cultivation

Không làm UI giống dashboard SaaS hiện đại.

Không dùng quá nhiều card trắng.

Palette ưu tiên:

charcoal black
ink black
dark jade
warm parchment
muted gold
moonlight silver

Accent:

jade green
gold

Background có thể sử dụng:

núi mờ
mây
mực tàu
trăng
động phủ
rừng trúc
kiếm
phù văn

UI vẫn phải dễ đọc và responsive.

---

# 20. Character art direction

Nhân vật theo phong cách:

semi-realistic xianxia fantasy illustration

Trang phục:

ancient Chinese-inspired robes
cultivator robes
swords
jade accessories
hair ornaments

Không dùng:

modern clothes
guns
sci-fi armor
cyberpunk
western medieval armor

NPC quan trọng cần portrait.

Common NPC không nhất thiết có portrait riêng.

---

# 21. Asset architecture

Frontend KHÔNG hard-code URL ảnh từ internet.

Assets phải được quản lý qua asset key.

Ví dụ:

npc:

portrait_key =
"npc/luo_thanh_han"

pet:

portrait_key =
"pets/fire_fox"

map:

background_key =
"maps/qingyun_mountain"

Frontend resolve asset key thành local asset.

Ví dụ:

/public/assets/
  characters/
  npcs/
  pets/
  monsters/
  maps/
  items/
  ui/
  effects/

Game phải chạy được kể cả khi không có internet.

---

# 22. Asset fallback

Nếu asset chưa tồn tại:

NPC:
dùng silhouette/default portrait.

Item:
dùng icon theo item category.

Monster:
dùng generic monster placeholder.

Map:
dùng generic ink landscape.

Không để missing image phá UI.

---

# 23. Important UX

Home screen phải cho người chơi biết ngay:

Tên
Cảnh giới
Tầng
Tu vi
Tu vi/phút
Thời gian dự kiến tới tầng tiếp theo
Linh thạch
Chiến lực
Linh thú
Đạo lữ
Hoạt động đang diễn ra

Primary action:

Tu Luyện / Đột Phá

Secondary:

Thám Hiểm
Luyện Đan
Nhân Vật

---

# 24. Development rules

Trước khi code feature:

1. đọc project hiện tại
2. hiểu schema hiện tại
3. không rewrite code đang hoạt động nếu không cần
4. lập implementation plan ngắn
5. implement
6. migration nếu cần
7. test
8. chạy test
9. sửa lỗi
10. báo lại files đã thay đổi

Không tự ý thêm dependency lớn.

Không tự ý đổi stack.

Không tự ý chuyển sang microservice.

Không implement multiplayer.

Không tạo feature ngoài scope chỉ vì "có thể hữu ích".

---

# 25. Current priority

Ưu tiên hiện tại:

PHASE 1

FastAPI
PostgreSQL
SQLAlchemy async
Alembic
Player
Realm
Spiritual Root
Cultivation
Offline Progress
Game State
Initial Seed
Tests

Sau khi Phase 1 chạy ổn mới tiếp tục:

Breakthrough
Inventory
Equipment

Không làm UI phức tạp trước khi core gameplay chạy.