---
name: test-design
description: >-
  USE FOR: feature/module test selection and implementation; suite-gap assessment. DO NOT USE FOR: isolated test quality or writing one preselected test, available dedicated
  framework workflows, flaky tests, review-finding plans.
argument-hint: "Contract, files, mode."
---

# Test Design

**WORKFLOW SKILL.** INVOKES: inspection, testing. FOR SINGLE OPERATIONS: select a mode.

## Scope

Select feature cases regardless of case count. Exclude preselected single-test writing. Implement only when explicitly asked to modify tests. Otherwise plan or assess requested suite gaps without editing. Available dedicated framework testing workflows take precedence. Inspect contracts and repository evidence; code alone cannot define expectations.

## Workflow

1. Model inputs, outputs, effects, errors, state.
2. Select normal, boundary, failure cases by risk. Name expectations and defects.
3. Assert results at a faithful layer. Follow repository conventions. Remove brittle or redundant cases.
4. Run final changed tests. Diagnose failures. If tests change, rerun. Record outcomes and causes.

## Decision Rules

Honor required coverage. Do not select solely for counts or percentages. Keep tests deterministic and isolated. Fake boundaries only when faithful. Read [selection guidance](references/test-selection.md) for assertions.

## Error Handling

If no expected behavior is established, report blocked before editing. Otherwise, design supported cases; identify missing decisions. Preserve valid expectations.

## Output

Start with the first label. Use ordered labels once. Caller labels replace them exactly.

`Designed cases:` Behavior, expected result, defect caught; assessment gaps or justified absence.

`Design evidence:` Contract, evidence, assumptions, missing decisions, limits, unresolved failures.

`Test execution:` must be the last line. Use `Ran: <command> => <passed|failed|exit N>` (integer N) or `Unverified: <reason>` for changed tests; otherwise `Not run; no tests changed.`

If blocked: cases contain only `Blocked.`, evidence names missing input, execution uses the no-changes status. Caller labels apply.

## Checklist

- Does each case catch a distinct defect through stable observations?
- Are final outcomes recorded, including diagnosed failures, with unresolved causes identified and unrun changes unverified?

## Example

Insufficient funds: assert rejection and unchanged balances.

## Definition of Done

Pass the checklist. Fix production defects only when authorized.
