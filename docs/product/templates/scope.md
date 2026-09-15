# <Milestone id> — <outcome in six words>

<!--
File: docs/product/scopes/<id>-<two-words>.md, named in ROADMAP.md's status
table. The buildable brief for one milestone: product layer still — fields, not
columns; states, not enums — but concrete enough that two builders would build
the same thing. Budget: 150 lines. Open decisions go at the TOP so they are not
resolved by default. Any task may amend this file (a bug adds a resilience row
and an evidence line); the milestone is closed when the Closed section is
filled. Delete these comments as you fill in.
-->

Milestone from ROADMAP.md; rules from PRODUCT.md.
Outcome: <the milestone's outcome sentence>

## Open decisions
<!-- Each with who decides and the default the build uses until answered.
Each line is asked at the walk (Register › Walk) before the scope is
handed on; the answer replaces the line with `**Settled <YYYY-MM-DD>
(walk):** <what was chosen>` at the top, and the sections it named are
edited to match. -->
- **Owner:** … (default: …)
- **Settled 2026-09-01 (walk):** owner picked the guest-checkout default;
  flow step 2 and Resilience row 1 updated to match.

## The flow
<!-- One actor, one journey that proves the outcome. Numbered; what they do,
what changes, what they SEE. Minimal = removing any step breaks the evidence. -->
1.

## Entities
<!-- One block each. Field: product type (text, money, file, one of [..]),
required?, entered or derived. Then identity: what makes two records the same —
that decides what a double submit produces. -->
```
Entity
  field        type, required
```
Identity:

## States
<!-- States, allowed transitions with the actor that triggers each, initial and
terminal states, and the source of truth repeated from PRODUCT.md in one line.
A transition the contract lists as a human decision stays manual here. -->
```
Entity: a → b (actor) ; b → c (actor). Starts a. c is terminal.
Source of truth:
```

## Saved for real
<!-- What persistence must survive here: reload, reopened browser, restart,
new deploy; reads back every field written. WHERE it lives is the build's call. -->
-

## Resilience
<!-- Decide the behaviour; "handle gracefully" is not a decision. Add the cases
that can break THIS outcome. Bugs append rows here. -->
| Case | Decided behaviour |
|---|---|
| Refresh mid-flow | |
| Submit twice in quick succession | |
| Reopen later / new deploy | |

## Deferred
<!-- Each → the roadmap milestone that owns it. No milestone → back to
tk-product-roadmap; it is a roadmap gap, not a scope decision. -->
- … → V?

## Evidence
<!-- One observable check per claim the outcome makes, each with an id (E-n)
so plans, bugs, and DECISIONS entries can point at it. Binary: a concrete
action → an observable result. Two speeds: automated lines rerun with every
plan; manual lines run at close, phrased to run in one sitting ("close the
browser, clear storage, reopen" — not "come back tomorrow"). Browser-visible
lines run through tk-ui-check. -->
Automated:
- [ ] E-1: …

Manual, at close:
- [ ] E-10: …

## Closed
<!-- Filled when the milestone closes: date, who ran the list, every line's
result, anything that failed and how it was resolved. Empty = open. -->
