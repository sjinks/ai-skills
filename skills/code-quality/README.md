# code-quality

> Review or simplify code in any language using contextual evidence about comprehension, maintainability, and change safety.

Checks cover readability, API and module design, representations, trust boundaries, errors, resources, retries and concurrency, behavioral evidence, performance tradeoffs, and compatibility. Separate plan validation, new-code authoring, framework recipes, companion-skill orchestration, and AI fingerprints are intentionally outside this skill's scope.

All 13 dimensions receive an applicability screen, followed by investigation of applicable signals and risks. Findings describe concrete consequences rather than smell counts and retain stable IDs, `Open`/`Resolved` statuses, and observable resolution criteria. The report uses `Quality` labels and returns `Blocked`, `Needs attention`, or `Clean`; `Clean` applies only to the inspected scope.

## Files

- [SKILL.md](SKILL.md) — modes, scope, workflow, decision rules, checklist, severity, and output contract.
- [Contextual criteria](references/criteria.md) — review dimensions, API design, representations, module boundaries, dependencies, and state ownership.
- [Correctness, verification, and change safety](references/correctness-and-boundaries.md) — validation, failures, values, resources, retries, concurrency, assertions, performance, compatibility, and simplification recipes.
- [Worked reports](references/worked-examples.md) — retained abstractions, genuine defects, verified prose cleanup, and a behavioral proposal awaiting checks.
