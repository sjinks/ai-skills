# adversarial-review

> Challenge a concrete artifact for plausible failures, misuse, regressions, and behavior-specific verification gaps.

This read-only skill reviews specs, designs, implementations, workflows, migrations, runbooks, security controls, and test plans. It separates confirmed defects from risks, questions, tradeoffs, and test gaps; recommends tests and mitigations; and returns a deterministic `BLOCK`, `CONCERNS`, or `CLEAN` verdict. Readability and style reviews without an explicit failure or risk objective are outside its scope.

The core defines boundaries, decision rules, the `## Adversarial Review Report` envelope, completion checks, and missing-target behavior. Prior passes load the revision and reconciliation rules before verdict selection; ordinary contextual prompts and category descriptions are independently consultable. Complete legacy report envelopes remain recognized as prior passes, including reports without findings. Partial reports require explicit user or trusted-caller identification as prior adversarial-review passes; shared labels alone do not establish prior-pass provenance.

## Files

- [`SKILL.md`](SKILL.md) — triggers, workflow, values, report contract, checklist, and failure handling.
- [`references/paired-review.md`](references/paired-review.md) — conditional revision identity, cross-pass deduplication, and remediation-aware verdict retention.
- [`references/review-guide.md`](references/review-guide.md) — contextual prompts, optional lenses, and failure-mode category descriptions.
