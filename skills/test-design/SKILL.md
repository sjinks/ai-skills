---
name: test-design
description: >-
  USE FOR: selecting feature/module test case sets; implementing tests from
  those sets; assessing suite gaps. DO NOT USE FOR: writing or auditing one
  test, framework testing with an available dedicated workflow, flaky tests,
  or review-finding plans.
argument-hint: "Feature contract, files, and requested mode."
---

# Test Design

**WORKFLOW SKILL.** INVOKES: inspection and test execution. FOR SINGLE OPERATIONS: plan, implement, or assess.

## Scope

Plan or assess without editing; implement selected cases when requested. For framework-specific testing, use its dedicated workflow when available. Inspect the contract, instructions, interfaces, code, and nearby tests; code alone cannot define expectations.

## Workflow

1. Model inputs, outputs, side effects, errors, and state changes.
2. Select distinct normal, boundary, and failure cases by risk; name each expected result and defect caught.
3. Assert contractual results at a faithful layer. Follow repository conventions.
4. Run changed tests; diagnose failures. Remove brittle or redundant cases.

## Decision Rules

Ignore test counts and coverage targets. Keep tests deterministic and isolated; fake external boundaries. Read [selection guidance](references/test-selection.md) for oracles and async cases.

## Error Handling

If behavior is unclear, name missing decisions and design only supported cases. Mark unrun changed tests unverified. Do not weaken valid expectations.

## Output

Use each label once in order; caller-required labels replace them exactly.

`Designed cases:` Behavior, expected result, defect caught; for assessment, gaps or why none is justified.

`Design evidence:` Contract, repository evidence, assumptions, or missing input.

`Test execution:` Final line: `Ran: <command> => <passed|failed|exit N>` (integer N) or `Unverified: <reason>` for changed tests; otherwise `Not run; no tests changed.`

If blocked: `Blocked.` in the first field, missing input in the second, and `Not run; no tests changed.` in the final field. Caller-required labels replace all three.

## Checklist

- Does each case catch a distinct plausible defect through a stable observation?
- Are changed tests verified or explicitly unverified?

## Example

For insufficient funds, assert error and unchanged balances; catch premature debit.

## Definition of Done

Finish when checklist passes and changed tests are verified or unverified.
