---
name: fix-blast-radius
description: "Use when: assessing what a proposed fix or patch could newly break before it is pushed, tracing fix impact through callers, shared state, and contracts, checking whether a fix regresses other resolved findings, or attaching a verification step to each impact risk of a fix."
argument-hint: "The fix description or diff, the finding it addresses, surrounding code context, and other recently resolved findings when available."
user-invocable: true
---

# Fix Blast Radius

Before a fix is pushed, identify what it could newly break and which previously resolved findings it could regress, and attach one verification step per risk. Fixes that break adjacent behavior are a main extender of review/fix chains.

## When to Use

Use after a fix is drafted and before it is pushed or re-reviewed. Out of scope: planning which fixes to make, judging the original finding, executing the verifications, and the final merge-gate decision.

## Required Inputs

- The fix, as a diff or precise description of what changes.
- The finding the fix addresses.
- Surrounding code context, when available.
- Other findings resolved in the same review cycle, when available (for regression cross-check).

If the fix content is unknown, emit the BLOCK template.

## Impact Trace (5 surfaces)

Trace each changed element structurally across all five surfaces. Tools that automate the trace (reference search, type checker, test runner) are optional accelerators, not requirements.

1. Callers and call sites: who consumes the changed function, endpoint, query, or template; which assumptions about its behavior change.
2. Shared state: data structures, caches, persisted records, config, or globals the change writes or whose invariants it touches.
3. Contracts: signatures, schemas, serialized formats, error types, ordering or nullability guarantees that consumers may rely on.
4. Behavioral siblings: code paths that intentionally mirrored the changed code and may now diverge (the other branch, the inverse operation, the other platform).
5. Resolved findings: each previously resolved finding in the cycle whose fix touches overlapping code or state — could this fix reopen it?

## Risk Rules

- Each identified risk gets: a surface tag, the concrete failure it would cause, likelihood (`likely`, `possible`, `unlikely`), and one verification step (existing test to run, new assertion to add, or a manual check precise enough to execute).
- A surface with no risks is reported `no impact found`, never silently omitted.
- Do not pad: report only risks the trace actually supports. An honest short list beats a speculative long one.
- If context is too thin to trace a surface, mark it `untraceable — <missing context>` rather than guessing.

## Output Format

```markdown
## Fix Blast Radius Report

- Fix under assessment: <one sentence>
- Finding addressed: <id/summary>

### Impact trace

| Surface | Result |
|---------|--------|
| Callers and call sites | <risks found | no impact found | untraceable — reason> |
| Shared state | ... |
| Contracts | ... |
| Behavioral siblings | ... |
| Resolved findings | ... |

### Risks

- [surface] <risk> — likelihood: likely|possible|unlikely — verify: <concrete step>

### Regression cross-check

- <resolved finding>: <safe | at risk — why> (or "No resolved findings supplied")

Verdict: SAFE-TO-PUSH | VERIFY-FIRST | BLOCK
```

Verdict mapping: `SAFE-TO-PUSH` — all five surfaces traced (none `untraceable`), no `likely` risks, every `possible` risk has a verification the author can run with the push. `VERIFY-FIRST` — at least one `likely` risk, or any surface marked `untraceable`; name the verifications or missing context to resolve before pushing. `BLOCK` — insufficient input. Emit exactly one value for each enum field; do not copy enum lists or angle-bracket placeholders into the report.

No-findings path: all surfaces `no impact found` is a valid `SAFE-TO-PUSH`; keep the full table.

### BLOCK Template (insufficient context)

```markdown
## Fix Blast Radius Report

Verdict: BLOCK

- Missing input: <fix content, finding, or context gap>
- Cannot evaluate: <surfaces affected>
- Smallest addition to proceed: <concrete ask>
```

## Definition of Done

All five surfaces appear in the trace table, every risk carries likelihood and a concrete verification, the regression cross-check covers every supplied resolved finding, and the verdict follows the mapping.
