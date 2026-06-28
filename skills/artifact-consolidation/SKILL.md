---
name: artifact-consolidation
description: "Use when: merging, unifying, or de-duplicating several same-kind planning artifacts (multiple specifications, architectures, or test plans) into one; reconciling colliding stable IDs across documents; building a single open-questions ledger; or marking superseded source documents for removal without losing requirements."
argument-hint: "The set of same-kind artifacts to merge (paths or content) plus the target single artifact, and any concern labels to namespace by."
user-invocable: true
---

# Artifact Consolidation

Use this skill to merge several **same-kind** planning artifacts (e.g. four specs, four architectures, three test plans) into one authoritative document **without losing or renumbering any stable ID**. The recurring failure mode it prevents is a lossy hand-merge: dropped requirements, four colliding `FR-1`s silently overwritten, duplicated rationale that drifts apart, and superseded source files left behind to rot.

The governing rule: **every source ID survives the merge.** Collisions are resolved by namespacing, never by renumbering or deletion.

## When to Use

Use when a project has accumulated multiple artifacts of the same kind that should become one, or when a user asks to "merge / unify / consolidate / de-duplicate" planning documents. Out of scope: amending a single existing artifact (that is an ordinary revision), and merging artifacts of *different* kinds (a spec and an architecture stay separate documents).

## Required Inputs

- The set of same-kind source artifacts (paths or content). If only one exists, stop — this is an in-place revision, not a consolidation.
- The target single artifact (new, or one designated source to absorb the rest).
- The **base** source: the one whose IDs keep their bare prefixes. Use the user's designation; otherwise, if the target is an existing source, that source is the base; if the target is new, the first listed source is the base.
- Concern labels to namespace by, when the user supplies them; otherwise derive them from each source's subject (e.g. `client`, `performance`, `hardening`).

## Procedure

1. **Confirm same-kind and ≥ 2 sources, and check each source for internal duplicate IDs.** Group inputs by artifact kind. Consolidate within one kind only. Scan **every** source (base and non-base) for internal duplicate IDs (two `FR-1`s within one document) — whole-source namespacing preserves them, so two `FR-1`s in a source become two `H-FR-1`s and still violate "every source ID survives." Flag any such duplicates as a pre-existing defect to resolve with the owner before merging, not something to paper over in the merge.
2. **Namespace every non-base source in full.** The base source keeps its bare prefixes (`FR-*`, `AC-*`, `D-*`, `TC-*`). Every additional source gets a short concern prefix on **all** its IDs (`C-FR-*`, `P-FR-*`, `H-FR-*`) — whether or not each individual ID collides — so one source maps to one namespace. Choose tokens tied to the concern, not the filename, so they survive a later rename. If two sources would derive the same prefix, disambiguate (`H-`, `H2-`); a prefix must be unique across all sources.
3. **Preserve, never renumber or drop.** Whole-source namespacing means no source ID is renumbered (never `FR-1` → `FR-39`) and none is dropped; the only transformation is the per-source prefix from step 2. This applies uniformly even when sources use different ID schemes (`FR-*` vs `REQ-*`): each non-base source is still namespaced in full, so one source maps to one namespace regardless of whether its tokens happened to collide.
4. **Merge section by section, de-duplicating.** Combine matching sections (scope, requirements, interfaces, acceptance, edge cases, assumptions). Collapse repeated rationale/boilerplate into one statement; keep distinct substance.
5. **Build one open-questions ledger.** Reconcile the per-source open-questions lists into a single deduplicated list; do not carry four copies of the same unresolved question.
6. **Reconcile against current source** when any artifact claims to reflect an implementation: before copying a fact forward, confirm it against the live tree — correct stale extensions, names, dependencies, enumerators, and volatile counts during the merge rather than carrying a drifted value into the merged document.
7. **Mark superseded sources for removal — do not delete.** List each merged-away document under the superseded section. The default is mark-only: never delete a source file as part of the consolidation. Deletion happens only as a separate step with explicit, path-scoped human approval for that exact path; version control keeps the source recoverable, so mark-don't-delete is the safe default.
8. **Emit the consolidation record** (below) so downstream agents resolve references unambiguously.

## ID Discipline

- Concern namespacing introduces new ID prefixes (e.g. `C-FR-*`, `P-FR-*`, `H-FR-*` — illustrative, not a fixed set). Before emitting them, gate on the project's ID discipline:
  - If the discipline allows namespaced prefixes, proceed.
  - If it fixes a closed prefix set and forbids new prefixes without updating that convention, stop and get the ID discipline updated first rather than inventing prefixes the rest of the project will reject.
  - If the supplied sources don't reveal the project's prefix policy, do not guess — stop and ask the owner whether namespaced prefixes are allowed (and which prefixes) before emitting any.
- Preserve every source ID. The base source keeps bare prefixes; every other source is namespaced in full. No ID is renumbered or dropped.
- A re-namespaced ID is recorded on the `Superseded:` line as `<old> -> <new>` (e.g. `FR-1 -> H-FR-1`). `Added`/`Updated`/`Removed` are `none` for a pure consolidation unless the merge genuinely introduced, changed, or deleted a requirement.
- The `Namespaces:` line in the `## ID Change Summary` is the authoritative concern→prefix mapping; the same mapping previewed in `## Consolidation Plan` must match it exactly.
- Return an ID change summary with a `Consolidated:` line naming which artifacts were merged in:

```
## ID Change Summary
- Added: <new ids or none>
- Updated: <ids or none>
- Superseded: <old -> new, or none>
- Removed: <ids or none>
- Consolidated: <source artifacts merged into this one>
- Namespaces: <concern -> prefix mapping>
```

## Output Format

```markdown
## Consolidation Plan

- Kind: <spec | architecture | test-plan>
- Sources: <list>
- Target: <path>
- Namespaces: <concern -> prefix>

## Merged Artifact

<the single merged document in the kind's standard section order, including the
deduplicated Open Questions ledger as one of those standard sections>

## ID Change Summary

<as above>

## Superseded Sources (mark for removal)

- <path> — merged into <target>; mark only. Delete later only with explicit, path-scoped approval.
```

## Anti-Patterns

- Renumbering or dropping a source ID to resolve a collision instead of namespacing it.
- Namespacing only the colliding IDs of a source, leaving its other IDs bare so the source maps to two namespaces.
- Leaving the source documents in place after merging (stale duplicates).
- Carrying four copies of the same open question or the same rationale paragraph.
- Copying stale facts (extensions, dependencies, counts) forward without reconciling against the current tree.
- Deleting a superseded file as part of the merge, or on machine-only authorization, instead of marking it and deferring deletion to explicit human approval.
