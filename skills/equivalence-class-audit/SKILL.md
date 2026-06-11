---
name: equivalence-class-audit
description: "Use when: a concrete defect, incident, review finding, PR review comment, test failure, or bug report suggests a class of equivalent defects across sibling fields, mirror use sites, inverse operations, bounds, contracts, authorization surfaces, paths, modes, tests, docs, or source-of-truth projections."
argument-hint: "Triggering finding plus the locked audit scope: files, modules, API surfaces, specs, tests, or artifacts to audit."
user-invocable: true
---

# Equivalence-Class Audit

Turn one confirmed defect into a locked-scope audit of equivalent defects: for each applicable axis below, enumerate candidate locations in scope, check each, and report presence and disposition. Standalone; same skill package, no other skill required. Use local `WORKFLOW.md` for detailed per-axis guidance and full report rules.

Trigger: one concrete finding implies equivalent defects in a locked scope. Not for greenfield, broad review, formatting-only, isolated typos, or out-of-scope vendor/gen artifacts.

Catalogue axes (18): Opposite Bound; Sibling Parameter/Field; Mirror Call Site/Use Site; Inverse Operation; Type/Schema Narrowing; Validation vs Normalization/Sanitization; Happy/Error/Retry/Cancel Path Twin; Race/Shared-State Twin; Permission/Authorization Class; Observability Twin; Resource Cleanup; Contract Symmetry; Equivalence by Naming; Test Mirror; Empty/Sentinel Equivalence; Async/Sync or Mode Twin; Documentation/Spec Prose Twin; Cache/Projection/Source-of-Truth Twin.

Must have: Triggering finding and locked audit scope. If missing, do not enumerate/invent scope/candidates; return only Blocking questions. Other unknowns: Presence `blocked — clarification needed`, Disposition `blocked`.

Output depth: default `standard`. `quick` is the only full-axis exception: report missing context, blockers, high-risk concerns, and target-specific applicable axes, then summarize omitted axes. `standard`/`exhaustive` represent every catalogue axis at least once when the table is included. Name requested `quick` or `exhaustive` depth in the report.

Defaults: present in-scope defects are `fix-now` unless boundary says otherwise. `defer-with-owner` needs named owner/team and reason. Represent every axis unless depth is `quick`.

Presence: `present`, `absent`, `n/a — structurally inapplicable`, `n/a — no candidates in scope`, `blocked — clarification needed`.
Disposition: `fix-now`, `defer-with-owner`, `n/a`, `blocked`.

Output: `## Equivalence-Class Audit Report`; Triggering finding; Locked audit scope; table: `Axis | Candidate | Presence | Disposition | Evidence`; sections: `Defects to fix now`, `Deferred follow-ups`, `Out-of-scope candidates discovered`, `Blocking questions`, `Test/doc implications`.