When to read: when composing a report or resolving finding, status, verification, or verdict ambiguity.

# Worked reports

These are hypothetical reports. File locations and check results illustrate the contract; they are not observations from this repository. Coverage groups below account for all 13 dimensions without requiring a file-by-dimension table.

## Retain a useful abstraction

Quality mode: review

Quality scope: Supplied `storage/port` and its single implementation; inspected consumers and tests. Assessed naming, comments, control flow, abstraction, duplication, API design, architecture, validation, errors, side effects, behavioral tests, performance costs, and change safety. The interface owns a consumer-facing storage contract and allows tests to exercise failures independently of the database. No exclusions or coverage gaps.

Quality findings: None.

Quality changes: None.

Quality verification: Not run; read-only source inspection established the boundary role and inspected test assertions. No runtime result is claimed.

Quality limitations: None.

Quality verdict: Clean

## Report a genuine defect

Quality mode: review

Quality scope: Supplied `client/retry-policy`; inspected configuration owner, callers, and retry tests. Assessed all 13 dimensions: naming, comments, control flow, abstraction, duplication, API design, architecture, validation, errors, side effects, behavioral tests, performance costs, and change safety. No exclusions or coverage gaps.

Quality findings:

CQ-001 — Retry configuration is ignored

Severity: High

Status: Open

Location: `client/retry-policy:18`

Evidence: The public `maxAttempts` option is accepted but the retry loop always uses the literal `3`; the inspected caller passes `1` to forbid retries.

Consequence: A failed operation can be repeated despite the caller's explicit limit.

Correction: Propose honoring the configured limit in a separate behavior-changing task; do not apply the correctness fix in this skill.

Resolved when: The loop follows the documented attempt-count contract, including the one-attempt case, and focused normal/failure checks pass.

Quality changes: Proposal only; review mode authorizes no edits.

Quality verification: Not run; the ignored binding was established by source inspection.

Quality limitations: Runtime behavior has not been exercised; the finding is source-supported.

Quality verdict: Needs attention

## Apply a safe simplification

Quality mode: simplify

Quality scope: Requested code-quality assessment of `format/label:12` with application of supported findings; inspected neighboring comments and tooling configuration. Assessed comments and change safety. Naming, control flow, abstraction, duplication, API design, architecture, validation, errors, side effects, behavioral tests, and performance costs are not applicable to the ordinary prose-only edit because their code is unchanged. No exclusions or coverage gaps.

Quality findings:

CQ-001 — Narration obscures the useful contract comment

Severity: Low

Status: Resolved

Location: `format/label:12`

Evidence: Three adjacent comments restate assignments between a contract comment and the code it explains; they contain no invariant or rationale and are not consumed by tooling.

Consequence: Readers must sift through repeated narration to locate the formatting contract.

Correction: Remove the three narration comments and retain the contract comment.

Resolved when: Narration is removed, contract documentation remains accurate, and applicable prose checks pass.

Resolution evidence: The final diff removes only the three comments; the contract comment remains accurate and lint passes.

Quality changes: Applied the comment removal.

Quality verification: Documentation class. Before and after editing, inspected prose/tooling boundaries and documentation accuracy; project lint passed before editing (the initial passing state) and again after editing on the combined result. Inspected the combined diff. Behavioral tests were not required for this prose-only edit.

Quality limitations: None.

Quality verdict: Clean

## Leave an edit as a proposal

Quality mode: simplify

Quality scope: Requested code-quality assessment of `checkout/eligibility` with application of supported findings; inspected callers and available tests. Assessed naming, comments, control flow, abstraction, duplication, API design, architecture, validation, errors, side effects, performance costs, and change safety. Behavioral tests are a coverage gap: the available test files cannot be read in this checkout. No unrelated paths selected.

Quality findings:

CQ-001 — Repeated eligibility policy obscures the decision

Severity: Medium

Status: Open

Location: `checkout/eligibility:20,35`

Evidence: Two branches repeat the same eligibility predicate owned by this module, and its adjacent policy comment requires them to change together.

Consequence: A policy update can leave the two branches inconsistent.

Correction: Extract the shared predicate while preserving evaluation order and effects.

Resolved when: Both branches use the same policy operation, with unchanged outcomes and effects demonstrated by passing focused checks before and after the edit.

Quality changes: Proposal only; no edit applied because the required behavioral baseline is unavailable.

Quality verification: Behavior class. Not run; affected tests are unavailable. Source inspection supports shared policy ownership but does not establish verified equivalence.

Quality limitations: Missing test files prevent assessment of behavioral tests and establishment of the required baseline.

Quality verdict: Needs attention
