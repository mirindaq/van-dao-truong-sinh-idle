# Roadmap

Bet: a small but persistent Phase 1 loop can prove the idle cultivation feel
before broader xianxia systems are added.

## Status

| Milestone | Scope | Status |
|---|---|---|
| phase-1-core-loop | scopes/phase-1-core-loop.md | closed 2026-09-17 |
| phase-2-breakthrough-items | scopes/phase-2-breakthrough-items.md | closed 2026-09-18 |
| phase-3-exploration-battle | scopes/phase-3-exploration-battle.md | closed 2026-09-18 |
| phase-4-living-world | scopes/phase-4-living-world.md | closed 2026-09-21 |
| phase-5-game-configuration | scopes/phase-5-game-configuration.md | closed 2026-09-21 |
| phase-6-npc-relationships | scopes/phase-6-npc-relationships.md | closed 2026-09-22 |
| phase-7-world-journeys | scopes/phase-7-world-journeys.md | closed 2026-09-22 |
| phase-8-spirit-pets | scopes/phase-8-spirit-pets.md | closed 2026-09-23 |
| phase-9-alchemy | scopes/phase-9-alchemy.md | closed 2026-09-23 |
| phase-10-partner-craft | scopes/phase-10-partner-craft.md | closed 2026-09-24 |
| phase-11-game-feel | scopes/phase-11-game-feel.md | open |

## phase-11-game-feel

Outcome: the player opens a living cave abode where cultivation visibly flows,
every system screen has a clear layout on phone and desktop, and each key
moment (breakthrough, offline return, alchemy, equipping, affinity, exploration
result) answers with a short, skippable effect.

Risk retired: a richer, animated interface can ship without changing rules,
API or saves, without breaking the 42 browser tests' roles and names, and
without harming players who turn motion off.

Not yet: sound and music, new art for every item, and new game systems stay
unplaced; Bí Cảnh stays locked until a milestone opens it.

Human decisions: settled 2026-09-24 — a separate milestone, and the `motion`
library plus light particles on top of CSS, installed only at pinned, stable
versions with no known vulnerability. Open: the layout direction for the
home screen and the list of moments that get an effect, settled in the spec.

Evidence: all 13 screens fit 320/390/768/1440px with no horizontal scroll; each
key moment shows its effect and a static equivalent with reduced motion on
(including view transitions and JS-driven motion); keyboard reaches every
action; new packages are pinned and `npm audit` reports 0 vulnerabilities; lint,
typecheck, build and the full browser suite pass; a manual pass
on the real app covers an offline return and a breakthrough.

## Dropped

- Multiplayer, PvP, Redis, Celery, Kafka, WebSocket, complex auth, and
  microservices are intentionally out of scope.
- Permanent NPC death and realtime combat are intentionally out of scope.
