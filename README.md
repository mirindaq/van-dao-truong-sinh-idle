# Van Dao Truong Sinh Idle

Single-player xianxia idle game scaffold.

## Stack

- Backend: Python 3.12, FastAPI, SQLAlchemy 2 async, Alembic, PostgreSQL
- Frontend: Next.js, TypeScript, TailwindCSS
- Local development: Python + Node.js directly on Windows; PostgreSQL can run
  locally or in your VMware VM

## Run Local, No Docker Desktop

Run the project with three pieces:

1. PostgreSQL
2. FastAPI backend
3. Next.js frontend

### 1. PostgreSQL

Use one of these setups.

If PostgreSQL is installed directly on Windows:

```text
host: localhost
port: 5432
user: postgres
password: 123456
database: mydb
```

If PostgreSQL runs inside VMware, use the VM IP instead of `localhost`.
Example:

```text
postgresql+asyncpg://postgres:123456@192.168.1.50:5432/mydb
```

Find the VM IP inside the VM:

```bash
ip addr
```

or:

```bash
hostname -I
```

The VM must allow connections on port `5432`. In PostgreSQL, that usually
means:

```text
postgresql.conf: listen_addresses = '*'
pg_hba.conf: allow your Windows host IP
```

### 2. Backend

Open terminal 1:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

If your PostgreSQL is in VMware, edit `backend\.env` after copying it:

```text
DATABASE_URL=postgresql+asyncpg://postgres:123456@VM_IP:5432/mydb
```

Replace `VM_IP` with the real address. Leaving the literal text `VM_IP` causes
Alembic to fail with `socket.gaierror: getaddrinfo failed`.

If Alembic reaches the VM but fails with `InvalidPasswordError`, the PostgreSQL
container probably reused an old data volume. Environment variables such as
`POSTGRES_PASSWORD=123456` are only applied when PostgreSQL initializes an empty
data directory. In the VM, reset the password and create the database:

```bash
docker exec -it postgres psql -U postgres -c "ALTER USER postgres WITH PASSWORD '123456';"
docker exec -it postgres psql -U postgres -c "CREATE DATABASE mydb;"
```

If `CREATE DATABASE mydb;` says it already exists, that is fine.

### 3. Frontend

Open terminal 2:

```powershell
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Then open:

- Frontend: http://localhost:3000
- Backend health: http://localhost:8000/health
- Game state: http://localhost:8000/game/state

The frontend proxies game API calls through `/api/*`; set `API_BASE_URL` or
`NEXT_PUBLIC_API_BASE_URL` only when the backend is not on
`http://localhost:8000`.

## Optional: Docker Compose

Docker Compose is still available if you later install Docker Desktop or run in
a Docker-capable environment:

```bash
docker compose up --build
```

## Backend checks

```bash
cd backend
pip install -e ".[dev]"
pytest
```

## Frontend checks

```bash
cd frontend
npm install
npm run lint
npm run typecheck
npm run build
npm run test
```

Playwright starts a disposable FastAPI server for browser tests and verifies
New Game, saved-state refresh, offline return, breakthrough success/failure,
mobile navigation, and connection recovery.

## Inventory upgrade and verification

Stop the backend and back up the database before upgrading an existing save.
From `backend`, run `.venv\Scripts\python.exe -m alembic upgrade head`, then
restart the backend. Revision `20260916_0004` moves the old pill count and manual
into inventory, preserving zero quantities and progression. It does not grant
new items to old saves. On an empty database, items are granted only by New Game.
Do not downgrade this migration as a substitute for restoring a database backup.

Backend `pytest -q` uses disposable PostgreSQL schemas, including real Alembic
upgrades from revision 0003, reconnects and repeated upgrades. The configured DB
user needs permission to create schemas; the player's default schema is not reset.
Playwright also creates and removes its own schema. `npm test -- tests/inventory.spec.ts`
checks item use, reordered previews, reload after a lost reply, retry conflicts,
unavailable browser storage, and inventory persistence in a new browser context.
The complete `npm test` includes the Phase 1 regressions. Build before running it.

The browser stores only unresolved breakthrough request payloads in local storage.
After a lost response, use **KIỂM TRA KẾT QUẢ** to recover the existing receipt.
The saved inventory and game progress remain in PostgreSQL.

Equipment revision `20260917_0005` adds the one-time equipment pack and saved
equipment slots. Run `.venv\Scripts\python.exe -m alembic upgrade head` before
using an existing database. Migration preserves old inventory, receipts and
progress; it does not automatically claim or equip the pack. The pack is
claimed from Túi Đồ and contains one sword, robe and amulet. Equipping changes
combat power only; cultivation and breakthrough chance are unchanged.

Exploration revision `20260918_0006` adds immediate Thanh Vân Sơn runs and
persistent battle logs. Run `alembic upgrade head` before using it. A victory
awards 10 Linh Thạch and 1 Tụ Khí Đan; the same request id is safe to retry and
does not battle or reward twice. Defeat saves its log without a reward.

Living-world revision `20260918_0007` adds saved NPC state, deterministic
10-minute simulation ticks, world news and return reports. Existing saves
initialize Tạ Vô Trần, Lạc Thanh Hàn and one wanderer on their first world read;
no events are backfilled from before initialization. A return processes at most
24 hours, and world events do not change player resources.

## Architecture

Backend follows:

```text
API route -> service -> repository -> PostgreSQL
```

Game rules live under `backend/app/game/` and should stay testable without
HTTP. Frontend resolves assets by key and uses local fallbacks under
`frontend/public/assets/`.
