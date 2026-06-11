---
name: spec-edge-case-enumeration
description: "Use when: enumerating edge cases for a feature spec, user story, or behavior description before implementation: empty and boundary inputs, error paths, permissions, concurrency, time, locale and text, limits, and lifecycle states, deciding which belong in the spec."
argument-hint: "The feature spec, story, or behavior description to enumerate edge cases for, plus any known constraints or existing edge-case notes."
user-invocable: true
---

# Spec Edge Case Enumeration

Systematically enumerate the edge cases a feature spec must decide on before implementation, and separate the ones that need a spec decision from the ones implementation can settle locally. Edge cases discovered during implementation become ad-hoc decisions nobody reviewed.

## When to Use

Use when a feature spec, user story, or behavior description is being finalized and needs an edge-case sweep. Out of scope: writing the tests for the cases (downstream work), reviewing code for missed edge cases, rewording or grading the spec's existing wording or acceptance criteria, and deep domain-specific audits (e.g. a full Unicode-security or archive-extraction review) — this skill flags that such a surface exists and that a dedicated deep review is warranted, without performing it.

## Required Inputs

- The feature spec, story, or behavior description.
- Known constraints and any existing edge-case decisions, when supplied; existing decisions are recorded, not re-litigated.

If no description is provided, emit the BLOCK template; do not invent the feature.

## Edge Case Dimensions

Sweep the described behavior once per dimension. Mark a dimension `n/a` (with a reason) only when it does not apply to the described behavior; an applicable dimension that yields nothing is reported as swept with no plausible cases.

1. `empty-and-boundary`: empty, null, zero, one, maximum, just-over-maximum inputs and collections.
2. `error-paths`: each named operation's failure modes — what the user or caller observes, and whether partial effects persist.
3. `permissions`: each action attempted by a user lacking the permission, with role/tenant variants the system has.
4. `concurrency`: the same action twice in flight, conflicting edits, retry after timeout, double-submit.
5. `time`: timezone boundaries, DST, clock skew, expiry during the operation, records created before the feature existed.
6. `locale-and-text`: non-ASCII input, very long strings, RTL text, locale-dependent formats (decimal separators, name order); flag — do not perform — any deep text-security review the surface warrants.
7. `limits`: rate limits, quota exhaustion, payload caps, pagination ends, storage full.
8. `lifecycle`: the feature meeting entities in every state they can be in (draft, archived, soft-deleted, migrating, orphaned).

## Case Disposition

Each enumerated case gets exactly one disposition:

- `spec-decision`: the right behavior is a product choice the spec must state; carries the concrete question and the options.
- `spec-stated`: the supplied spec already decides it; append `— stated: "<quote>"` inside the table's Case cell.
- `implementation-detail`: any reasonable handling is acceptable; the spec may stay silent. Use sparingly — user-observable differences are never implementation details.
- `flag-for-deep-review`: the case opens a specialized surface (security-sensitive text handling, file parsing, payment idempotency) needing its own dedicated review; name the surface.

## Rules

- Enumerate cases for behavior in the supplied description only; adjacent features are out of scope.
- Phrase each case as a concrete scenario ("user submits the form twice before the first response arrives"), not a category name.
- Do not answer `spec-decision` questions yourself; present options with their user-visible consequences and leave the choice to the owner.
- Existing edge-case decisions supplied as input are recorded as `spec-stated`, even if you disagree; note disagreement as a one-line item under `### Remarks on supplied decisions`, not a reversal.
- Bound the sweep: prefer the 3–8 most plausible cases per dimension over exhaustive combinatorics.

## Output Format

```markdown
## Edge Case Enumeration Report

- Feature: <one sentence>

| # | Dimension | Case (concrete scenario) | Disposition |
|---|-----------|--------------------------|-------------|

### Spec decisions needed

For each, numbered as in the table:
- Question: <what the spec must decide>
- Options: <option A — consequence> / <option B — consequence> [/ further options as needed; 2–4 expected]

### Flagged for deep review

- <case #, surface, why a dedicated review is warranted>

### Remarks on supplied decisions

- <case #, one-line disagreement remark>

### Dimensions without cases

- <dimension>: n/a — <reason it does not apply>
- <dimension>: swept, no plausible cases
```

Empty sections are written with `None`. `spec-stated` and `implementation-detail` cases appear in the table only (plus, for `spec-stated`, any remark under `### Remarks on supplied decisions`). `### Dimensions without cases` lists every dimension with no table rows, in exactly one of its two line forms: `n/a — <reason>` for a dimension that does not apply, or `swept, no plausible cases` for an applicable dimension that yielded nothing.

The report has no verdict line; `Verdict: BLOCK` appears only in the insufficient-input template below.

## Error Handling (BLOCK Template)

Use this reduced template only for missing or unreadable input.

```markdown
## Edge Case Enumeration Report

Verdict: BLOCK

- Missing input: <no feature description provided / text unreadable>
- Smallest addition to proceed: <concrete ask>
```

## Example

Feature: a comment can be edited by its author within 15 minutes of posting.

Table row: `| 1 | time | the author opens the edit box at minute 14 and submits at minute 16 | spec-decision |`

Under `### Spec decisions needed`:
- Question: does the window apply at open time or at save time?
- Options: save time — edits in flight at the deadline are rejected with a message / open time — an open editor extends the window, allowing edits arbitrarily late.

## Anti-Patterns

- Category names as cases ("concurrency issues") instead of concrete scenarios.
- Answering a `spec-decision` yourself instead of presenting options with consequences.
- Marking a user-observable behavioral difference `implementation-detail`.
- Performing the deep review a `flag-for-deep-review` case warrants, instead of naming the surface.
- Exhaustive combinatorics across dimensions instead of the 3–8 most plausible cases each.
- Reopening an edge-case decision the input already settled.

## Definition of Done

All eight dimensions are represented by table cases or a line under `### Dimensions without cases` (`n/a — <reason>` or `swept, no plausible cases`), every case is a concrete scenario with exactly one disposition, every `spec-decision` carries options with consequences, and no decision was made on the owner's behalf.
