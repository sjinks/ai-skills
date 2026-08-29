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
2. Require a triggering finding and locked audit scope. If either is missing, do not enumerate or invent candidates; return the reduced report without a table and put the smallest missing input under `### Blocking questions`. Missing required input suppresses the table, not depth-specific sections: preserve an explicitly requested depth and append `Omitted axes` for `quick`.
3. Enumerate candidates in scope using the catalogue below. Record other critical unknowns as Presence `blocked — clarification needed` and Disposition `blocked`.
4. Mark present defects `fix-now` by default. Use `defer-with-owner` only for an explicit deferral with a named owner/team and reason. If a required deferral lacks either, use `blocked`.

## Error Handling

Never guess missing evidence. Use the reduced report shell for missing required inputs and a blocked row for other critical unknowns.

## Example

For a quick audit, emit `Output depth: quick`, only target-specific rows, and `Omitted axes`. For standard depth, emit all 18 axes.

## Catalogue

Catalogue axes (18): Opposite Bound; Sibling Parameter/Field; Mirror Call Site/Use Site; Inverse Operation; Type/Schema Narrowing; Validation vs Normalization/Sanitization; Happy/Error/Retry/Cancel Path Twin; Race/Shared-State Twin; Permission/Authorization Class; Observability Twin; Resource Cleanup; Contract Symmetry; Equivalence by Naming; Test Mirror; Empty/Sentinel Equivalence; Async/Sync or Mode Twin; Documentation/Spec Prose Twin; Cache/Projection/Source-of-Truth Twin.

## Values

Presence: `present`, `absent`, `n/a — structurally inapplicable`, `n/a — no candidates in scope`, `blocked — clarification needed`.
Disposition: `fix-now`, `defer-with-owner`, `n/a`, `blocked`.

## Output

Use this complete form only when both required inputs are available:

```text
## Equivalence-Class Audit Report
Triggering finding: <one concrete finding>
Locked audit scope: <exact files, modules, or artifacts>
Output depth: <quick | standard | exhaustive; select exactly one>
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

If either required input is missing, omit the table and use this reduced form:

```text
## Equivalence-Class Audit Report
Triggering finding: <value or missing>
Locked audit scope: <value or missing>
Output depth: <quick | standard | exhaustive; select exactly one>
### Defects to fix now
- None
### Deferred follow-ups
- None
### Out-of-scope candidates discovered
- None
### Blocking questions
- <smallest missing required input>
### Test/doc implications
- None
```

For either form, when `Output depth: quick`, append `### Omitted axes (quick mode only)` and summarize why axes were not expanded. In a reduced report, state that required input is missing and no axes were enumerated. Omit this section for `standard` and `exhaustive`.