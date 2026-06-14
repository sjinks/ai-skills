# adversarial-review

> Use when: performing adversarial review, red-team analysis, edge-case discovery, failure-mode analysis, misuse review, regression hunting, and risk-focused test planning.

This skill is aimed at specs, designs, implementations, workflows, migrations, operational procedures, and test plans that need deliberate failure-mode review before they are trusted.

It helps an assistant:

- identify the target, intended behavior, assumptions, and evidence basis before judging
- apply optional review lenses for reliability, maintainability, security/privacy, user workflow, and verification
- classify failure modes with concrete categories, severity, and evidence standards
- distinguish confirmed issues, likely risks, open questions, accepted tradeoffs, and test gaps
- convert top risks into adversarial tests, mitigations, or acceptance criteria
- return `BLOCK`, `CONCERNS`, or `CLEAN` verdicts without inventing findings

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
