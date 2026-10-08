# equivalence-class-audit

> Expand one concrete finding into an evidence-backed audit of equivalent defects within a locked scope.

This read-only skill checks sibling fields, mirrored use sites, inverse operations, paths, modes, contracts, tests, documentation, and projections. It reports presence, disposition, severity, and a deterministic `BLOCK`, `CONCERNS`, or `CLEAN` verdict. It recommends follow-up without implementing fixes.

Full `standard` and `exhaustive` reports cover all 18 axes except the explicit catalogue-unavailable failure; `quick` covers target-specific axes, blockers, and high-risk concerns with an omitted-axis summary. Missing or unreadable required inputs produce a reduced report and one question, requesting only the triggering finding first when both are unavailable. Deferrals require an explicit owner/team and reason; absent optional deferral metadata preserves the `fix-now` default.

The core owns workflow, failure branches, values, report labels, and the completion checklist. References contain the detailed catalogue and a worked report.

## Files

- [`SKILL.md`](SKILL.md) — activation, workflow, decision rules, output, and completion gate.
- [`references/catalogue.md`](references/catalogue.md) — the 18 canonical axes and candidate illustrations.
- [`references/examples.md`](references/examples.md) — a complete standard report with hypothetical evidence.
