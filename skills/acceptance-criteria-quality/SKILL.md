---
name: acceptance-criteria-quality
description: "Use when: writing, rewriting, or auditing acceptance criteria, definition-of-done lists, or user-story AC for quality: testable, observable, single, scoped, and implementation-neutral, plus a coverage check, so each criterion can be objectively verified before work starts."
argument-hint: "The draft acceptance criteria or user story to audit or rewrite, plus the feature description or spec they belong to when available."
user-invocable: true
---

# Acceptance Criteria Quality

Enforce a quality contract on acceptance criteria so each one can be objectively checked when the work is claimed done. Vague AC cause "done" disputes; missing AC cause silent scope invention by the implementer.

## When to Use

Use when drafting acceptance criteria, rewriting existing draft AC, or auditing an AC list before implementation starts. Out of scope: inventing the feature's requirements (this skill formats and audits criteria for behavior it is given), writing the tests themselves, judging whether the feature is worth building, and enumerating new edge-case scenarios beyond the supplied feature description — the coverage check only marks gaps against it.

Input modes:

- Audit/rewrite mode: draft criteria supplied. The table and Criteria section cover them.
- Drafting mode: no draft criteria, but a feature description is supplied. Emit the table header with no rows, write `None` under `### Criteria`, and emit every drafted criterion under `### Proposed additions` prefixed with `drafted`, each meeting the criterion contract with its nested `Verify by` line.
- Criteria-only mode: draft criteria supplied without a feature description. Run the per-criterion audit only; mark every coverage category `n/a (no feature description supplied)` and write `None` under Proposed additions.

## Required Inputs

At least one of the following must be supplied:

- The draft acceptance criteria, as text (absent in drafting mode).
- The feature description or spec they belong to (absent in criteria-only mode); used to spot coverage gaps and to draft additions, never to invent new requirements beyond it.

If neither is provided, emit the BLOCK template; do not fabricate criteria.

## Criterion Contract

Every criterion must satisfy all five properties:

1. Testable: an objective procedure could pass or fail it; no "works well", "is intuitive", "handles errors gracefully".
2. Observable: phrased as externally visible behavior or state, not internal implementation ("returns 422 with field errors", not "uses the validator service").
3. Single: one checkable outcome per criterion; compound criteria are split. A split keeps one numbered entry with status `rewritten`; list each resulting criterion as its own `Final:` bullet (numbered 3a, 3b, …), each with its own `Verify by` line.
4. Scoped: names its trigger or precondition when behavior is conditional ("when the file exceeds the size limit, …").
5. Implementation-neutral: constrains what, not how, unless the contract itself is the requirement (a mandated protocol, format, or API shape stays).

## Coverage Check

After auditing individual criteria, check the set against the supplied feature description for these gap categories: success path, failure/rejection path, empty or boundary input, permission or authorization outcome, and persistence or side-effect visibility. A category that does not apply is marked `n/a` with a one-line reason. Gaps become items under `### Proposed additions`, derived only from the supplied feature description — never from guessed requirements; when the description does not say what the behavior should be, the gap becomes an open question instead.

## Per-Criterion Status

- `compliant`: satisfies all five contract properties; keep verbatim.
- `rewritten`: rewritten here to satisfy the contract, preserving the original intent.
- `needs-owner-input`: cannot be made testable without a product decision; name the decision.

## Output Format

```markdown
## Acceptance Criteria Quality Report

Verdict: BLOCK | CONCERNS | CLEAN

| # | Status | Contract gaps |
|---|--------|---------------|

### Criteria

For each criterion numbered as in the table:
- Original: <verbatim>
- Final: <compliant original or rewrite; for needs-owner-input, the blocking decision>
- Verify by: <one-line objective check; omit this line for needs-owner-input>

### Proposed additions

- <category or `drafted`>: <proposed criterion derived from the feature description>
  - Verify by: <one-line objective check>

### Coverage

- success path: covered | gap | n/a (<reason>)
- failure/rejection path: covered | gap | n/a (<reason>)
- empty or boundary input: covered | gap | n/a (<reason>)
- permission or authorization outcome: covered | gap | n/a (<reason>)
- persistence or side-effect visibility: covered | gap | n/a (<reason>)

### Open questions (product decisions)

- <decision needed, who can make it>
```

The `Contract gaps` cell lists the violated contract property names (`testable`, `observable`, `single`, `scoped`, `implementation-neutral`) and contains exactly `none` for `compliant` rows.

For a split criterion, replace its single `Final:`/`Verify by:` pair with one pair per split part, each `Final:` prefixed by the part label:

```markdown
- Final (3a): <first split criterion>
- Verify by: <check for 3a>
- Final (3b): <second split criterion>
- Verify by: <check for 3b>
```

`### Proposed additions` holds coverage-gap criteria in audit/rewrite mode (prefixed with their coverage category) and all drafted criteria in drafting mode (prefixed with `drafted`).

Verdict mapping: `BLOCK` — insufficient input (reduced template below). `CONCERNS` — any criterion is not `compliant`, or any coverage category is `gap`. `CLEAN` — every criterion `compliant` and no coverage gaps; say so immediately after the verdict line and keep the report.

Empty sections are written with `None`.

## Error Handling (BLOCK Template)

Use this reduced template only when neither criteria nor a feature description is supplied, or the input is unreadable.

```markdown
## Acceptance Criteria Quality Report

Verdict: BLOCK

- Missing input: <no criteria or feature description provided / text unreadable>
- Smallest addition to proceed: <concrete ask>
```

## Example

Draft criterion 1: "Invalid files are handled gracefully."
Feature description says: files over 5 MB or outside JPEG/PNG are rejected with a message naming the allowed formats and size.

Table row: `| 1 | rewritten | testable, scoped |`

Criterion 1:
- Original: "Invalid files are handled gracefully."
- Final: "When a user uploads a file over 5 MB or outside JPEG/PNG, the upload is rejected and the UI shows a message naming the allowed formats and the 5 MB limit."
- Verify by: upload a 6 MB JPEG and a 1 MB GIF; both are rejected with the message; no photo is stored.

## Anti-Patterns

- Inventing thresholds, limits, or behaviors the feature description does not state; undecided values become `needs-owner-input` or open questions.
- Stripping a mandated contract (protocol, format, API shape) as "implementation coupling".
- Collapsing a compound criterion's rewrite back into one criterion instead of splitting it.
- Marking a coverage category `covered` because a criterion mentions the topic, when no criterion actually checks the outcome.
- Writing the tests; this skill stops at `Verify by` lines.

## Definition of Done

Every input criterion appears exactly once with a status, every `compliant` or `rewritten` criterion (including each split part) has a `Verify by` line, all five coverage categories are marked, the verdict follows the mapping, and no criterion or addition was invented beyond the supplied feature description.
