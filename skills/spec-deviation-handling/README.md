# spec-deviation-handling

> Use when: implementation work discovers the spec or design is wrong, incomplete, ambiguous, or infeasible mid-build: classifying the deviation, deciding proceed/pause/escalate, routing the decision to the owner, and recording the divergence instead of silently coding around it.

This skill is aimed at the mid-build moment when implementation discovers the approved spec or design is wrong, incomplete, ambiguous, or infeasible — and the silent fork must not happen.

It helps an assistant:

- classify each deviation as exactly one of `spec-bug`, `spec-gap`, `spec-ambiguity`, `infeasible-as-specified`, `better-way-found`, or `scope-creep-detected`, with evidence standards for the strong claims
- assign exactly one disposition — `proceed-and-record`, `pause-this-thread`, or `escalate-now` — under conservative tie-breaks (consumed contracts never silently proceed; proposals and creep always go to the owner)
- state the spec side and the discovery side faithfully and separately, with an interim behavior and a blocked/unblocked boundary per deviation
- package owner questions and spec-fix requests instead of rewriting the spec or coding around it
- classify multiple deviations independently — one escalation does not promote the rest
- emit a deterministic BLOCK template when either side of the deviation is missing

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
