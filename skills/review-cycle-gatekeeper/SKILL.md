---
name: review-cycle-gatekeeper
description: "Use when: enforcing review-fix cycle quality gates, verifying review findings are closed, checking merge readiness, validating fix evidence after a review round, deciding go/no-go on merge, auditing unresolved or reopened review threads, confirming regressions introduced by fixes are tracked, and producing a final pre-merge gate decision."
argument-hint: "Findings list, fix summary, verification evidence, and unresolved discussion threads."
user-invocable: true
---

# Review Cycle Gatekeeper

Use this skill to enforce closure quality across iterative review rounds. The goal is to prevent superficial thread closure and ensure real merge readiness.

## When to Use

Use this skill when a change has already been reviewed and at least one fix cycle has occurred.

Typical triggers:

- Reviewer findings were addressed in one or more follow-up commits.
- There are unresolved or reopened review threads.
- Merge readiness is unclear due to missing evidence.
- A final go or no-go decision is needed before merge.

## Required Inputs

- Findings list with severity and current status.
- Fix summary or commit list tied to findings.
- Verification evidence after fixes (tests, checks, manual validation).
- Unresolved or reopened discussion thread list (may be empty; an empty list is a valid input, an unknown list is not).

## Severity Vocabulary

Use these severity levels consistently:

- `High`: incorrect behavior, security/privacy risk, data integrity risk, crash, or production-impacting reliability fault.
- `Medium`: likely regression, contract mismatch, weak error handling, or meaningful operational risk.
- `Low`: maintainability or clarity issue with limited near-term risk. Advisory only.

### Severity Normalization

When supplied findings use a four-level vocabulary, collapse it for the gate:

| Input label | Gate severity |
|-------------|---------------|
| `CRITICAL`  | `High`        |
| `HIGH`      | `High`        |
| `MEDIUM`    | `Medium`      |
| `LOW`       | `Low`         |

Rules:

1. Apply the mapping above before evaluating the Gate Rules.
2. When the original label matters for a waiver decision, preserve it in the findings matrix `evidence` column (e.g., `orig_severity: CRITICAL`).
3. Keep the `id` column stable and free of severity annotations.

## Finding States

Each finding must be in exactly one explicit state:

- `fixed`: the underlying defect is no longer present and has been verified.
- `owned-with-remediation-plan`: the defect remains, but a named owner has committed to a concrete remediation plan.
- `waived-with-rationale`: the defect remains and will not be fixed, with explicit risk acceptance.
- `open`: the defect remains and is not fixed, owned, or waived.

### Required Evidence Per State

| State                         | Required artifacts                                                                                                                                |
|-------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| `fixed`                       | Linked fix commit or PR change, plus verification evidence (tests, manual checks) or an explicit no-test rationale (see Gate Rule 4).             |
| `owned-with-remediation-plan` | All fields listed under Ownership Rules.                                                                                                          |
| `waived-with-rationale`       | All fields listed under Waiver Rules.                                                                                                             |
| `open`                        | None required, but the finding blocks per the Gate Rules.                                                                                         |

### Reopened Findings

If a previously `fixed` finding is reopened by a reviewer, it returns to `open`. Prior verification evidence is treated as invalidated and must be re-established before the finding can return to `fixed`.

## Gate Rules

1. Every `High` finding must be either `fixed` or `waived-with-rationale`.
2. Every `Medium` finding must be `fixed`, `owned-with-remediation-plan`, or `waived-with-rationale`.
3. Every `Low` finding must be tracked in one of the four declared states. `Low` findings never block merge regardless of state.
4. Every functional fix must include test evidence or an explicit rationale for no test. A functional fix is any change that alters runtime behavior, a public contract, persisted state, or security posture; documentation-only and pure formatting changes are excluded.
5. Every fix batch must include full re-review of touched areas, not only thread-level replies. A fix batch is the set of changes pushed in a single review round (one push or one PR update), regardless of how many commits it contains.
6. Regressions introduced by fixes are treated as new findings, added to the findings matrix with their own severity and state, and additionally summarized in the "New regressions" output section for visibility.
7. The gate passes only when every `High` finding is `fixed` or `waived-with-rationale`, and every `Medium` finding is `fixed`, `owned-with-remediation-plan`, or `waived-with-rationale`. Any other state for a `High` or `Medium` finding fails the gate.

## Waiver Rules

A waiver is valid only if all fields are present:

- Scope statement: the exact code path, behavior, configuration, or condition the waiver applies to, precise enough that a future change can be tested for re-entering the waived scope.
- Technical rationale: why the residual risk is acceptable in context.
- Risk acceptance owner: named individual or role accepting the residual risk.
- Follow-up issue reference, or explicit `wontfix` rationale.

## Ownership Rules

`owned-with-remediation-plan` is valid only if it includes:

- Named owner
- Target milestone/date
- Concrete remediation steps
- Tracking issue reference

## Decision Procedure

1. Map each finding to exactly one of the four declared states; reject any other label.
2. Validate that every finding carries the artifacts listed in "Required Evidence Per State".
3. Verify that fixes are linked to findings and that touched areas have been re-reviewed per Gate Rule 5.
4. Check for newly introduced regressions and add them as findings per Gate Rule 6.
5. Apply the Gate Rules and issue the final decision.

### Insufficient Input

If required inputs are missing, unreadable, or too vague to apply the Gate Rules (for example: a finding has no severity, fix commits are not linked to findings, or verification evidence is absent for any claimed `fixed` state), do not emit `pass` or `fail`. Emit `BLOCK` with:

- The specific missing or ambiguous input.
- The findings or rules that cannot be evaluated as a result.
- The smallest concrete addition needed to proceed.

## Output Format

Return output as markdown suitable for a pull request review summary.

Include:

- Findings matrix with `id`, `severity`, `state`, `owner`, `evidence`. Regressions introduced by fixes appear here as their own rows.
- Newly introduced regressions, summarized for visibility (each must also appear in the findings matrix).
- Missing evidence.
- Waivers and whether each waiver is valid.
- Gate decision: `pass`, `fail`, or `BLOCK`.
- Exact blockers to clear before merge.

Use this shape:

```markdown
Gate decision: pass | fail | BLOCK

Findings matrix:
| id    | severity | state                         | owner       | evidence                                  |
|-------|----------|-------------------------------|-------------|-------------------------------------------|
| F-001 | High     | fixed                         | -           | commit abc1234, tests in foo.spec.ts      |
| F-002 | Medium   | owned-with-remediation-plan   | @alice      | issue #42, target 2026-06-15              |
| F-003 | Low      | waived-with-rationale         | @bob (lead) | scope: legacy /v1 endpoint; issue #43     |

New regressions:
- <item or None>

Missing evidence:
- <item or None>

Waivers:
- <id>: valid | invalid - <reason>

Blockers to clear:
- <blocker or None>
```

## Anti-Patterns

- Marking a finding as fixed without verification evidence.
- Closing threads without checking touched-area regressions.
- Treating `owned-with-remediation-plan` as acceptable for `High` severity.
- Approving merge while blockers remain undefined.
