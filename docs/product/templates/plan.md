# <slug> — plan

Approved: pending

<!--
HOW for one task, no line cap — steps as few as the task allows (growing
past them is two tasks); Status grows freely with its evidence. A plan is
a small dependency graph: each step
names what it needs, the files it owns, the check that proves it, and the AC it
satisfies. Two fixed steps close every plan on a scoped product — Record, then
Evidence. Status lists every step from the start; "completion is a state
transition, not a sentence": a step is done when its check's output is pasted
in, not when someone says so. Delete these comments on fill.

Conventions:
- Prose in the person's language (the chat's); headings, the `Approved:`
  line, ids, checkboxes, and pasted evidence as given here — `find-plan.sh`
  and the review parse the skeleton.
- Steps are vertical slices, riskiest first. A step whose failure the final
  check would hide is why this plan exists.
- needs: the steps that must be complete first. Steps with no unmet needs and
  disjoint files may run in parallel (a subagent per step, workhorse tier —
  a step flagged risky rides the session's model — each with a brief:
  TASK · CONTEXT · READ · WRITE · ACCEPTANCE · STATUS · RETURN). The tier
  is passed as the spawn's `model` parameter — a spawn that omits it
  inherits the session's model (`WORKFLOW.md` › Model tiers). STATUS:
  the subagent ticks its own Status line with the evidence — and still
  RETURNs it. Shared files = no parallel; one lead marks `[~]` on dispatch
  and verifies lines against returns at fan-in; a missing line is not done.
- files: the only paths the step may change. A step that touched a file it did
  not name has grown — change the plan, say so.
- check: a command and its expected result (exit code, count, output), or a
  manual check precise enough to say pass/fail. "Test it" is not a check.
- Phases (optional): a plan MAY group contiguous steps under
  `### Phase <n> — <name>` headers inside Steps — only when the final diff
  would be too large for one review walk, or the build will not fit one
  session's context budget. Steps keep their global numbers; each phase
  ends product-working. Status gains one gate line per phase:
  `- [ ] G<n> — phase <n> gate`, ticked
  `- [x] G<n> — Approved — <who> — <date>` only by the owner's yes at the
  boundary; no step of phase n+1 runs while G<n> is unticked. Before the
  gate's ask, the build writes the phase landing under the gate line:
  `landing: state <commit or diff hash> · ACs met: <ids + evidence
  pointers> · growth/deviations: <notes, or none>` — a fresh session must
  be able to run phase n+1 from spec.md + plan.md alone.
- A bug plan carries a same-cause sweep between the repro and the fix, in
  the shape tk-plan's sweep section requires: one sentence of cause, both
  axes evidenced, every found site landed here or recorded as a case.
- Record before Evidence, so the evidence rerun already contains the new line.
- Approved: `pending` until the owner's yes at the gate, then `<who> — <date>`.
  tk-build refuses a pending plan; any later edit resets the line.
- The gate is reached through the Register's Walk (`WORKFLOW.md` ›
  Register › Walk): every `Q-n` default a step would proceed on and
  every decision pushed back to the owner is its own open item, asked
  before the whole-plan `Approved:` question. An answer lands on the
  item's line — `— answered: <option> — <who> — <date>` — is applied
  to the step it names, and gets one dated line under
  `## Clarifications` per round (asked ids → chosen answers, raised
  ids). Cap three rounds; unattended, no walk — lines stay `pending`.
-->

Source: .ai/<date>-<slug>/spec.md | scopes/<id>.md § … | the request + <files read>
Scope: docs/product/scopes/<id>.md | none (no product layer)
Run by: <agent / model> — <date>

## Steps
1. <riskiest slice — for a bug, the failing test; the same-cause sweep
   follows it, before the fix>
   needs: — · files: … · satisfies: AC-1
   check: `<command>` → <expected: exit 1, "1 failed">
2. <next slice>
   needs: 1 · files: … · satisfies: AC-1, AC-2
   check: `<command>` → <expected>
3. Record — apply the spec's delta (incl. exercised Q-n defaults, landed
   as what the default was, never as its Q-n id): scope rows/lines,
   PRODUCT.md rule if any, DECISIONS.md entry. A blocking
   Q-n still open → `blocked: Q-n — owner`, stop.
   needs: 2 · files: docs/product/…
   check: the delta's lines are in the files it names
4. Evidence — rerun the scope's automated list (or the project's suite);
   browser-visible lines via tk-ui-check. If a code graph is available, run its
   change-impact query on the diff and add any affected evidence line it names.
   needs: 3
   check: every line passes; output pasted below

## Clarifications
<!-- The gate's walk (Register › Walk), dated so the order of answers
is part of the record. Each round adds one line naming the ids it
asked, what was answered, the ids the re-read raised, and the steps
the answers touched. -->
- <YYYY-MM-DD> round <n> — asked: <ids> → A: … — raised: <ids> —
  affects: <steps>

## Status
<!-- Live state, one line per step: `[ ]` open · `[~] running — <who>,
since <when>` · `[x]` + the check's output pasted in. A line is written
the moment its check lands, never batched at the end. A step owns its
line as it owns its files — a parallel subagent ticks its own. Fail +
what was tried and ruled out · blocked + what it waits on, on the line. -->
- [ ] 1
- [ ] 2
- [ ] 3
- [ ] 4
