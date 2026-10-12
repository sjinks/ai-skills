---
name: refactoring-safety
description: "Use when: planning or executing a behavior-preserving refactor: characterization coverage before touching code, small reversible steps with a green check after each, strict separation of restructuring from behavior change, and a stop-and-reclassify tripwire when behavior shifts."
argument-hint: "The code to refactor, the goal of the restructuring, existing test coverage signals, and any known consumers of the touched surface."
---

# Refactoring Safety

Plan and run refactors as behavior-preserving, step-checked, reversible work. Keep behavior changes separate from restructuring.

## When to Use

Use when restructuring existing code is planned or underway and behavior must not change: extracting modules, renaming, inverting dependencies, replacing internals behind a stable surface. Out of scope: deciding whether the new structure is the right design, behavior changes and feature work (including "while we're in there" fixes), splitting an already-written mixed diff for review, and performance optimization that intentionally changes observable timing or output.

## Required Inputs

- The code or surface to refactor and the goal of the restructuring.
- Test coverage signals for the touched surface: which behaviors are exercised by existing tests, when known.
- Known consumers of the touched surface (callers, other services, serialized data), when supplied.

If no refactoring target is provided, emit the BLOCK template; do not invent the codebase.

Select `plan` when the user requests planning or analysis; do not execute transformations. If the user authorizes implementation, select `execute`. If the requested action is unclear, use `plan`.

## Behavior Baseline

Before any step executes:

1. Define preserved behavior: the observable contract that must not change — outputs, side effects, error types and messages callers match on, serialization formats, public API shapes. Performance characteristics count only when a consumer depends on them; say which.
2. Map each preserved behavior to a safety net. Distinguish user-reported coverage from inspected tests and executed checks; cite the supplied evidence, file, or check result. Use `unknown — verify` until evidence establishes that the check exercises that behavior. For uncovered behavior, schedule characterization, or record `accepted-uncovered` with a reason and explicit acceptance by a named user or accountable owner. A named role alone is not acceptance: use `pending acceptance` with the reason and required role.
3. Characterization tests pin what the code does, not what it should do; a bug discovered while characterizing is recorded under `### Discovered behavior questions`, not silently fixed.

Coverage gate: before dependent restructuring executes, each preserved behavior it touches must have a verified safety net, passing characterization checks, or explicit acceptance of the uncovered behavior. Otherwise, mark dependent rows `Check after: blocked` and add matching `### Blocked` entries naming the missing evidence or acceptance. If characterization is impractical, name the missing seam. Prerequisite inspection and characterization may proceed. Acceptance waives only the stated coverage gap; it does not waive baseline or after-step checks.

## Step Rules

- Each step is one named transformation (characterize, extract, inline, rename, move, replace-internal, delete-dead-code) on one surface. Name the relevant build and regression checks in `Check after`.
- After every executed step, run the checks exercising the touched surface and its consumers, named in `Check after`. If a check fails, revert or fix the step; do not continue until checks pass.
- In `execute` mode, run applicable existing baseline checks against unchanged code before step 1. Run newly added characterization checks against unchanged production behavior after creating them and before dependent restructuring. Record baseline and after-step commands/checks and actual outcomes under `### Check results`. If required baseline checks fail or cannot run, record the reason under `### Blocked` and do not start. If required checks cannot run after a step, stop further steps and report the unchecked change; do not claim execution complete. Do not fix pre-existing failures in-flight.
- Bind each executed check result to the checked state: a revision plus any tracked/untracked changes, or a content snapshot identifier covering the checked code, consumers, and check inputs. A revision alone is insufficient when those inputs contain uncommitted changes. Confirm that the checked inputs remain unchanged during the check; if they change, invalidate that result and rerun against a stable state. If those inputs later change, reassess affected safety nets and rerun affected checks before dependent execution or completion. Retain earlier results as historical evidence, including the original baseline; do not present them as validation of the changed state.
- Each step is independently revertible; steps that cannot be reverted alone (schema or serialized-format moves) are flagged `point-of-no-return` with a one-line rollback story.
- Before executing each step, record the pre-step state of its touched surface and identify pre-existing edits. Revert or roll back only that step's changes, preserving pre-existing and concurrent work. Do not restore whole files or repository state when that would discard unrelated changes. If overlapping edits cannot be separated safely, stop and record the blocker instead of overwriting them. These protections also apply to a `point-of-no-return` rollback story.
- Mechanical, tool-applied transformations (IDE rename, codemod) are separated from hand edits — different steps, so review effort can be calibrated.
- The tripwire: if preserved observable behavior shifts, or an expectation encoding that behavior must change, stop. Record the event under `### Tripwire events`, reclassify the behavior change as separate work, and revert the step or remove the behavior change while preserving the original contract. If the tripwire fires on a `point-of-no-return` step, execute its stated rollback story and record the outcome. If rollback fails or is unavailable, record the blocker and stop.
- If evidence shows an asserted internal structure is outside the preserved contract, its assertion may change. Record the justification and the check retaining the original behavior under `### Check results`. If the distinction is uncertain, block the step. Do not weaken observable-behavior assertions to make checks pass.

