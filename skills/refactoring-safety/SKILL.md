---
name: refactoring-safety
description: "Use when: planning or executing a behavior-preserving refactor: characterization coverage before touching code, small reversible steps with a green check after each, strict separation of restructuring from behavior change, and a stop-and-reclassify tripwire when behavior shifts."
argument-hint: "The code to refactor, the goal of the restructuring, existing test coverage signals, and any known consumers of the touched surface."
user-invocable: true
---

# Refactoring Safety

Plan and run refactors as behavior-preserving, step-checked, reversible work. A refactor that changes behavior is not a refactor; it is an unreviewed behavior change wearing a tidy commit message.

## When to Use

Use when restructuring existing code is planned or underway and behavior must not change: extracting modules, renaming, inverting dependencies, replacing internals behind a stable surface. Out of scope: deciding whether the new structure is the right design, behavior changes and feature work (including "while we're in there" fixes), splitting an already-written mixed diff for review, and performance optimization that intentionally changes observable timing or output.

## Required Inputs

- The code or surface to refactor and the goal of the restructuring.
- Test coverage signals for the touched surface: which behaviors are exercised by existing tests, when known.
- Known consumers of the touched surface (callers, other services, serialized data), when supplied.

If no refactoring target is provided, emit the BLOCK template; do not invent the codebase.

## Behavior Baseline

Before any step executes:

1. Define preserved behavior: the observable contract that must not change — outputs, side effects, error types and messages callers match on, serialization formats, public API shapes. Performance characteristics count only when a consumer depends on them; say which.
2. Check the safety net: for each preserved behavior, name the existing test or check that would catch a regression. Coverage claims the input does not verify are written `unknown — verify` rather than asserted. Behaviors with no net get a characterization step (a test pinning current behavior, bugs included) before restructuring touches them — or an explicit `accepted-uncovered` entry with a one-line reason and the acceptor from the input; when no acceptor was named, write `pending acceptance by <role>`.
3. Characterization tests pin what the code does, not what it should do; a bug discovered while characterizing is recorded under `### Discovered behavior questions`, not silently fixed.

## Step Rules

- Each step is one named transformation (characterize, extract, inline, rename, move, replace-internal, delete-dead-code) on one surface, leaving the build green and all checks passing.
- After every step, the relevant check suite (the suites exercising the touched surface and its consumers, named in the step's `Check after` cell) runs green before the next step starts; a red check means revert or fix the step, never "continue and stabilize later".
- A suite that is already red before step 1 is recorded under `### Blocked` and the plan does not start; pre-existing failures are not fixed in-flight.
- Each step is independently revertible; steps that cannot be reverted alone (schema or serialized-format moves) are flagged `point-of-no-return` with a one-line rollback story.
- Mechanical, tool-applied transformations (IDE rename, codemod) are separated from hand edits — different steps, so review effort can be calibrated.
- The tripwire: the moment a step requires changing a test's expected values, or any preserved behavior shifts, stop — the work is no longer a refactor. Record it under `### Tripwire events`, reclassify that change as behavior change to be done separately, and either revert the step or carve the behavior change out of the plan; if the tripwire fires on a `point-of-no-return` step, execute its stated rollback story and record the outcome.

## Rules

- Plan only over code and coverage signals in the input; coverage claims the input does not verify are written `unknown — verify`, never asserted from optimism.
- Discovered bugs, dead code, and surprising behaviors are recorded as questions for the owner, not fixed in-flight.
- Keep the refactor's blast surface explicit: each step names what it must not touch.
- When coverage is too thin to protect a step and characterization is impractical (no seam to test against), the step is blocked: it keeps its numbered table row with `Check after: blocked` and gets a matching `### Blocked` entry naming the missing seam — it is not attempted bare.

## Output Format

```markdown
## Refactoring Safety Plan

- Target: <code/surface and restructuring goal>
- Consumers considered: <list, or `none named in input`>

### Preserved behavior

| Behavior | Safety net |
|----------|------------|
| <observable behavior> | <existing test/check> \| unknown — verify \| characterization step <#> \| accepted-uncovered — <reason, acceptor or `pending acceptance by <role>`> |

### Steps

| # | Transformation | Check after | Revertible | Notes |
|---|----------------|-------------|------------|-------|
| 1 | <one named transformation on one surface> | <suite/check that must be green, or `blocked`> | yes \| point-of-no-return — <rollback story> | <`mechanical` or `hand-edit`; `must not touch: <boundary>`; optional note — semicolon-separated, in that order> |

### Discovered behavior questions

- <bug or surprise found, question for the owner>

### Tripwire events

- <step #, what behavior shifted, reclassification decision>

### Blocked

- <step that cannot proceed, missing seam or coverage, who decides>
```

Empty sections are written with `None`. Emit exactly one value for each enum field; do not copy enum lists or angle-bracket placeholders into the report. The report has no verdict line; `Verdict: BLOCK` appears only in the insufficient-input template below.

## Error Handling (BLOCK Template)

Use this reduced template only for missing or unreadable input.

```markdown
## Refactoring Safety Plan

Verdict: BLOCK

- Missing input: <no refactoring target provided / text unreadable>
- Smallest addition to proceed: <concrete ask>
```

## Example

Target: extract the pricing rules out of `OrderService` into a `PricingPolicy` collaborator; behavior must not change.

Preserved behavior row:

| Behavior | Safety net |
|----------|------------|
| order total for mixed-discount carts | characterization step 1 |

Step rows:

| # | Transformation | Check after | Revertible | Notes |
|---|----------------|-------------|------------|-------|
| 1 | characterize: pin totals for the five known cart shapes | new tests green against current code | yes | hand-edit; must not touch: production code |
| 2 | extract: `PricingPolicy` with methods delegating to existing private logic | full order-service suite green | yes | hand-edit; must not touch: discount data schema |
| 3 | move: call sites to `PricingPolicy` | full suite + characterization green | yes | mechanical; must not touch: public `OrderService` API |
| 4 | delete-dead-code: unused private pricing methods | full suite + characterization green | yes | hand-edit; must not touch: public `OrderService` API |

## Anti-Patterns

- Restructuring first, "adding tests after" — the net goes up before the acrobatics.
- Fixing bugs found mid-refactor instead of recording them as questions.
- A red suite carried across steps to be "stabilized at the end".
- Updating test expectations to make a step pass — that is the tripwire, not a fix.
- One giant revert-resistant step doing extract, rename, and behavior tweak at once.
- Claiming coverage from test files that exist but do not exercise the preserved behavior.

## Definition of Done

Every preserved behavior has a safety net, an `unknown — verify` marker, a characterization step, or an explicit `accepted-uncovered` entry; every step is one named transformation with a green-check requirement (or `Check after: blocked` with a matching `### Blocked` entry) and a revertibility status; mechanical and hand edits are separated; discovered bugs sit under questions rather than fixes; and any behavior shift appears as a tripwire event with a reclassification decision.
