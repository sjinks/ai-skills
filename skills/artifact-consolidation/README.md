# artifact-consolidation

> Use when: merging, unifying, or de-duplicating several same-kind planning artifacts (multiple specifications, architectures, or test plans) into one; reconciling colliding stable IDs across documents; building a single open-questions ledger; or marking superseded source documents for removal without losing requirements.

This skill merges several **same-kind** planning artifacts (e.g. four specs, four architectures, three test plans) into one authoritative document without losing or renumbering any stable ID. The governing rule: every source ID survives the merge, and collisions are resolved by namespacing — never by renumbering or deletion. It is the cure for a lossy hand-merge: dropped requirements, four colliding `FR-1`s silently overwritten, rationale duplicated until it drifts, and superseded source files left behind to rot.

It helps an assistant:

- confirm the inputs are same-kind and at least two (one source is an in-place revision, not a consolidation) and merge within a single kind only
- assign a concern namespace per source — the base artifact keeps bare prefixes (`FR-*`, `AC-*`, `D-*`, `TC-*`), every additional source gets a short concern prefix (`C-FR-*`, `P-FR-*`, `H-FR-*`) tied to the concern rather than the filename
- namespace each non-base source in full (every one of its IDs gets the source's concern prefix, whether or not it collides) so one source maps to one namespace, while the base keeps bare prefixes — no ID is ever renumbered or dropped
- merge section by section, collapsing repeated rationale into one statement while keeping distinct substance, and reconcile the per-source open-questions lists into a single deduplicated ledger
- verify any "reflects current implementation" facts against the live tree during the merge instead of carrying drifted values forward
- mark each merged-away document for removal (deleting only with explicit approval) and emit a consolidation record with an `## ID Change Summary` (including a `Consolidated:` line and the namespace mapping)

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
