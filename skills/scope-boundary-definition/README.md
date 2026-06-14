# scope-boundary-definition

> Use when: defining or auditing the scope of a feature, project, spec, or task: explicit in-scope and out-of-scope lists, non-goals, deferred items, smallest valuable slice, and scope-creep risks, before work is planned or estimated.

This skill is aimed at features, specs, projects, and tasks whose scope needs explicit boundaries — or whose existing scope statement needs an audit — before planning or estimation.

It helps an assistant:

- produce four exclusive boundary lists: in scope, out of scope (with reasons), non-goals, and deferred (with revisit triggers)
- flag inferred in-scope items, and surface unsettled placements as boundary decisions for the owner instead of guessing
- identify the smallest valuable slice — what it includes, proves, and leaves for later — or rule one out with a reason
- list scope-creep vectors with the boundary statement that pre-empts each
- mark items `kept`, `moved`, or `split` when auditing an existing scope statement so the delta is reviewable
- emit a deterministic BLOCK template when no work-item description is supplied

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
