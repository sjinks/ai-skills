# cross-model-instruction-authoring

> Use when: creating, revising, or adapting agent instructions or Agent Skills that must work across multiple model families and runtimes.

This skill is aimed at instruction artifacts that need a model-neutral core, runtime-specific adapters, and behavior that stays usable across both smaller models and frontier models.

It helps an assistant:

- extract required outcomes, invariants, evidence needs, completion criteria, and return contracts
- separate portable core guidance from runtime-specific adapters and invocation details
- check small-model executability without forcing every model into the same implementation strategy
- catch frontier-model overconstraint, unnecessary routing, and duplicated runtime assumptions
- produce a finished instruction artifact with assumptions, adapters, and compatibility notes when needed

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- [`references/model-profiles.md`](references/model-profiles.md) — model-specific tradeoffs and compatibility notes.
- [`references/authoring-checklist.md`](references/authoring-checklist.md) — finalization checklist for complex or production-bound artifacts.
- [`references/templates.md`](references/templates.md) — starting structures for common instruction surfaces.