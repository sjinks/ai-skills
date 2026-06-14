# dependency-choice-review

> Use when: deciding at design time whether to build, buy, or adopt a library, framework, service, or platform dependency: maintenance signals, API stability, lock-in and exit cost, operational burden, license fit, and the conditions under which the choice should be reversed.

This skill is aimed at design-time build-vs-buy and dependency-adoption decisions, before a library, framework, service, or platform is woven into a design.

It helps an assistant:

- score each candidate (including the build option) on six dimensions: maintenance health, API stability, fit, lock-in and exit, operational burden, and license and policy
- demand concrete evidence per `concern`, keep unverifiable claims `unknown`, and map each `unknown` to the cheapest way to settle it
- state an exit path and its cost for every candidate, including the recommended one
- treat license and compliance constraints as pass/fail eliminations
- end with a recommendation or deciding question plus concrete reversal triggers
- emit a deterministic BLOCK template when no capability or candidate is supplied

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
