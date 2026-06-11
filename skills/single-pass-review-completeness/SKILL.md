---
name: single-pass-review-completeness
description: "Use when: making one review round complete instead of incremental, enumerating review dimensions up front, sweeping a whole diff per dimension, declaring review coverage and uncovered dimensions, or preventing new findings on unchanged code in later review rounds."
argument-hint: "The diff or change set to review, the change intent, and any dimensions the requester wants prioritized or excluded."
user-invocable: true
---

# Single-Pass Review Completeness

Structure one review round so it is complete by construction: enumerate the dimensions first, sweep the entire diff per dimension, and declare what was and was not covered. The failure mode this prevents is incremental review — new findings appearing in later rounds on code that did not change.

## When to Use

Use when performing a review round that should be the only one, or when a review has been criticized for drip-feeding findings across rounds. Out of scope: deciding merge readiness after fixes, formatting individual findings, and re-reviewing fixes from an earlier round.

## Required Inputs

- The diff or change set.
- The change intent.
- Requester's dimension priorities or exclusions, when given.

If the diff is unavailable, emit the BLOCK template.

## Dimension Catalogue (8)

1. Correctness — logic, edge cases, off-by-one, error paths.
2. Contracts — API, schema, config, wire-format compatibility.
3. Security — input handling, authn/authz, secrets, injection surfaces.
4. Concurrency and state — shared state, ordering, idempotency, lifecycle.
5. Performance — complexity, hot paths, resource usage, N+1 patterns.
6. Tests — coverage of changed behavior, test quality, missing negative paths.
7. Maintainability — naming, structure, duplication, comprehensibility.
8. Operability — logging, metrics, failure visibility, rollout/rollback.

## Procedure

1. Lock the diff under review; later pushes start a new pass, never extend this one.
2. List all eight dimensions and classify each as `swept`, `skipped`, or `n/a` before reporting findings, recording the reason in the coverage table's reason column. Use `n/a` when the diff has no surface for the dimension. Skipping is allowed only for requester exclusion or for missing expertise/context.
3. Sweep dimension by dimension across the whole diff — not file by file with ad-hoc concerns. Record findings as they are found, tagged with their dimension.
4. After the sweep, do one anti-increment check: for each `swept` dimension, confirm every file in the diff was considered under it. List any file–dimension pair that was not as an explicit coverage gap, never silently.
5. Report with the declared-coverage output.

## Rules

- Never report a dimension as `swept` if any file in the diff was not considered under it.
- Findings outside the locked diff (pre-existing issues) are listed separately, not mixed into the pass findings.
- A later round on the same locked diff may only contain findings traceable to declared coverage gaps or to new information; say so explicitly when invoked for such a round.

## Output Format

```markdown
## Single-Pass Review Report

- Locked diff: <identifier / summary>
- Change intent: <one sentence>

### Coverage declaration

| Dimension | Status | Reason if not swept |
|-----------|--------|---------------------|
| <Correctness> | <swept \| skipped \| n/a> | <reason, or empty for swept> |

One row per dimension, all eight dimensions.

### Findings

- [dimension] <anchor> — <issue>

### Pre-existing issues (outside locked diff)

- <item or "None">

### Coverage gaps

- <file–dimension pairs not covered, or "None">

Verdict: COMPLETE-PASS | PARTIAL-PASS | BLOCK
```

Verdict mapping: `COMPLETE-PASS` — every dimension is `swept`, `n/a`, or skipped for requester exclusion, and Coverage gaps is `None`. `PARTIAL-PASS` — coverage gaps exist, or a dimension is skipped for missing expertise/context (any skip without requester agreement); name what a follow-up pass must cover. `BLOCK` — insufficient input. Emit exactly one value for each enum field; do not copy enum lists or angle-bracket placeholders into the report.

No-findings path: full coverage with no findings is a valid `COMPLETE-PASS`; keep the `### Findings` heading with the single line `Findings: none` under it.

### BLOCK Template (insufficient context)

```markdown
## Single-Pass Review Report

Verdict: BLOCK

- Missing input: <diff, intent, or named gap>
- Cannot evaluate: <dimensions affected>
- Smallest addition to proceed: <concrete ask>
```

## Definition of Done

All eight dimensions appear in the coverage declaration, every finding carries a dimension tag, coverage gaps are explicit, and the verdict follows the mapping.
