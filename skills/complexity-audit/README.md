# complexity-audit

> Identify avoidable complexity and propose the smallest supported simplification.

This read-only skill performs dedicated audits whose primary goal is identifying avoidable complexity in supplied code, diffs, or paths against requirements, callers, and local conventions. Broader production-code quality assessments, including reviews of complexity alongside other quality dimensions, are excluded. Four evidence gates prevent speculative findings and protect necessary behavior, defensive checks, boundaries, and test seams. It does not apply changes or perform comprehensive correctness/security reviews.

The report uses `Complexity scope:`, `Complexity findings:`, `Complexity limitations:`, and `Complexity verdict:`. Verdict precedence is `Blocked`, then `Incomplete`, then `Findings`, then `No findings`; supported findings remain visible in an incomplete review. A completed review with no findings emits `No actionable complexity findings.`. Missing evidence is a coverage limitation, not a code defect. Each finding exposes all four gates: observed code in `Location:`, lack of justification and supporting preservation evidence in `Evidence:`, and the simpler alternative with its maintenance benefit in `Minimal change:`. Preservation constraints alone do not establish behavior preservation.

## Files

- [`SKILL.md`](SKILL.md) — activation, read-only workflow, evidence gates, output contract, examples, and completion checklist.
- [`references/review-rubric.md`](references/review-rubric.md) — complexity investigation prompts and counterevidence.
