# implementation-task-decomposition

> Use when: decomposing an approved spec, design, or feature into an ordered sequence of small implementation steps before coding starts: per-step scope, verification check, and do-not-touch boundary, with explicit dependencies and no step too large to verify in one sitting.

This skill is aimed at the moment after a spec or design is approved and before coding starts, when the work needs to become an ordered sequence of small, independently verifiable steps.

It helps an assistant:

- give every step five fields: scope (one capability, not "part 1 of N"), a concrete `Verify by` check, a `Must not touch` boundary, acyclic dependencies, and a risk note
- split along seams — contract first, implementation second, call-site adoption third — with mechanical changes in their own steps
- never fuse behavior-preserving restructuring with behavior change in one step
- mark the earliest observable end-to-end step `walking-skeleton` and prefer it early
- route vague spec material to `### Blocked on` with concrete questions instead of vague steps
- emit a deterministic BLOCK template when no spec or design is supplied

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
