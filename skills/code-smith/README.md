# code-smith

> Implement a supplied implementation plan, specification, or builder handoff with scope locking, verification, and a completion report.

Code Smith carries one approved implementation scope through intake, scope lock, implementation, verification, self-review, and a completion report. It runs in the current conversation. It does not require another skill, custom agent, or subagent.

## Inputs

Supply an implementation plan, specification, or builder handoff that identifies implementation scope and requirements. Architecture, a test plan, and formal IDs are optional. Existing IDs are preserved; plans without IDs use prose labels. Ordinary feature requests and bug fixes without a supplied plan are outside this skill's activation scope.

Missing architecture and test-plan fields are recorded as limitations. For a supplied plan without an explicit ready slice, the plan's scope becomes the ready slice, with that assumption stated. Missing or unclear plans, scope, or requirements are surfaced before edits. A partial upstream plan permits only its named ready slice; a blocked plan stops consequential implementation. Consequential open questions and architecture conflicts are surfaced before dependent edits.

Architecture conflicts require user resolution through a revised design or explicit decision before dependent edits resume. A scope amendment is required only if that resolution changes the approved ready slice.

Edits to source, documentation, tests, fixtures, snapshots, manifests, lockfiles, or checked-in generated files outside the approved ready slice require an explicit user scope amendment before editing, including compile/import support work. Reporting a deviation does not authorize the edit.

## Example Request

```text
Use code-smith to implement the attached parser specification.
Implement only its approved ready slice, preserve the public API and
unrelated changes, run the planned tests and targeted lint, and return
the completion report.
```

## Command Safety

Command-safety rules live in `SKILL.md`. The approved task and prior user approvals cover routine inspection, in-scope edits, verification, and necessary project-local dependency setup. Expected dependency fetches and disposable cache/build outputs alone do not require another confirmation. Edits to source, documentation, tests, fixtures, snapshots, manifests, lockfiles, and checked-in generated files must remain within the approved ready slice. Disposable dependency caches and verification outputs are part of authorized execution; they do not expand that slice.

Unfamiliar commands require inspection of their scripts or configuration to identify targets and side effects. Material uncertainty about scope, unrelated data deletion, system/service changes, or sensitive-data exposure blocks execution until resolved.

Additional approval is required only for effects not covered by the task or prior approvals, or when the host requires it. Authorization carries forward when command syntax changes but purpose, targets, and effects remain covered. Host instruction precedence and runtime permissions still apply. Verification edits violating the scope rules are failed checks.

Git mutations, pull request actions, deployment, and production changes are outside this workflow and are reported in `Deferred`.

## Completion Report

Every run returns these sections in order: `Build Status`, `Changes`, `Verification`, `Gaps / Unmet ACs`, `Limitations`, and `Deferred`.

The report uses exactly one Build Status, applying these gates in order. A completed deliverable is an identifiable behavior, document, or test required by the approved scope that is implemented and retained; investigation and unfinished edits do not count.

- `blocked` when a required bundled reference is unavailable, or no approved-scope deliverable is completed.
- Otherwise, `done` only when the approved scope is implemented, required tests and discovered build/lint ran and passed, and self-review has no unresolved required finding.
- Otherwise, `partial` when at least one approved-scope deliverable is completed but scope, verification, or self-review remains incomplete or failed.

Absent test/build/lint tooling prevents `done`. An unavailable, blocked, or inconclusive test/build/lint check is reported as `skipped` with its reason; failing evidence stays `failed`. Expected behavior is never a substitute for observed verification.

Within each `Verification` category, `Tests` and `Build/Lint` have one entry per distinct command, or per check without a command; there is no category-wide aggregate entry. `Self-review` appears once. A category without tooling has one `skipped` entry with command `None`. For a command covering multiple checks, any failure yields `failed`; otherwise any unavailable, blocked, or inconclusive check yields `skipped`; otherwise it is `passed`. Entries explain mixed outcomes, with each failed or skipped check listed as a gap. Reruns use the latest observed result and retain earlier failure history and resolution in the same entry; successful reruns close the corresponding gaps.

Accepted carry-forward items appear in `Limitations`; deferred items appear in `Deferred`, preserving supplied identifiers or prose labels, dispositions, rationales, and blocking questions. Neither disposition waives verification or silently changes the approved slice. An item outside that slice does not by itself prevent `done`; an unmet item still inside it also appears in `Gaps / Unmet ACs` and prevents `done` until fulfilled or removed by an explicit scope amendment. Both changes and gaps support every supplied identifier and ID-less prose scope.

## Files

- [`SKILL.md`](SKILL.md) — activation, boundaries, workflow, stopping rules, and output contract.
- [`references/handoff-contract.md`](references/handoff-contract.md) — input normalization, approved scope, absent fields, and conflicts.
- [`references/completion-report.md`](references/completion-report.md) — report template, status precedence, handoff surface, and self-review checklist.