## Rules

- Use supplied evidence and authorized inspection of the target repository, including callers and tests. Do not invent consumers or coverage. If inspection is unavailable, record unknown evidence and block dependent execution.
- Under `Consumer inspection`, record searched paths or surfaces, inspection evidence, and remaining unknowns. Distinguish supplied consumers from discovered consumers in `Consumers considered`. If no consumers are identified, write `none found within <searched scope>` when inspection ran, or `unknown` when it did not. Do not infer that no consumers exist outside the searched scope. If inspection did not run, record `not inspected` and the reason under `Consumer inspection`.
- Record discovered bugs, pre-existing suspected dead code, and surprising behaviors as questions for the owner; do not fix them in-flight. Before deleting code made redundant by a planned transformation, check relevant consumers and confirm that removal preserves the observable contract. If consumer evidence is insufficient, block deletion.
- Keep the refactor's blast surface explicit: each step names what it must not touch.

## Final Diff Review

In `execute` mode, inspect the complete refactor diff against the recorded pre-refactor state, including committed, uncommitted, and newly created changes attributable to the refactor. Distinguish unrelated work using the pre-step records. Compare the changed production code, tests, and supporting files against the preserved behavior and each step's boundary. Passing checks alone do not establish behavior preservation.

Record the reviewed state, inspected paths, and contract/boundary comparison evidence under `### Final diff review`. If behavior changed, apply the Step Rules tripwire. If a boundary was violated, fix or roll back the affected step using the Step Rules protections. If the diff is unavailable, changes cannot be attributed, or contract questions remain unresolved, record blockers and do not claim execution complete. After any further refactor edit, repeat the final diff review; apply the Step Rules check-invalidation rule to affected checks.

## Output Format

```markdown
## Refactoring Safety Plan

- Target: <code/surface and restructuring goal>
- Mode: <plan or execute>
- Consumers considered: <identified consumers with supplied/discovered provenance, unknown, or none found within a searched scope>
- Consumer inspection: <searched paths/surfaces and evidence, or not inspected with reason>; remaining unknowns: <list or None>

### Preserved behavior

| Behavior | Safety net |
|----------|------------|
| <observable behavior> | <verified test/check and evidence> \| unknown — verify — <reported coverage or missing evidence> \| characterization step <#> \| accepted-uncovered — <reason, named acceptor and acceptance evidence> \| pending acceptance — <reason, required role> |

### Steps

| # | Transformation | Check after | Revertible | Notes |
|---|----------------|-------------|------------|-------|
| 1 | <one named transformation on one surface> | <required suite/check, or `blocked`> | yes \| point-of-no-return — <rollback story> | <`mechanical` or `hand-edit`; `must not touch: <boundary>`; pre-step state when executed; required checks when blocked; optional note — semicolon-separated, in that order> |

### Check results

- <baseline or step #>: <command/check>; <passed, failed, or not run with reason>; checked state: <state identifier for an executed check, or not run>; <internal-assertion justification and preserved-behavior check, when applicable>

### Final diff review

- Outcome: <passed, blocked, or not run>
- Evidence: <reviewed state, inspected paths, contract/boundary comparison, or reason review was not performed>

### Discovered behavior questions

- <bug or surprise found, question for the owner>

### Tripwire events

- <step #, what behavior shifted, reclassification decision>

### Blocked

- <step that cannot proceed, missing seam or coverage, who decides>
```

Empty sections are written with `None`; in `plan` mode, write `None` under `### Check results`, describe required checks in the step table, and use `Outcome: not run` with `Evidence: plan only` under `### Final diff review`. Use `passed` only when the Final Diff Review requirements are satisfied, `blocked` for an attempted review with unresolved issues, and `not run` when no review occurred. For executed steps, record the pre-step state in Notes after the boundary. For blocked rows, include the checks required after unblocking after any pre-step state. Omit these conditional Notes fields when their conditions do not apply. Emit exactly one value for each enum field; do not copy enum lists or angle-bracket placeholders into the report. The report has no verdict line; `Verdict: BLOCK` appears only in the insufficient-input template below.

## Error Handling (BLOCK Template)

Use this reduced template only for missing or unreadable input.

```markdown
## Refactoring Safety Plan

Verdict: BLOCK

- Missing input: <no refactoring target provided / text unreadable>
- Smallest addition to proceed: <concrete ask>
```

## Examples

Read [examples](references/examples.md) when constructing step tables or checking common mistakes. The reference contains a partial extraction plan and anti-patterns.

## Definition of Done

- Plan complete: the behavior map, step plan, and report satisfy Behavior Baseline, Step Rules, Rules, and Output Format. The plan may retain explicit blockers governed by the coverage gate; a complete plan does not authorize their execution.
- Execution complete: all planned steps have executed; the Behavior Baseline coverage gate and Step Rules validation and rollback requirements are satisfied; Final Diff Review has passed against the final state; and Output Format records the evidence. No unresolved blockers or behavior changes remain. A complete plan alone is not completed execution.
