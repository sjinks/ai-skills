# assumption-surfacing

> Use when: surfacing implicit assumptions in a spec, plan, design, or estimate before work starts: data shapes, ordering, scale, auth context, environment, compatibility, dependency behavior, and people-process expectations, classifying each as verify-before-build or accept-with-risk.

This skill is aimed at specs, plans, designs, and estimates about to be committed to, whose implicit assumptions need to become an explicit verification worklist before building starts.

It helps an assistant:

- sweep eight assumption categories: data, ordering, scale, auth-context, environment, compatibility, dependency-behavior, and people-process
- state each assumption as a falsifiable claim anchored to the plan text that depends on it
- classify each assumption as `verify-before-build` (with a verification step) or `accept-with-risk` (with the risk if wrong and the earliest signal that would reveal it)
- apply the tie-break that structural damage — schema, contract, security, data loss — forces `verify-before-build` regardless of likelihood
- produce the worklist without performing the verifications or inventing owners
- emit a deterministic BLOCK template when no plan or spec text is supplied

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
