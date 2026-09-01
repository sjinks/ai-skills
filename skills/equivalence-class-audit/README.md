# equivalence-class-audit

> Use when: a concrete defect, incident, review finding, PR review comment, test failure, or bug report suggests a class of equivalent defects across sibling fields, mirror use sites, inverse operations, bounds, contracts, authorization surfaces, paths, modes, tests, docs, or source-of-truth projections.

This skill is aimed at situations where a concrete defect, incident, review finding, test failure, or bug report suggests a wider class of equivalent defects that need to be audited in one bounded pass.

For the expanded catalogue, output contract, anti-patterns, and worked example, see [WORKFLOW.md](WORKFLOW.md).

It helps an assistant:

- lock the audit scope before expanding from the triggering finding
- enumerate candidate equivalents across bounds, sibling fields, mirror use sites, inverse operations, paths, modes, contracts, authorization surfaces, tests, docs, and source-of-truth projections
- record evidence-based `present`, `absent`, `n/a`, and `blocked` presence verdicts without guessing
- assign explicit dispositions for present defects: `fix-now` by default, `defer-with-owner` for explicit deferrals with ownership and reason, or `blocked` when a required deferral lacks that metadata
- support local output depth (`quick`, `standard`, or `exhaustive`), while `quick` still reports missing context, blockers, high-risk concerns, and target-specific findings
- return one structured audit report with an explicit `Output depth:` marker; when both required inputs are available, every catalogue axis is represented in `standard` and `exhaustive` modes and target-specific axes in `quick` mode, plus fix-now defects, deferred follow-ups, out-of-scope candidates, blocking questions, and test/doc implications

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- [`WORKFLOW.md`](WORKFLOW.md) — supporting reference.
