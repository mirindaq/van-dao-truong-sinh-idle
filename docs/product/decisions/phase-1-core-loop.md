## phase-1-core-loop

Outcome: the player can open the game, create or load a persisted cultivator,
receive offline cultivation progress, inspect realm/root state, and attempt a
backend-decided basic breakthrough.

Risk retired: the core idle model, persistence boundary, and backend/frontend
split are proven before adding wider systems.

Not yet: item-assisted breakthrough, inventory, equipment, alchemy, exploration,
battle, NPC simulation, pets, dao partners, and complex world events land in
later milestones.

Human decisions: exact balancing numbers remain adjustable seed data.

Evidence: backend tests prove deterministic idle progress and idempotent
breakthrough; `/game/state`, `/game/new`, and `/breakthrough/*` support UI-1;
frontend renders responsive home/cultivation screens without putting
authoritative game logic in the browser.

## 2026-09-16 — phase-1-core-loop — feature — Basic breakthrough in UI-1
Decision: Phase 1 includes backend-decided breakthrough preview and attempt for
minor and major realm advancement, with idempotent request ids and result
receipts stored through game log metadata.
Why: UI-1 needs a real breakthrough interaction, and the frontend must not roll
outcomes or invent consequences.
Recorded in: PRODUCT.md Source Of Truth; ROADMAP.md phase-1-core-loop;
scopes/phase-1-core-loop.md Flow, Resilience, Evidence

