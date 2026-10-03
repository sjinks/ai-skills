---
name: test-design
description: >-
  USE FOR: selecting feature tests; writing tests from a contract; assessing
  suite gaps. DO NOT USE FOR: single-test audits, flaky-test diagnosis, or
  review-finding test plans. Framework-independent.
argument-hint: "Feature contract, files, and requested mode."
---

# Test Design

Choose tests that catch plausible behavioral defects.

**WORKFLOW SKILL.** INVOKES: repository inspection and changed-test execution. FOR SINGLE OPERATIONS: plan, implement, or assess as requested.

## Scope

Plan or assess without editing; implement when requested. Inspect the contract, instructions, interfaces, code, and nearby tests. Code alone cannot define expected behavior.

## Workflow

1. Model inputs, outputs, side effects, errors, and state changes.
2. Select distinct normal, boundary, and failure cases by risk; name each expected result and defect caught.
3. Assert contractual results at a faithful layer. Follow repository conventions.
4. Run changed tests; diagnose failures before changing expectations. Remove brittle or redundant cases.

## Decision Rules

Case count and coverage percentage are not goals. Keep tests deterministic and isolated; fake external boundaries. Read [test selection guidance](references/test-selection.md) for assertions, expected values, and async cases.

## Error Handling

If behavior remains unclear, name the missing decision and design only supported cases. Mark unrun changed tests unverified. Do not weaken valid expectations.

## Output

Default: use labels once, in order. Caller-required labels replace them exactly.

`Test cases:` Each behavior, expected result, and defect caught; for assessment, gaps or why none is justified.

`Evidence:` Contract, repository evidence, assumptions, or missing input.

`Verification:` Final line: `Ran: <command and result>` or `Unverified: <reason>` for changed tests; otherwise `Not run; no tests changed.`

If blocked, use `Test cases: Blocked.`, name missing input under `Evidence:`, and end with `Verification: Not run; no tests changed.`

## Checklist

- Does each case catch a distinct plausible defect through a stable observation?
- Are changed tests verified or explicitly unverified?

## Example

For insufficient funds, assert the error and unchanged balances; this catches premature debit.

## Definition of Done

Stop when selected cases pass the checklist and changed tests are verified or marked unverified.
