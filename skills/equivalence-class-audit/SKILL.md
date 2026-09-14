---
name: equivalence-class-audit
description: "Use when: a concrete defect, incident, review finding, PR review comment, test failure, or bug report suggests a class of equivalent defects across sibling fields, mirror use sites, inverse operations, bounds, contracts, authorization surfaces, paths, modes, tests, docs, or source-of-truth projections."
argument-hint: "Triggering finding plus the locked audit scope: files, modules, API surfaces, specs, tests, or artifacts to audit."
user-invocable: true
---

# Equivalence-Class Audit

**UTILITY SKILL.** INVOKES: read-only inspection of supplied artifacts; no other skill required. FOR SINGLE OPERATIONS: audit one concrete finding across one locked scope.

Turn one confirmed defect into a locked-scope audit of equivalent defects: for each applicable axis below, enumerate candidate locations in scope, check each, and report presence and disposition. Standalone; same skill package, no other skill required. Use local `WORKFLOW.md` for detailed per-axis guidance and full report rules.

## Routing

Automatically activate when one concrete finding implies equivalent defects in a locked scope. When explicitly invoked with either input missing, activate and follow the missing-input branch in the procedure.

## DO NOT USE FOR:

Do not use for greenfield work, broad initial review, formatting-only changes, isolated typos, or scoped-out vendor/generated artifacts.

## Procedure

1. Select `quick`, `standard` (default), or `exhaustive`; always emit one `Output depth:` value.
2. Require a triggering finding and locked audit scope. If either is missing, do not enumerate or invent candidates; return the reduced report without a table and request exactly one missing input under `### Blocking questions`. Request the triggering finding first when both are missing; otherwise request whichever single input is missing. Missing required input suppresses the table, not depth-specific sections: preserve an explicitly requested depth and append `### Omitted axes (quick mode only)` for `quick`.
3. Enumerate candidates in scope using the catalogue below. Record other critical unknowns as Presence `blocked — clarification needed` and Disposition `blocked`.
4. Mark present defects `fix-now` by default. Use `defer-with-owner` only for an explicit deferral with a named owner/team and reason. If a required deferral lacks either, use `blocked`.

## Error Handling

Never guess missing evidence. Use the reduced report shell for missing required inputs and a blocked row for other critical unknowns.

## Example

When both required inputs are available, a quick audit emits `Output depth: quick`, only target-specific rows, and `### Omitted axes (quick mode only)`; a standard audit emits all 18 axes. Missing-input audits use the reduced form at any depth.

## Catalogue

Catalogue axes (18): Opposite Bound; Sibling Parameter/Field; Mirror Call Site/Use Site; Inverse Operation; Type/Schema Narrowing; Validation vs Normalization/Sanitization; Happy/Error/Retry/Cancel Path Twin; Race/Shared-State Twin; Permission/Authorization Class; Observability Twin; Resource Cleanup; Contract Symmetry; Equivalence by Naming; Test Mirror; Empty/Sentinel Equivalence; Async/Sync or Mode Twin; Documentation/Spec Prose Twin; Cache/Projection/Source-of-Truth Twin.

## Values

Presence: `present`, `absent`, `n/a — structurally inapplicable`, `n/a — no candidates in scope`, `blocked — clarification needed`.
Disposition: `fix-now`, `defer-with-owner`, `n/a`, `blocked`.

## Severity and Verdict

Severity: `CRITICAL` for immediate severe security, privacy, data-loss, safety, legal, or irreversible production harm; `HIGH` for normally triggerable major security, authorization, reliability, contract, or data-integrity harm; `MEDIUM` for a credible bounded regression or meaningful user/operational harm; `LOW` for a localized low-impact correctness or maintainability concern; `NONE` only for a clean report; `UNASSESSED` only when missing information prevents impact assessment. Use the highest applicable severity.

