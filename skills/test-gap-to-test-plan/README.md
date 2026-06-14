# test-gap-to-test-plan

> Use when: converting review findings, identified test gaps, or unverified behaviors into a concrete, prioritized test plan with assertions, layer choice, ownership, and a merge-gate-ready evidence trail.

This skill is aimed at the step that comes after a review has produced findings: turning those findings into a concrete, prioritized, owned test plan that a merge gate can verify. It consumes upstream review output rather than re-judging it, and stays stack-neutral so it can work from any source that supplies findings with enough context.

It helps an assistant:

- consume findings with severity labels when available from any of three declared local vocabularies — the 4-level `CRITICAL` / `HIGH` / `MEDIUM` / `LOW` vocabulary, the 3-level `High` / `Medium` / `Low` vocabulary, or the `Critical` / `Warning` / `Suggestion` rubric — and map them to `must-have` / `should-have` / `nice-to-have` priority, preserving missing or unrecognized labels as `unmapped`
- restate each finding as one specific unverified behavior before proposing a test
- pick the smallest faithful test layer (unit, integration, or e2e) and record it on the case
- write each case against a fixed template covering finding reference, original severity label, target suite, scenario, input/setup, expected behavior, failure signal, layer, priority, owner, and status
- group cases by finding rather than by file so traceability survives deduplication
- record live-system or production-data dependencies under `Untestable risks` instead of forcing them into the plan
- return `BLOCK`, `PLAN-PARTIAL`, or `PLAN-READY` so downstream merge gates can distinguish proposed coverage from landed test evidence
- refuse to fabricate findings, severities, or owners; emit `BLOCK` when required input context is missing

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
