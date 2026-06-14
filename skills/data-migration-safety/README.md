# data-migration-safety

> Use when: planning or auditing the implementation of a schema or data migration: expand-contract sequencing, backfill idempotency and batching, dual-write or dual-read windows, rollback paths per phase, verification queries, and cutover/contract criteria.

This skill is aimed at schema changes, data backfills, format migrations, and store-to-store moves whose implementation needs to be phased, verifiable, and reversible until the explicit point of no return.

It helps an assistant:

- sequence the work expand-contract: `expand`, `dual-write`, `backfill`, `verify`, `cutover`, `contract` — each present or, except `verify`, explicitly `n/a — <reason>`
- require the backfill to be idempotent, batched with a sourced basis, rate-limited, resumable, and explicit about writes arriving mid-backfill (dual-write, change capture, or delta pass)
- attach a rollback path with a stated test plan to every state-mutating pre-contract phase (read-only phases carry `n/a — read-only`) and a verification check to every phase, with divergence thresholds for cutover
- map every consumer to the phase where it switches, and label `contract` as the point of no return with a soak period
- source every number (batch size, soak, thresholds) from input, mark it inferred-with-basis, or route it to open decisions
- emit a deterministic BLOCK template when the shapes are missing in plan mode, or when neither shapes nor a readable script are supplied in audit mode

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