Verdict mapping: a reduced missing-input report is `BLOCK` / `UNASSESSED`. A complete report with a blocked row is `BLOCK` with a non-`NONE` severity; every complete-report blocking question maps one-to-one to a distinct normalized blocked-candidate label. Without blocked rows, `CRITICAL` or `HIGH` is `BLOCK`, actionable `MEDIUM` or `LOW` is `CONCERNS`, and only an all-absent/`n/a` report with no actionable summaries is `CLEAN` / `NONE`.

## Output

Emit no preamble or trailing commentary. The report heading must be the first content line. Every present candidate must be named in its corresponding fix-now, deferred, or blocking section. In those three disposition sections, name only candidates whose table disposition matches the section; do not repeat a candidate under another disposition, including candidates with `n/a`. If the same normalized candidate label appears in multiple rows, all such rows must use one disposition; otherwise use distinct labels. Label matching decodes HTML entities, removes Unicode format/bidi controls, applies NFKC, removes format/bidi controls again, removes Markdown code/emphasis markers, and compares case-insensitively; never use those forms to distinguish labels. Present `Test Mirror` and `Documentation/Spec Prose Twin` candidates must also be named under `### Test/doc implications`.

For machine-checked metadata, end each deferred bullet with `owner: NAME; reason: RATIONALE` and each out-of-scope bullet with `provenance: SOURCE`; values must be positive and populated. A blocker for required report input must name exactly one verbatim header label: `Triggering finding` or `Locked audit scope`; do not mention the other label. A blocker for missing deferral metadata must end with `; missing: owner`, `; missing: reason`, or `; missing: owner, reason`. Write exactly one blocker bullet per distinct normalized blocked-candidate label. Phrase each blocker as an imperative (`provide`, `specify`, `clarify`, `confirm`, `need`) or a question beginning with `what`, `which`, `who`, `why`, `can`, `could`, `would`, `are`, `does`, `do`, `is`, or `should`; Markdown emphasis is allowed.

Use this complete form only when both required inputs are available:

```text
## Equivalence-Class Audit Report
Triggering finding: <one concrete finding>
Locked audit scope: <exact files, modules, or artifacts>
Output depth: <quick | standard | exhaustive; select exactly one>
Verdict: <BLOCK | CONCERNS | CLEAN; select exactly one>
Severity: <CRITICAL | HIGH | MEDIUM | LOW | NONE | UNASSESSED; select exactly one>
| Axis | Candidate | Presence | Disposition | Evidence |
|------|-----------|----------|-------------|----------|
| <axis> | <candidate> | <strict Presence value> | <strict Disposition value> | <evidence> |
### Defects to fix now
- <present fix-now candidate, or `None`>
### Deferred follow-ups
- <present deferred candidate with owner and reason, or `None`>
### Out-of-scope candidates discovered
- <candidate with provenance, or `None`>
### Blocking questions
- <smallest required clarification, or `None`>
### Test/doc implications
- <implication, or `None`>
```

If either required input is missing, omit the table and use this reduced form. A missing header value is exactly one bare marker: `missing`, `not provided`, `not supplied`, `required`, or `needed`; do not append a clarifier.

```text
## Equivalence-Class Audit Report
Triggering finding: <supplied value or bare missing marker>
Locked audit scope: <supplied value or bare missing marker>
Output depth: <quick | standard | exhaustive; select exactly one>
Verdict: BLOCK
Severity: UNASSESSED
### Defects to fix now
- None
### Deferred follow-ups
- None
### Out-of-scope candidates discovered
- None
### Blocking questions
- <triggering finding when both inputs are missing; otherwise the one missing input>
### Test/doc implications
- None
```

For either form, when `Output depth: quick`, append `### Omitted axes (quick mode only)` and summarize why axes were not expanded. In a reduced report, state that required input is missing and no axes were enumerated. Omit this section for `standard` and `exhaustive`.

Table cell spacing may vary. Escape a literal pipe inside a cell as `\|`. In Evidence, paths containing `/` may be plain text; wrap standalone basenames, dotfiles, and extensionless filenames in backticks so they are unambiguous artifact citations. Candidate labels must not mix Latin and Cyrillic letters. The header uses the five canonical labels above, and each separator cell consists only of three or more hyphens; alignment colons are not allowed.