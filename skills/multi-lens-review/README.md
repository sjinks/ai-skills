# multi-lens-review

> Use when: structuring a multi-lens review of a change, spec, design, or implementation; combining intent, design, implementation, security, adversarial, and verification perspectives, then synthesizing them into a single integrated decision.

This skill is aimed at changes that span more than one concern (correctness, security, data, UX, ops) and need several review perspectives reconciled into a single merge decision, rather than a single-lens check that an existing focused skill already covers.

It helps an assistant:

- walk a target through Intent / Spec, Design, Implementation, Security & Privacy, Adversarial, and Verification lenses, skipping any lens that does not add value
- recognize when a lens falls squarely inside a focused review concern while keeping each skill independently discoverable by its own scope
- record findings with severity, confidence, classification, concrete trigger, evidence, and suggested fix, separated from one-line per-lens summaries
- run an explicit Synthesis step to deduplicate, reconcile lens conflicts by naming the winning tradeoff, and split required actions from follow-ups
- emit a `BLOCK`, `CONCERNS`, or `CLEAN` verdict with residual risk
- avoid role-playing independent reviewers, applying every lens by default, or hiding conflicts behind silent consensus

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
