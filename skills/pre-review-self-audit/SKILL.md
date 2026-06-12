---
name: pre-review-self-audit
description: "Use when: auditing your own change before requesting review, running a pre-review or pre-PR self-check, checking diff hygiene, leftover debug code, commented-out code, unrelated changes, missing tests for changed behavior, commit atomicity, PR description accuracy, or repeated templated edits applied consistently across files before opening or updating a pull request."
argument-hint: "The diff or changed files, the intended behavior of the change, and the draft PR description or commit messages when available."
user-invocable: true
---

# Pre-Review Self-Audit

Audit your own change against the checks a reviewer will apply, before requesting review. The goal is to remove the predictable first review round: hygiene findings, missing tests, and description drift.

## When to Use

Use after a change is functionally complete and before opening a pull request or requesting re-review. Author-side only: reviewing someone else's change, arbitrating review threads, or post-review fix verification are out of scope.

## Required Inputs

- The diff or change set (files plus changed content).
- The intended behavior of the change, stated by the author.
- Draft PR description and commit messages, when they exist.

If the diff or change set is unavailable, emit the BLOCK template; do not audit from the description alone. If commit messages or a PR description do not exist yet, do not block: mark checklist items 5–6 `n/a` with a note. If the diff contains a repeated templated edit but repository search is unavailable, do not block: mark item 9 `n/a` and list the sweep as outstanding, using the canonical command `git grep -nF -- '<template line>'` with a single, distinctive line from the validated template substituted (the command matches line by line, so never substitute a multi-line snippet); use a different search tool only when the author names one.

## Workflow

1. State the change intent in one sentence and lock the audit scope to the supplied diff. One exception: checklist item 9 may search the rest of the repository, but only for instances of a pattern the diff touches.
2. Discover the project's own checks structurally: CI configuration, package scripts, Makefile or task runner targets, lint and formatter configs. Run them when the environment allows; otherwise list each as outstanding. Never invent check names.
3. Sweep the checklist below over the whole diff, not only suspicious areas.
4. Report using the output format. All checklist items must appear with a status.

## Checklist (gating source of truth)

1. Diff hygiene: no debug prints, dumps, commented-out code, new stray TODO/FIXME, temporary files, committed secrets, or accidental formatting churn.
2. Scope: every hunk serves the stated intent; unrelated changes are flagged for removal or a separate change.
3. Tests: every behavior change is exercised by a test in the diff, or carries an explicit no-test rationale.
4. Contracts: public API, schema, config, or wire-format changes are documented, with migration or compatibility notes.
5. Commit atomicity: commits are separable and messages match their content.
6. Description accuracy: the PR description matches the actual diff; every claim in it is verifiable from the diff.
7. Project checks: discovered checks were run and passed, or are listed as outstanding with the exact command.
8. Reviewer anticipation: spots likely to draw a reviewer question carry a code comment or a PR-description note explaining the choice.
9. Repeated-pattern consistency: when the diff applies the same templated sentence, snippet, or contract reference (path, heading, enum value, label casing) across multiple files, validate the template once, then search the whole repository and report each instance — changed or not — that deviates from the validated template as a finding. A value shared only between changed code and its own test does not count as a templated edit. Deviating instances in files the diff does not touch are fixed as a follow-up change listed as outstanding, not folded into the current diff.

## Severity Rubric

- `High`: would force a review round on its own — broken or untested behavior change, misleading description, committed secret.
- `Medium`: a likely reviewer finding — scope creep, noisy diff, unclear naming, missing contract note, an instance deviating from a templated pattern.
- `Low`: minor polish; advisory only.

## Output Format

```markdown
## Pre-Review Self-Audit Report

- Change intent: <one sentence>
- Scope audited: <files / diff summary>
- Project checks discovered: <list with run|outstanding status, or "none found">

| # | Checklist item | Status | Notes |
|---|----------------|--------|-------|
| <1> | <Diff hygiene> | <pass \| fail \| n/a> | <evidence or reason> |

One row per checklist item, all nine items.

### Findings

- [High|Medium|Low] <anchor> — <issue> — <action before requesting review>

### Outstanding before requesting review

- <ordered list, or "None">

Verdict: CLEAN | CONCERNS | BLOCK
```

Verdict mapping: `CLEAN` — all checklist items pass, no findings, ready for review. `CONCERNS` — findings exist; fix or annotate them before requesting review. `BLOCK` — insufficient input or the change is not in a reviewable state. Emit exactly one value for each enum field; do not copy enum lists or angle-bracket placeholders into the report.

No-findings path: when every item passes, still emit the full table, keep the `### Findings` heading with the single line `Findings: none` under it, and return `CLEAN`.

### BLOCK Template (insufficient context)

```markdown
## Pre-Review Self-Audit Report

Verdict: BLOCK

- Missing input: <diff, change intent, or other named gap>
- Cannot evaluate: <checklist items affected>
- Smallest addition to proceed: <concrete ask>
```

## Definition of Done

For non-BLOCK reports: every checklist item has a status, every `fail` has a finding with severity and action, project checks are run or listed as outstanding, and the verdict line is the last line of the report. BLOCK reports follow the BLOCK template exactly.
