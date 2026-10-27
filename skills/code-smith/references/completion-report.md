When to read: before self-review and before producing the completion report.

# Completion Report Reference

This reference defines the report Code Smith returns at the end of every run. It is a local reference, not an invocable skill.

The report is the audit and handoff surface. Keep it factual, low-cardinality, and free of secrets: redact any secret or PII appearing in command or test output before including it. Reference existing IDs only; do not introduce a new ID prefix and do not number the change list.

## Required Sections

Return all sections in order. Write an empty section as `None — <reason>`.

```markdown
## Build Status
`done | partial | blocked` — <one-sentence rationale>

## Changes
- <file or change> → satisfies <existing identifier or approved prose scope>

## Verification
- Tests: <TC- IDs or prose test scope> — <passed | failed | skipped> (restated resolved command or None; exit status or reason)
- Build/Lint: <build or lint check> — <passed | failed | skipped> (restated resolved command or None; exit status or reason)
- Self-review: <checklist run; findings and how they were addressed or reported>

## Gaps / Unmet ACs
- <existing identifier, approved prose scope, or check> — <why unmet, blocking question, or follow-up>

## Limitations
- <accepted carry-forward item with supplied disposition, rationale, and blocking questions; or other limitation>

## Deferred
- <deferred carry-forward item with supplied disposition, rationale, and blocking questions>
- Commit, branch, push, pull request, and deploy are out of Code Smith's scope.
```

## Verification Entries

Within each category, emit one `Tests` or `Build/Lint` entry per distinct command; for a check without a command, emit one entry per check. Do not add category-wide aggregate entries. Include every planned test and discovered targeted build/lint check, even if it could not run. If a category has no tooling, emit exactly one `skipped` entry for that category with command `None` and the missing-tooling reason. Emit `Self-review` exactly once after those entries.

If one command covers multiple checks, list their IDs or prose labels in its entry. Assign `failed` if any covered check failed; otherwise assign `skipped` if any covered check was unavailable, blocked, or inconclusive; otherwise assign `passed`. Describe mixed outcomes in that entry and list every failed or skipped check separately in `Gaps / Unmet ACs`. Do not infer an individual pass from an aggregate success without supporting evidence.

For reruns of the same check, report its latest observed result and preserve earlier failures with their resolution or remaining impact in the same entry. A successful rerun can close the corresponding gap; unresolved failures remain gaps.

## Status Rules

- Use exactly one Build Status.
- Apply the status gates below in order. A completed deliverable is an identifiable behavior, document, or test required by the approved scope that is implemented and retained; investigation and unfinished edits do not count.
- `blocked` when a required bundled reference is unavailable, or no approved-scope deliverable is completed. Name the blocker or unfinished work.
- Otherwise, `done` only when all approved scope is implemented, required tests and discovered build/lint ran and passed, and self-review has no unresolved required finding.
- Otherwise, `partial`: at least one approved-scope deliverable is completed, but scope, verification, or self-review is incomplete or failed. Name what remains.
- For scope without IDs, apply the same gates to the approved prose scope. Report changes against that scope without inventing IDs.
- Absent test/build/lint tooling is a verification gap and prevents `done`.
- In Verification, report an unavailable, blocked, or inconclusive test/build/lint as `skipped` with its exact reason. Preserve failing evidence as `failed`, applying Verification Entries for mixed outcomes and reruns.

## Carry-Forward Status Rules

Preserve accepted items in `Limitations` and deferred items in `Deferred`, using their original identifiers or prose labels, dispositions, rationales, and blocking questions. Do not invent missing metadata.

- Neither acceptance nor deferral waives verification or silently removes an item from the approved ready slice.
- An accepted limitation or deferred item outside that slice does not by itself prevent `done`; all Status Rules still apply.
- If an accepted or deferred item remains unmet within that slice, also list it in `Gaps / Unmet ACs`. It prevents `done` until fulfilled or removed by an explicit user scope amendment.
- If the disposition conflicts with the approved slice, ask before dependent edits; do not silently select a scope.

In `Changes` and `Gaps / Unmet ACs`, preserve every supplied identifier, including `US-`, `FR-`, `NFR-`, `INT-`, `AC-`, `EDGE-`, `D-`, and `TC-`. For items without IDs, use their existing prose scope or check labels.

## Reserved Handoff Surface

The `Verification` and `Gaps / Unmet ACs` sections are the documented surface that future Test-execution, Review-execution, and Orchestrator agents will consume. Keep their shape stable; do not invoke or depend on those agents in this version.

# Self-Review Checklist Reference

This reference defines the self-review Code Smith runs at the done gate. It is self-contained: Code Smith depends on no external review skill. It is a local reference, not an invocable skill.

Read this before producing the completion report. Run the checklist over the complete change set and fold fixes back into the work; do not emit a separate review report.

## Checklist

- **Scope adherence.** Every edit to source, documentation, tests, fixtures, snapshots, manifests, lockfiles, or checked-in generated files maps to an identifier or prose scope in the approved ready slice, including any explicit user scope amendment obtained before the edit. Compile/import support edits have no independent exception. Disposable dependency caches and verification outputs do not expand the ready slice or authorize those edits. No change maps to `Excluded blocked scope`.
- **No incidental work.** No unrequested refactors, renames, formatting sweeps, feature additions, or behavior changes outside the approved scope.
- **Behavior preserved.** Unrelated existing work is preserved. Assess behavior outside the approved scope from inspected code and available checks; report uncertainty instead of claiming unobserved behavior.
- **Verification actually ran.** The planned `TC-` tests and the project's targeted build/lint were attempted; results are recorded with restated resolved commands. Apply Verification Entries for cardinality, mixed outcomes, missing tooling, and reruns. If verification could not run, this is a gap, not a pass.
- **Gaps are honest.** Every unresolved failed, skipped, or blocked check and every unmet acceptance criterion is listed as a gap, never reported as success. A successful rerun closes a check's gap only as specified in Verification Entries.
- **Carry-forward preserved.** Accepted items appear in `Limitations`; deferred items appear in `Deferred`. Their original identifiers or prose labels, dispositions, rationales, and blocking questions are preserved when supplied. Unmet items still in the approved slice also appear in `Gaps / Unmet ACs` and prevent `done`.
- **Contract conflicts surfaced.** Any architecture-vs-repository conflict or upstream open question that blocked a choice is reported. Dependent edits wait for user resolution; a scope amendment is required only when that resolution changes the approved ready slice.
- **Safety respected.** Command effects were covered by the approved task or prior approvals; any additional approval required by the skill or host was obtained. Verification edits violating the scope rules were reported as failed checks. No hooks were bypassed; no secrets or PII were requested, echoed, logged, or persisted.
- **IDs preserved.** Existing IDs are referenced as-is; no new ID prefix was introduced.
- **Report complete.** The completion report contains every required section, with empty sections written as `None — <reason>`.
