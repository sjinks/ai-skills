# code-quality

> Review production-code quality or discover and verify behavior-preserving simplifications using project evidence.

Targets can be supplied code snippets, diffs, or named paths; only when no target is supplied does the skill select relevant current workspace changes. Missing required snippet context remains an explicit coverage gap.

Checks cover readability, API and module design, representations, trust boundaries, errors, resources, retries and concurrency, behavioral evidence, performance tradeoffs, and compatibility. Separate plan validation, new-code authoring, framework recipes, companion-skill orchestration, and AI fingerprints are intentionally outside this skill's scope. Comprehensive security audits, performance investigations, test-suite audits, isolated test-code reviews, and preplanned behavior-preserving refactors are excluded; performance costs and behavioral tests remain dimensions of a code-quality review.

Isolated test-code review means a primary target of test assertions, determinism, or isolation. A preplanned refactor means the caller has already selected a transformation or plan to execute; this skill instead discovers quality problems and chooses simplifications. Correctness fixes and other behavior changes remain proposals here, even when separately authorized; implementation requires a separate behavior-changing task.

Simplification records a passing starting state and checks retained edits together. Failed or unavailable required checks, or uncertain equivalence, stop new edits and roll back the agent’s edits since the last passing combined state, preserving pre-existing work and reporting recovery results.

All 13 dimensions receive an applicability screen, followed by investigation of applicable signals and risks. Findings describe concrete consequences rather than smell counts and retain stable IDs, `Open`/`Resolved` statuses, and observable resolution criteria. The report uses `Quality` labels and returns `Blocked`, `Needs attention`, or `Clean`; `Clean` applies only to the inspected scope.

## Files

- [SKILL.md](SKILL.md) — modes, scope, workflow, decision rules, checklist, severity, and output contract.
- [Contextual criteria](references/criteria.md) — review dimensions, API design, representations, module boundaries, dependencies, and state ownership.
- [Correctness, verification, and change safety](references/correctness-and-boundaries.md) — validation, failures, values, resources, retries, concurrency, assertions, performance, compatibility, and simplification recipes.
- [Worked reports](references/worked-examples.md) — retained abstractions, genuine defects, verified prose cleanup, and a behavioral proposal awaiting checks.
