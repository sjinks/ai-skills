# architecture-decision-record

> Use when: writing, rewriting, or auditing an architecture decision record (ADR), design decision log entry, or technical decision write-up: context, decision drivers, options considered with costs, chosen option, positive and negative consequences, and revisit triggers.

This skill is aimed at technical decisions that need a durable record — or existing ADRs that need an audit — so the next engineer can reconstruct why alternatives were rejected.

It helps an assistant:

- enforce an eight-field contract: title, status, context, decision drivers, options, decision, consequences, and revisit triggers
- require at least two real options each with a benefit and a cost, flagging single-option records and strawmen as contract gaps
- require at least one concrete negative consequence and concrete revisit triggers
- mark inferred content `(inferred)` and route unmade choices to `### Open decisions` instead of deciding for the owner
- audit existing ADRs by restructuring them into the contract and listing every gap
- emit a deterministic BLOCK template when no decision context is supplied

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
