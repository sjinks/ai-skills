---
name: test-design
description: >-
  USE FOR: feature/module test selection and implementation; suite-gap assessment. DO NOT USE FOR: isolated test-code quality, available dedicated
  framework workflows, flaky tests, review-finding plans.
argument-hint: "Contract, files, mode."
---

# Test Design

**WORKFLOW SKILL.** INVOKES: inspection, testing. FOR SINGLE OPERATIONS: plan, implement, assess.

## Scope

Route by task, regardless of case count. Plan or assess without editing. Implement when requested. Available dedicated framework testing workflows take precedence. Inspect contracts and repository evidence. Code alone cannot define expectations.

## Workflow

1. Model inputs, outputs, side effects, errors, and state changes.
2. Select distinct normal, boundary, and failure cases by risk. Name expected results and defects caught.
3. Assert expected results at a faithful layer. Follow repository conventions. Remove brittle or redundant cases.
4. Run final changed tests. Diagnose failures. If tests change, rerun. Record outcomes and causes.

## Decision Rules

Honor required coverage. Do not select cases solely for counts or percentages. Keep tests deterministic and isolated. Fake boundaries only when faithful. Read [selection guidance](references/test-selection.md) for assertions and output examples.

## Error Handling

If no expected behavior is established, report blocked before editing. Otherwise, design supported cases and identify missing decisions. Do not weaken valid expectations.

## Output

Start with the first label. Use labels once, ordered. Caller-required labels replace them exactly.

`Designed cases:` Behavior, expected result, defect caught; assessment gaps or justified absence.

`Design evidence:` Contract, repository evidence, assumptions, missing decisions, environment limits, unresolved failures.

`Test execution:` must be the last line. Use `Ran: <command> => <passed|failed|exit N>` (integer N) or `Unverified: <reason>` for changed tests; otherwise `Not run; no tests changed.`

If blocked: cases contain only `Blocked.`, evidence names missing input, execution uses the no-changes status. Caller labels apply.

## Checklist

- Does each case catch a distinct plausible defect through stable observations?
- Are final outcomes recorded, including diagnosed failures, with unresolved causes identified and unrun changes unverified?

## Example

For insufficient funds, assert rejection and unchanged balances.

## Definition of Done

Finish when checklist passes. Fix production defects only when authorized.
