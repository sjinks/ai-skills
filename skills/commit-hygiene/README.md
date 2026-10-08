# commit-hygiene

> Plan or audit an unmerged branch's commit sequence without running Git.

Recommends fixup squashing, evidence-backed dropping, splitting mixed commits, dependency ordering, and reword targets. It returns a rebase todo, per-commit actions, a resulting sequence, cautions, and author questions with a `CLEAN`, `CONCERNS`, or `BLOCK` verdict. Individual message writing, PR splitting, and code correctness review are outside its scope.

Unknown merge style uses preserved-commit rules; squash merge focuses on final content. Uncertain changes stay pending rather than being discarded. Rewrite plans require backup and publication cautions. Missing or invalid range metadata or merge topology uses the reduced `BLOCK` report; an explicitly empty range is valid. Missing change summaries or verification stays pending in the full report. Audit reports retain required safety recommendations without directing execution of the cleanup plan. Todo and Actions contain each input commit once; Resulting sequence removes drops/folds and expands splits. Net content is preserved except explicitly author-approved discards.

## Files

- [`SKILL.md`](SKILL.md) — workflow, safety rules, output contract, and completion checklist.
- [`references/examples.md`](references/examples.md) — report examples and authoritative Git references.
