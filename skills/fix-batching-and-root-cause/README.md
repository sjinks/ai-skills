# fix-batching-and-root-cause

> Plan fixes for supplied review findings using evidenced causes and explicit dependencies.

This planning-only skill groups findings that share a demonstrated producing cause and records a concrete planned change for each actionable cluster. It does not discover or validate findings, implement changes, run verification, create issues, or approve fixes.

It distinguishes `root-cause` changes from justified `symptom-level` containment with a named follow-up. `no-fix` records only a caller-supplied decline or deferral with a reason and owner. Unknown causes or unresolved fix analysis use `cause-unknown`; known causes retain their evidence even when the fix approach is unresolved. Missing context remains explicit rather than invented.

Dependencies take precedence over fix-category preferences. Cycles, unresolved prerequisites, unavailable verification and missing decision metadata produce planning gaps; only supported independent work receives an executable order. Verification specifies proposed checks and expected observations, not successful test results. For `no-fix`, it checks decision metadata instead of claiming cause removal.

The report contains Findings, Clusters (including Planned change and Verification), Symptom-level and no-fix justifications, Fix order, Planning gaps, and a final Verdict. `BLOCK` applies only to an unusable findings list. Otherwise `BATCH-READY` requires all checklist conditions and no planning gaps; every other plan is `BATCH-PARTIAL`. Missing code context alone produces a partial plan. A fully documented all-`no-fix` plan can be ready without executable changes. Readiness applies to the plan, not completed fixes.

## Files

- [`SKILL.md`](SKILL.md) — inputs, cause tracing, fix-depth decisions, dependency ordering, report schema, readiness checklist, and blocked template.
- [`references/worked-examples.md`](references/worked-examples.md) — complete hypothetical root-cause and symptom-containment plans, with proposed checks and their evidence limits.
