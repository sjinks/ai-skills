# commit-hygiene

> Plan or audit an unmerged branch's commit sequence without running Git.

Recommends fixup squashing, evidence-backed dropping, splitting mixed commits, dependency ordering, and reword targets. It returns a rebase todo, per-commit actions, a resulting sequence, cautions, and author questions with a `CLEAN`, `CONCERNS`, or `BLOCK` verdict. Individual message writing, PR splitting, and code correctness review are outside its scope. Apply it to history-planning subtasks within PR preparation or maintenance when cleanup decisions are needed; ordinary commit creation alone does not activate it. The caller supplies Git evidence and retains execution and authorization.

Unknown merge style uses preserved-commit rules; squash merge focuses on final content. Uncertain changes stay pending rather than being discarded. Rewrite plans require backup and publication cautions. Emit a concrete backup command only when supplied evidence identifies a valid unused branch name and hexadecimal original-tip hash; quote both arguments; otherwise describe the requirement and request missing values. Moves and nonadjacent folds require evidence for crossing intervening commits without breaking dependencies or review boundaries; unresolved moves/folds stay at their original positions. Use fixup only when folded-message and authorship-metadata preservation is established; otherwise request message review through squash. Missing or invalid range metadata or merge topology uses the reduced `BLOCK` report; an explicitly empty range is valid. Missing change summaries or verification stays pending in the full report. Audit reports retain required safety recommendations without directing execution of the cleanup plan. Actions explicitly include severity. Todo and Actions contain each input commit once; Resulting sequence removes drops/folds and expands splits. Net content is preserved except explicitly author-approved discards.

## Files

- [`SKILL.md`](SKILL.md) — workflow, safety rules, output contract, and completion checklist.
- [`references/examples.md`](references/examples.md) — complete known-fixup and unresolved-crossing reports, backup/message-preservation branches, and authoritative Git references.
