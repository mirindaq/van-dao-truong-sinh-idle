# Project Notes

Stack is fixed by `PROJECT_CONTEXT.md`: FastAPI, SQLAlchemy async, Alembic,
PostgreSQL, Next.js, TypeScript, TailwindCSS, and shadcn-style components.

Do not add multiplayer, Redis, Celery, Kafka, WebSocket, complex auth, or
microservices unless the owner asks for them.

## Workflow

Before coding tasks, read `docs/product/WORKFLOW.md` and route the task from
there. The current product truth lives in `docs/product/PRODUCT.md`, the
current milestone in `docs/product/ROADMAP.md`, and the active scope under
`docs/product/scopes/`.

## Agent skills

### Issue tracker

Issues live in GitHub Issues for `mirindaq/van-dao-truong-sinh-idle`, via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: root `GLOSSARY.md` + `docs/adr/`, alongside the existing product decisions in `docs/product/DECISIONS.md`. See `docs/agents/domain.md`.
