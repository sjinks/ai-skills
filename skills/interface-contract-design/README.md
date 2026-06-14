# interface-contract-design

> Use when: designing or auditing the contract of a boundary before implementation: API, service interface, module boundary, message schema, or webhook — operations, inputs and outputs, error semantics, idempotency, ordering, versioning posture, and invariant ownership.

This skill is aimed at new boundaries — APIs, service interfaces, module seams, message schemas, webhooks — whose contract should be decided before anything implements or consumes it, and at existing contract descriptions that need an audit.

It helps an assistant:

- define six per-operation fields: name and intent, inputs with validators, outputs including the empty-result shape, distinguishable errors with caller actions, idempotency class with duplicate-call outcome, and side effects
- decide three per-boundary fields: ordering and concurrency assumptions, versioning posture with what counts as breaking, and invariants each owned by exactly one of `caller`, `boundary`, or `downstream`
- flag implementation leakage (table names, internal services, framework types) in audit mode
- route unsettled design choices to `### Open decisions` with who decides instead of picking silently
- emit a deterministic BLOCK template when no boundary description is supplied

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
