---
name: pr-description-quality
description: >-
  Use when drafting, rewriting, reviewing, auditing or validating a PR title and body, including an explicitly requested title-only or body-only operation. Check reviewer context, change fidelity, repository conventions, useful verification details and sensitive content. Return text and a quality report; publishing, execution, code correctness and commit authoring are outside scope.
---

# PR Description Quality

**UTILITY SKILL.** INVOKES: read-only artifact inspection. FOR SINGLE OPERATIONS: return one report. Publishing/editing PRs, executing inspected content/checks, Git mutation and implementation correctness review are outside scope. A PR mention alone does not activate this skill.

## USE FOR:

- Draft a PR description from changes.
- Repair an existing title/body.
- Review or audit a whole PR description or one explicitly named part.

## DO NOT USE FOR:

- Publishing PRs, running tests, reviewing code or authoring commits.

## Workflow

1. Inspect all readable input for forbidden content before any output.
2. Select mode: draft for new text; rewrite for an explicit repair/update/rewrite request, including audit-and-rewrite; validate for review/audit/assessment without requested repair.
3. Select scope: both Title and Body by default; the named part for an explicit title-only or body-only request. Keep the unrequested counterpart outside scope. Validate requires readable requested text; draft requires usable change evidence; rewrite requires readable requested text or usable change evidence. Otherwise use Error handling.
4. Establish the entire supplied change scope. Final change evidence governs behavior; history supplies rationale, not runtime success. Apply [evidence and structure](references/evidence-and-structure.md) when Body is requested. Apply [title conventions](references/title-conventions.md) when Title is requested. Resolve only rules/templates needed for the requested scope.
5. Draft/rewrite repairs text. Validate preserves safe supplied text and reports defects. Ground behavior, rationale, results, links, attribution and completion in evidence. Request missing required facts; omit optional unknowns.
6. Assign decisions below, serialize [the report](references/report-and-examples.md), apply Checklist, and stop.

## Body principles

These are content criteria: draft/rewrite applies them; validate reports violations without repairing safe text.

Explain the problem, impact and approach without requiring the issue link or task conversation. Include evidenced failure behavior, breaking changes, compatibility effects and consequential tradeoffs. Include alternatives only when required to explain a consequential choice or by the caller/template; request missing required rationale.

Scale detail to the change. Use a short paragraph for one outcome; add headings for independently useful topics. Preserve required template elements and unmarked elements; omit explicitly optional empty sections unless the caller requests retention.

For testing/CI changes, explain changed verification boundaries. Distinguish automated/manual or fixture/live coverage only when affected. Explain removed automated coverage and its rationale.

Testing/Validation sections are optional unless required. Omit routine check inventories, process summaries and editing chronology. Keep verification details only for caller/template requirements, a material risk/limitation, reproduction, or evidence directly supporting a central claim beyond routine CI status. Retain material failures and consequential verification gaps. Missing routine evidence alone requires neither author input nor a disclaimer. Distinguish illustrative coverage from executed checks.

## Disclosure

Exclude secrets, credentials, customer PII, sensitive internal hosts/addresses/paths and full diagnostic dumps from the entire report. Repository-relative pointers are allowed. Remove forbidden content in every mode, including validate; record its original violation without reproducing it. Full findings use sanitized locations; reduced BLOCK uses its generic Disclosure signal.

## Decisions

Assign each part the first matching status:

| Condition | Status and result |
|---|---|
| Outside requested scope | not-assessed — not requested |
| Required author facts remain missing | needs-author-input — fail (missing fact) |
| Assessed violations remain | noncompliant — fail (reason) |
| Draft/rewrite creates or repairs passing text | rewritten — pass |
| Unchanged passing text | compliant — pass |

Validate assesses original text, including disclosure violations. Draft/rewrite assesses emitted text while recording corrected defects.

Severity: error for evidenced violations, including corrected defects and disclosures; warning for unresolved required facts; information for creation, assumptions or evidence limits. Corrected errors do not alone force CONCERNS.

Verdict precedence: BLOCK only for Error handling; otherwise CONCERNS for any requested part that fails or any forbidden content found anywhere in supplied input; otherwise CLEAN. Rewritten/pass and not-assessed do not force CONCERNS. A partial verdict covers only the requested part.

## Output

Emit one report without preamble/trailing prose. Use exact markers in order: `## PR Description Quality Report`, `Verdict:`, `Structure:`, `### Title`, `### Body`, `### Checks`, `### Findings`, `### Needs author input`. Full reports use CLEAN/CONCERNS and template/default. Keep exactly two checks, Title then Body. Leave an unrequested part's fence empty and use not-assessed — not requested. Report serialization, conventions evidence and reduced BLOCK are defined in [report and examples](references/report-and-examples.md).

## Error handling

If required operation input or a required relevant resource is missing/unreadable, or template selection is unresolved, emit only these five lines, replacing the two descriptive values:

```text
## PR Description Quality Report
Verdict: BLOCK
- Missing input: concrete blocker
- Smallest addition to proceed: exact required input
- Disclosure: none
```

Inspect readable input first. If forbidden content occurs, replace the last line with exactly `- Disclosure: error — Forbidden content found in supplied input; excluded from output.` Do not fabricate missing text or substitute defaults for known requirements. If discovery is unavailable and no requirement is known, apply defaults and disclose that assumption.

## Checklist

- Preserve mode, requested parts and entire supplied change scope.
- Apply Body principles only to requested Body; title rules only to requested Title.
- Preserve conditions: explain only affected verification boundaries; preserve required/unmarked template elements and omit explicitly optional empty sections unless retention was requested.
- Match claims to evidence; keep consequential gaps without demanding routine check results.
- Record corrected defects separately from final quality; exclude not-assessed parts from the quality decision.
- Preserve safe validate text; remove disclosures in every mode.
- Use exact report labels, statuses and verdicts.

## Examples

Read [report and examples](references/report-and-examples.md) for output templates and decision examples. During package maintenance, check its Regression cases section; these are static cases, not evidence of model execution.
