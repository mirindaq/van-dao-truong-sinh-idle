# phase-1-core-loop Scope

## Open Decisions

- Settled 2026-09-17: tiếp tục dùng seed hiện tại khi triển khai milestone kế
  theo yêu cầu owner; các giá trị vẫn là dữ liệu cân bằng có thể chỉnh.

## Flow

1. Player opens the app.
2. Frontend requests `GET /game/state`.
3. If no save exists, frontend shows the narrative New Game screen and calls
   `POST /game/new`.
4. Backend applies offline cultivation from `last_cultivation_at`.
5. Backend returns one aggregate state with player, realm, spiritual root,
   cultivation rate, next-stage estimate, resources, active pet, dao partner,
   current activity, pending offline report, breakthrough preview, server time,
   and recent logs.
6. Frontend renders the home screen with cultivation as the primary action
   surface.
7. Frontend may preview and attempt breakthrough through backend endpoints.

## Entities

- Player: one local save profile, identified by its database id.
- Realm: seeded progression data, identified by its key.
- Spiritual root: seeded root profile assigned at start.
- Game log: timestamped event visible to the player.
- Breakthrough attempt receipt: idempotent backend result keyed by request id.

## States

- Player cultivation state lives on the player record.
- Realm progression lives in realm seed data.
- Logs are append-only game records.
- Pending offline reports and breakthrough receipts live in game log metadata.

## Saved For Real

State must survive application restart and browser refresh through PostgreSQL.
No authoritative game value may live only in frontend memory.

## Resilience

| Case | Expected result |
|---|---|
| First launch with empty database | Realm and spiritual root seed data are created; `/game/state` returns a no-save response and the player is only created when the New Game screen calls `POST /game/new`. |
| Browser refresh | `/game/state` returns the same saved player with updated offline progress. |
| Long offline gap | Progress is calculated from timestamps and capped only by realm data rules. |
| Offline modal refresh | Pending report remains until acknowledged through the backend. |
| Double breakthrough submit | Same request id replays the stored result, not a second roll. |
| Missing asset | Frontend resolves to a local fallback asset key. |

## Deferred

- Item-assisted breakthrough and consumable support items ->
  `phase-2-breakthrough-items`.
- Inventory, equipment, pills, and manuals as real item records ->
  `phase-2-breakthrough-items`.
- Exploration, loot, and battle -> `phase-3-exploration-battle`.
- NPC simulation, relationships, pets, and world events ->
  `phase-4-living-world`.

## Evidence

Automated:

- `pytest` passes backend engine and service tests.
- `GET /health` returns ok.
- `GET /game/state` returns saved player state or a no-save response for the UI.
- `POST /game/new` persists the first local save and refuses a second one.
- `GET /breakthrough/preview` and `POST /breakthrough/attempt` use backend
  calculations and idempotent request ids.
- Frontend lint, typecheck, build, and Playwright pass.

Manual:

- Open the frontend on desktop and mobile and confirm New Game, root reveal,
  Động Phủ, Tu Luyện, offline return, and breakthrough result render from real
  backend state.

## Closed

Closed 2026-09-17 — Codex.
- Backend pytest: 30 passed; health trả ok; tests xác nhận no-save/New Game,
  lưu/đọc lại, offline ack, preview backend và replay receipt.
- Frontend lint/typecheck/build exit 0; Playwright 17 passed.
- agent-browser trên API PostgreSQL schema tách biệt: desktop 1440x900 và
  mobile 390x844 đã thao tác New Game, Trắc Linh Thạch, Động Phủ, Tu Luyện,
  Bế Quan Kết Thúc/nhận tu vi và kết quả đột phá (success desktop, failure mobile).
- Mobile không overflow; console/browser errors sạch ở bước kiểm tra cuối.
  Trong kiểm tra thủ công, reset fixture quá sớm sau offline ack gây tranh
  request với sync; lỗi chỉ thuộc cách chuyển fixture kiểm thử, không xảy ra
  trong flow Playwright (chờ thao tác trước hoàn tất).
