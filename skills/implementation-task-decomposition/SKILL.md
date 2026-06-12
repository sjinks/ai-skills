---
name: implementation-task-decomposition
description: "Use when: decomposing an approved spec, design, or feature into an ordered sequence of small implementation steps before coding starts: per-step scope, verification check, and do-not-touch boundary, with explicit dependencies and no step too large to verify in one sitting."
argument-hint: "The spec or design to decompose, the codebase areas it touches, and any ordering constraints or deadlines."
user-invocable: true
---

# Implementation Task Decomposition

Turn an approved spec or design into an ordered sequence of small, independently verifiable implementation steps before the first line is written. Work planned as one big step gets verified as one big step — usually in review, by someone else, expensively.

## When to Use

Use after a spec or design is approved and before implementation starts, when the work needs to become a step sequence. Out of scope: writing the spec or design being decomposed, deciding whether an already-written diff should be split for review, performing the implementation itself, sprint-level estimation or assignment across people, safety-planning a behavior-preserving restructure of existing code (characterization coverage, revertibility discipline) — such a restructure appears here only as a step whose internal safety plan is owned elsewhere, and phase-planning a schema or data migration (expand/contract sequencing, backfill, cutover), which needs migration-specific rollback and verification phases rather than a generic step plan.

## Required Inputs

- The approved spec or design, or enough of it to name the behaviors being built. A partially approved spec is decomposed for its approved parts; draft parts go under `### Blocked on`.
- The codebase areas it touches, when known (modules, services, directories).
- Ordering constraints when supplied: migrations that must land first, feature flags, freeze windows. Contradictory supplied constraints go under `### Blocked on` with both constraints quoted.
- Who answers blocked questions, when known.

If no spec or design is provided, emit the BLOCK template; do not invent the work.

## Step Contract

Every step carries all five fields. Fields 1, 2, 4, and 5 fill the table columns `Step`, `Verify by`, `Depends on`, and `Risk`; field 3 lives on the step's `Step details` line.

1. Step: what this step builds or changes, as one capability, seam, or single mechanical transformation — not "part 1 of N".
2. Verify by: the concrete check that proves the step works (named test, command, observable behavior; for mechanical steps, build and full suite green is the default). A step with no check is not a step; merge it into one that has one.
3. Must not touch: what this step leaves alone, named concretely (other modules, public contracts, the data schema) — the boundary that keeps the step reviewable.
4. Depends on: prior step numbers, or `none`. No cycles.
5. Risk: `low`, or the one-line reason this step is the risky one (schema change, shared contract, concurrency).

## Sizing Rules

- A step is small enough when its verification can run in one sitting and a reviewer could hold the whole step in their head; when in doubt, split.
- Split along seams, in preference order: contract/interface first, implementation behind it second, call-site adoption third; mechanical changes (renames, codegen, lockfiles) get their own steps.
- Never mix behavior-preserving restructuring and behavior change in one step.
- A step whose scope cannot be stated without "and" is two steps.
- The first step that can produce an observable end-to-end result (even behind a flag) is marked `walking-skeleton`; prefer ordering it early.

## Rules

- Decompose only what the supplied spec or design contains; mark steps you inferred (plumbing the spec implies but does not name) with `(inferred)`.
- Sequencing the steps is this skill's job; choosing between competing designs is not — a decomposition that needs a design decision first lists it under `### Blocked on` and stops the affected steps there.
- Parallel-capable steps share the same `Depends on` value; do not add any other parallelism annotation.
- Spec material too vague to decompose ("handle errors properly") goes under `### Blocked on` with the concrete question, not into a vague step.
- Do not pad with process steps ("write tests", "review") — verification lives inside each step's `Verify by`, not as separate steps.

## Output Format

```markdown
## Implementation Step Plan

- Work item: <one sentence>
- Constraints considered: <ordering constraints, or `none supplied`>

| # | Step | Verify by | Depends on | Risk |
|---|------|-----------|------------|------|
| 1 | <scope, one capability> | <concrete check> | none | low \| <one-line reason> |

### Step details

- Step <#>: Must not touch: <concrete boundary>. <`walking-skeleton` / `(inferred)` markers and any notes>

### Blocked on

- <question or missing decision, which steps it blocks, who answers>
```

Empty sections are written with `None`. One table row per step. Every step gets a `Step details` line carrying at least its `Must not touch` boundary. Emit exactly one value for each enum field; do not copy enum lists or angle-bracket placeholders into the report. The report has no verdict line; `Verdict: BLOCK` appears only in the insufficient-input template below.

## Error Handling (BLOCK Template)

Use this reduced template only for missing or unreadable input.

```markdown
## Implementation Step Plan

Verdict: BLOCK

- Missing input: <no spec or design provided / text unreadable>
- Smallest addition to proceed: <concrete ask>
```

## Example

Spec: team admins can invite members by email; invites expire after 7 days; an existing member's address is rejected.

- Work item: email invitations for team admins with 7-day expiry
- Constraints considered: none supplied

| # | Step | Verify by | Depends on | Risk |
|---|------|-----------|------------|------|
| 1 | invites table migration + Invite model, no endpoints | migration applies and rolls back cleanly on a copy of staging schema | none | schema change |
| 2 | POST /invites endpoint behind `invites` flag, happy path only | integration test: admin request creates row, returns 201 | 1 | low |
| 3 | rejection paths: non-admin, existing member, invalid email | integration tests for 403, 409, 422 | 2 | low |

### Step details

- Step 1: Must not touch: existing members table, auth middleware.
- Step 2: Must not touch: email sending (stubbed), expiry logic. `walking-skeleton`
- Step 3: Must not touch: invite acceptance flow.

Under `### Blocked on`: None

## Anti-Patterns

- "Part 1 of 3" steps sliced by size instead of by capability or seam.
- Steps with no verification check, or one shared "test everything" step at the end.
- Refactoring and behavior change fused in one step.
- A dependency chain that is really one big step wearing numbers.
- Inventing scope the spec does not contain instead of marking inferred plumbing or blocking on the gap.

## Definition of Done

Every step carries all five contract fields, no step mixes restructuring with behavior change, dependencies are acyclic, a `walking-skeleton` step is marked when one exists, inferred steps are marked `(inferred)`, and everything undecidable from the input sits under `### Blocked on` rather than inside a vague step.
