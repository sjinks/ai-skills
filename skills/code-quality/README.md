# code-quality

> Assess production-code quality and, when requested, apply verified behavior-preserving findings using project evidence.

Targets can be supplied code snippets, diffs, or named paths; only when no target is supplied does the skill select relevant current workspace changes. Missing required snippet context remains an explicit coverage gap.

Checks cover readability, API and module design, representations, trust boundaries, errors, resources, retries and concurrency, behavioral evidence, performance tradeoffs, and compatibility. Separate plan validation, new-code authoring, framework recipes, companion-skill orchestration, and AI fingerprints are intentionally outside this skill's scope. Comprehensive security audits, performance investigations, test-suite audits, isolated test-code reviews, and standalone refactoring or simplification requests are excluded; performance costs and behavioral tests remain dimensions of a code-quality review.

Isolated test-code review means a primary target of test assertions, determinism, or isolation. Standalone refactoring or simplification means the requested deliverable is restructured or simplified code, including open-ended goals and preselected transformations. Edits here require a requested code-quality assessment and application of its supported findings; a mixed request must limit edits to those findings. Correctness fixes and other behavior changes remain proposals here, even when separately authorized; implementation requires a separate behavior-changing task.

Simplification records a passing starting state and checks retained edits together. Failed or unavailable required checks, or uncertain equivalence, stop new edits and roll back the agent’s edits since the last passing combined state, preserving pre-existing work and reporting recovery results.

Applicability and reference loading consider the target and relevant inspected context, including callers and behavioral tests. Required but unavailable context is a coverage gap; context inspection does not expand edit scope.

All 13 dimensions receive an applicability screen, followed by investigation of applicable signals and risks. Findings describe concrete consequences rather than smell counts and retain stable IDs, `Open`/`Resolved` statuses, and observable resolution criteria. The report uses `Quality` labels and returns `Blocked`, `Needs attention`, or `Clean`; `Clean` applies only to the inspected scope.

## Files

- [SKILL.md](SKILL.md) — modes, scope, workflow, decision rules, checklist, severity, and output contract.
- [Contextual criteria](references/criteria.md) — review dimensions, API design, representations, module boundaries, dependencies, and state ownership.
- [Correctness, verification, and change safety](references/correctness-and-boundaries.md) — validation, failures, values, resources, retries, concurrency, assertions, performance, compatibility, and simplification recipes.
- [Worked reports](references/worked-examples.md) — retained abstractions, genuine defects, verified prose cleanup, and a behavioral proposal awaiting checks.
