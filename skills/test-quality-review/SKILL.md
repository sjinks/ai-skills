---
name: test-quality-review
description: "Use when: writing one preselected test, reviewing, or auditing test code (not selecting cases or a test plan) for assertion quality, determinism, isolation, and behavioral focus."
argument-hint: "Test code to audit, or one preselected behavior and expected result to test."
user-invocable: true
---

# Test Quality Review

**WORKFLOW SKILL.** INVOKES: inspection; writing when requested. FOR SINGLE OPERATIONS: audit one test.

## Scope

Audit test code or write one preselected test. Writing requires that the caller has already selected one behavior and its expected result. Feature selection and subsequent implementation belong to feature workflows, even for one case. Available dedicated framework workflows take precedence for writing.

## DO NOT USE FOR:

Feature case selection, coverage strategy, framework mechanics, or diagnosing intermittent failures.

## Workflow

1. Identify the behavior and expected result.
2. Read the [quality checklist](references/quality-checklist.md) for six dimensions. Mark each `ok` / `weak` / `missing`; cite source or generated snippet lines.
3. Ask whether the test fails when that behavior regresses. If no, prioritize `cannot-fail`.
4. Give fixes for weak or missing dimensions. Write one preselected test when requested; otherwise review without editing.

## Checklist

Tests must fail for their claimed behavioral reason. Apply six reference dimensions. A test that cannot fail is `cannot-fail`; otherwise any weak or missing dimension makes it `weak`; all dimensions ok make it `solid`.

## Error Handling

For missing review source or expected behavior, use insufficient-context output; do not guess.

## Output

For each test, use labels once in order: `Verdict:`, `Findings:`, then `Authored test:` for writing with sufficient context. Caller labels replace defaults exactly. Read the [report contract](references/report-contract.md) for branches, findings syntax, locations, and code placement.

Review verdicts: `solid` / `weak` / `cannot-fail`; missing input: `insufficient-context`. Preserve spelling. An existing test body is optional for writing. Cite real files for reviewed files or honest supplied/generated snippet lines; never invent paths.

## Example

`EXPECT_EQ(result, result)` cannot detect a regression. Compare against the contract's expected result.

## Definition of Done

Verdicts follow the checklist; findings have fixes.
