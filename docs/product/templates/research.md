# <slug> — research

Question: <the one question this research answers for the task>
Date: <YYYY-MM-DD> | Panel: <viewpoints, comma-separated>
Frame: from <document> | stated | assumed

<!-- Prose in the person's language (the chat's); headings, marks, and F-n /
     C-n ids as given here. Frame: `from <document>` when the caller's
     document states the target; `stated` when drafted from a bare request
     and run in the same turn — `stated — asked: <topic> → <answer> — <who>
     — <date>` if the one allowed question was asked; `assumed` when nobody
     could answer the run. Delete this comment on fill. -->

## Findings
<!-- Every finding carries a mark:
     verified — read from a live source; URL + date
     docs     — from documentation for a stated version, not confirmed live
     assumed  — model knowledge, unconfirmed; check before building on it -->
- F-1 (verified — <url>, <date>) <the fact, with the version or number>
- F-2 (assumed) <the fact>

## Viewpoints
<!-- One block per panel member, each written blind to the others. -->
### <viewpoint — e.g. customer: small shop owner>
- needs: <what would make them say the task worked>
- objects: <what harms or bothers them that nobody said out loud>
- asks: <the question the request does not answer>

## Conflicts
<!-- Disagreements between viewpoints or sources. Each is a decision for the
     spec or the owner, never averaged into a compromise here. -->
| Id  | Between | Disagreement | Falls to |
|-----|---------|--------------|----------|
| C-1 | <viewpoint A> vs <viewpoint B> | <the two readings> | spec D-n / OPEN — owner |

## Implications
<!-- What the spec should decide, each backed by ids above. -->
- <candidate decision> — per F-n, C-n

## Not found
- <question that stayed open, and where an answer might live>
