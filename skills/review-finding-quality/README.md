# review-finding-quality

> Draft, rewrite, or audit supplied code review findings in a Finding Quality Report.

This skill is aimed at draft review comments and findings lists that need to be actionable and closable in a single round before they are posted.

It helps an assistant:

- enforce a five-field contract per finding: impact severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`), anchor, observed-vs-expected problem, concrete fix direction, and an objective `Resolved when` acceptance condition
- split compound findings, separate questions from findings, and drop formatter-covered style nits as non-findings
- mark findings that cannot satisfy the contract as `needs-author-input` with the missing information named, never inventing anchors or evidence
- report each input finding exactly once as `compliant`, `rewritten`, or `needs-author-input`
- return the finding quality report with summary table, per-finding fields, questions, and dropped items, or `BLOCK` when no findings text is supplied

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
