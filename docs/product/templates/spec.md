# <slug> — spec

Approved: pending

<!--
WHAT and WHY for one task, as short as its decisions allow — growing past
them means it is two tasks. A contract three readers check the same
way: the agent builds to it, a test asserts it, a human reviews the diff
against it. No steps, no code, no implementation hints ("use a map", "add a
column") — those are the plan's and the build's. Every item carries an id so
the plan, the evidence, and the review can point at it. Delete these comments
on fill.

Conventions (the same in every spec, so review is a lookup, not a reading):
- Prose in the person's language (the chat's); headings, the `Approved:`
  line, ids, and checkboxes as given here — tools parse the skeleton.
- Ids: AC-n acceptance criteria · D-n decisions · Q-n open questions.
- Every AC is binary — pass or fail from a concrete input and an observable
  result — and names its oracle: the command or observation that proves it.
  At least one AC is a failure or edge case.
- No quality adjectives in a result clause: "returns an appropriate error"
  is binary-shaped and unverifiable — INVALID. Write the concrete value
  instead: "returns 422 and the body names the rejected field".
- Scope is default-deny: anything not listed under Write paths or Read-only
  is out of bounds; a build that needs another path stops and amends this
  spec first.
- Conflicts inside the spec halt the build: an AC that would touch a
  read-only path, or two items that contradict → stop and raise a new Q-n.
  No part of the spec outranks another silently.
- Authority: if this spec and a later prompt disagree, the spec wins until
  the spec is changed. A gap found mid-build lands as a Clarifications
  line, which edits the sections it names, then the build continues.
- Approved: `pending` until the owner's yes at the gate, then
  `<who> — <date> — sha256:<12 hex>` — the first 12 hex of sha256 over
  this file with this line set back to `Approved: pending`. Recomputing it
  is how a later session detects a post-approval edit. Any edit resets the
  line to `pending`; the re-gate presents only the affected ids, and the
  yes re-stamps the whole file. tk-plan consumes this spec only approved.
- The gate is walked, not asked in one shot: every `Q-n` and every `D-n`
  marked `→ docs/product` is an open item, asked as its own question
  before the whole-document `Approved:` question. An answered item gets
  `— answered: <option> — <who> — <date>` appended to its own line, and
  one dated line lands in `## Clarifications` per round naming the ids
  asked and the ids raised.
- Regeneration test before hand-off: could another agent build the same
  thing from this file alone?
-->

## Problem
<!-- What is wrong or missing, for which actor, observed how. A request that is
a solution ("add a cache") is rewritten as the problem it solves. -->

## Context read
<!-- PRODUCT.md rules · scope sections · DECISIONS.md entries that bear on this.
Without docs/product: the code and tests read. One line each. -->
-

## Scope
<!-- Bounds the build. Write paths are the only places the diff may touch;
read-only paths are context the build may read and must not change.
Default-deny: anything not listed is out of bounds — a build that needs
another path stops and amends this spec first. Prefer files and narrow
globs over whole directories. -->
Write paths:
-
Read-only:
-

## Decisions
<!-- D-n: the choice — why — the alternative rejected. Product-level ones are
marked → docs/product and RECORDED by the plan's Record step, never here.
Choices that are the owner's (money, visibility, anything irreversible) are
not decided; they go to Open questions. -->
- D-1: … — why: … — rejected: …
- D-2: … → docs/product

## Delta to docs/product
<!-- The lines the Record step will land, written out so recording is copying. -->
- ADDED rule, PRODUCT.md › Business rules: "…"
- ADDED term, PRODUCT.md › Glossary: "<term> — <meaning>"
- MODIFIED scope, scopes/<id>.md › Resilience: "<case> → <behaviour>"
- ADDED evidence, scopes/<id>.md › Automated: "E-n …"
- DECISIONS.md: "<title>"

## Acceptance criteria
<!-- AC-n: given <concrete input / state> → <observable result> — oracle:
<the command or observation that proves it>. Binary, no quality adjectives
in the result clause. At least one failure or edge case. These become the
plan's checks and, where durable, the scope's evidence lines. -->
- [ ] AC-1: given … → … — oracle: …
- [ ] AC-2: given … (failure case) → … — oracle: …

## Out
<!-- The adjacent thing that looks like part of this task and is not. -->
-

## Clarifications
<!-- The amendment path for mid-build, out-of-band corrections, and the
gate's walk, dated so the order of answers is part of the record. Each entry
edits the sections it names; the edit resets Approved and the re-gate covers
the affected ids. A walk round adds one line naming the ids it asked and the
ids the re-read raised; a mid-build gap adds a plain Q → A line. -->
- <YYYY-MM-DD> round <n> — asked: <ids> → A: … — raised: <ids> — affects: <ids>
- <YYYY-MM-DD> Q: … → A: … — affects: <ids>

## Open questions
<!-- Q-n — owner — blocking: yes/no — default used meanwhile. A blocking
question stops the step that needs it; a non-blocking one lets the build
proceed on the default — and a default the build actually used is a
decision: the plan's Record step promotes it into the delta it implies. -->
- Q-1: … — owner — blocking: no — default: … — answered: <option> — <who> —
  <date>
