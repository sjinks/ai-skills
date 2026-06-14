# spec-edge-case-enumeration

> Use when: enumerating edge cases for a feature spec, user story, or behavior description before implementation: empty and boundary inputs, error paths, permissions, concurrency, time, locale and text, limits, and lifecycle states, deciding which belong in the spec.

This skill is aimed at feature specs, user stories, and behavior descriptions being finalized, whose edge cases need systematic enumeration so spec decisions are made before implementation instead of during it.

It helps an assistant:

- sweep eight edge-case dimensions: empty-and-boundary, error-paths, permissions, concurrency, time, locale-and-text, limits, and lifecycle, reporting case-less dimensions as `n/a` with a reason or as swept with no plausible cases
- phrase each case as a concrete scenario and give it exactly one disposition: `spec-decision`, `spec-stated`, `implementation-detail`, or `flag-for-deep-review`
- present options with user-visible consequences for spec decisions while leaving the choice to the owner
- record supplied edge-case decisions as `spec-stated` even under disagreement, noting disagreement as a remark
- flag specialized surfaces (security-sensitive text, file parsing, payment idempotency) for dedicated review without performing it
- emit a deterministic BLOCK template when no feature description is supplied

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
