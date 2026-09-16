# Decisions

<!--
Append-only, newest last. One entry per decision that moved a rule, a scope, or
a deferral — written by the plan step that records it, not from memory at the
end. The `Recorded in` line is what keeps this log from being the only place a
rule lives: the rule itself goes into PRODUCT.md, ROADMAP.md, or the scope, and
this entry points there.

This file holds ONE milestone's worth — the "tail" every task reads IS the
file. Closing a milestone rotates its entries to decisions/<milestone-id>.md,
so the file never grows past a milestone and history stays greppable per
milestone. Nothing operational is lost in the move: the rules themselves
already live where `Recorded in` points. History is SEARCHED, never read
whole — the fixed entry heading is the index; grep decisions/ for the word,
then read only the file the hit names. A rotation the close missed is
finished by the next session's Before-any-task tripwire, before routing.
Delete this comment once the first entry lands.

Entry shape:

## <date> — <milestone id> — <kind: feature | bug | roadmap | contract> — <title>
Decision: <one or two sentences>
Why: <the reason, in one>
Recorded in: <file and section> | none — reply only
-->

## 2026-09-16 — phase-1-core-loop — feature — Basic breakthrough in UI-1
Decision: Phase 1 includes backend-decided breakthrough preview and attempt for
minor and major realm advancement, with idempotent request ids and result
receipts stored through game log metadata.
Why: UI-1 needs a real breakthrough interaction, and the frontend must not roll
outcomes or invent consequences.
Recorded in: PRODUCT.md Source Of Truth; ROADMAP.md phase-1-core-loop;
scopes/phase-1-core-loop.md Flow, Resilience, Evidence
