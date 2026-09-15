# Review checkpoints

<!--
Empty by default — most projects need nothing beyond `tk-review`'s fixed walk
(AC, boundary, decisions landed). Add a line per gate THIS project always
wants checked, on top of the spec: a security pass on anything touching auth,
a rollback note on a schema migration, no PII in a log line. `tk-review` walks
each one the same way it walks an AC — named, evidenced, pass or fail — and
folds it into the verdict.

This is the shipped default and stays empty. Delete this comment once the
list is real, or leave the list empty — both are fine.

Entry shape:

- <what to check> — <what "pass" looks like>
-->
