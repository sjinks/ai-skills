# pre-review-self-audit

> Use when: auditing your own change before requesting review, running a pre-review or pre-PR self-check, checking diff hygiene, leftover debug code, commented-out code, unrelated changes, missing tests for changed behavior, commit atomicity, PR description accuracy, or repeated templated edits applied consistently across files before opening or updating a pull request.

This skill is aimed at the author-side moment just before requesting review, when most first-round findings (hygiene, scope creep, missing tests, description drift) are still cheap to fix.

It helps an assistant:

- audit the supplied diff against a nine-item gating checklist: diff hygiene, scope, tests, contracts, commit atomicity, description accuracy, project checks, reviewer anticipation, and repeated-pattern consistency (templated multi-file edits validated once and swept repo-wide)
- discover the project's own checks structurally from CI config, package scripts, and task runners, listing unrun checks as outstanding instead of inventing them
- classify findings as `High`, `Medium`, or `Low` by whether they would force a review round on their own
- keep the full checklist table even on the no-findings path
- return `CLEAN`, `CONCERNS`, or `BLOCK` with findings, outstanding items, and a deterministic insufficient-context template

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
