# complexity-audit

> Identify avoidable complexity and propose the smallest supported simplification.

This read-only skill reviews supplied code, diffs, or paths against requirements, callers, and local conventions. Four evidence gates prevent speculative findings and protect necessary behavior, defensive checks, boundaries, and test seams. It does not apply changes or perform comprehensive correctness/security reviews.

The report uses `Complexity scope:`, `Complexity findings:`, `Complexity limitations:`, and `Complexity verdict:`. Verdict precedence is `Blocked`, then `Incomplete`, then `Findings`, then `No findings`; supported findings remain visible in an incomplete review. A completed review with no findings emits `No actionable complexity findings.`. Missing evidence is a coverage limitation, not a code defect.

## Files

- [`SKILL.md`](SKILL.md) — activation, read-only workflow, evidence gates, output contract, examples, and completion checklist.
- [`references/review-rubric.md`](references/review-rubric.md) — complexity investigation prompts and counterevidence.
