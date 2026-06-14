# acceptance-criteria-quality

> Use when: writing, rewriting, or auditing acceptance criteria, definition-of-done lists, or user-story AC for quality: testable, observable, single, scoped, and implementation-neutral, plus a coverage check, so each criterion can be objectively verified before work starts.

This skill is aimed at draft acceptance criteria, definition-of-done lists, and user-story AC that need a quality contract enforced before implementation starts.

It helps an assistant:

- check each criterion against a five-property contract: testable, observable, single, scoped, and implementation-neutral, while keeping mandated contracts (protocols, formats, API shapes) intact
- mark each criterion `compliant`, `rewritten`, or `needs-owner-input`, with a `Verify by` line for every kept or rewritten criterion
- run a coverage check across success path, failure/rejection path, empty or boundary input, permission or authorization outcome, and persistence or side-effect visibility
- propose additions only from the supplied feature description, turning undecided behavior into open questions instead of invented requirements
- emit a deterministic BLOCK template when neither criteria nor a feature description is supplied

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
