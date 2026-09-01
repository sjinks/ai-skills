# adversarial-review

> Use when: performing adversarial review, red-team analysis, edge-case discovery, failure-mode analysis, misuse review, regression hunting, or risk-focused test planning. Do not use for ordinary readability, linting, idiomatic-style, or general best-practices review without an explicit failure, misuse, edge-case, or risk objective.

This skill is aimed at specs, designs, implementations, workflows, migrations, operational procedures, and test plans that need deliberate failure-mode review before they are trusted.

Ordinary readability, linting, idiomatic-style, and general best-practices reviews are outside its scope unless the request explicitly asks to challenge failures, misuse, material edge cases, or risks.

It helps an assistant:

- identify the target, intended behavior, assumptions, and evidence basis before judging
- apply optional review lenses for reliability, maintainability, security/privacy, user workflow, and verification
- classify failure modes with concrete categories, severity, and evidence standards
- distinguish confirmed issues, likely risks, open questions, accepted tradeoffs, and test gaps
- convert top risks into adversarial tests, mitigations, or acceptance criteria
- return `BLOCK`, `CONCERNS`, or `CLEAN` verdicts without inventing findings
- classify target revisions deterministically, then deduplicate findings and retain verdict strength for unresolved findings across repeated passes on the same revision (paired review)

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- [`references/paired-review.md`](references/paired-review.md) — cross-pass dedup and remediation-aware verdict rules for repeated passes on the same target revision.
