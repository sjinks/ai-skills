---
name: data-migration-safety
description: "Use when: planning or auditing the implementation of a schema or data migration: expand-contract sequencing, backfill idempotency and batching, dual-write or dual-read windows, rollback paths per phase, verification queries, and cutover/contract criteria."
argument-hint: "The schema or data change to implement, current shape and target shape, data volume, and the system's availability requirements."
user-invocable: true
---

# Data Migration Safety

Plan a schema or data migration as phased, verifiable, reversible-until-committed work. Migrations fail differently from code: a bad deploy rolls back in minutes, a bad migration eats data and rolls back never.

## When to Use

Use when implementing or auditing a schema change, data backfill, format migration, or store-to-store move, after the target shape is decided. Out of scope: deciding the target schema or storage design itself, designing the system's general failure policies, one-off analytical queries, and infrastructure capacity planning.

Input modes:

- Plan mode: current shape, target shape, and constraints supplied. Produce the phased plan. `### Plan gaps` holds required content the inputs cannot fill; `### Open decisions` holds choices the inputs do not settle.
- Audit mode: an existing migration plan or script supplied. Infer the shapes from the supplied script or DDL when not stated separately. Reproduce the plan restructured into the phases and checks below and list every gap under `### Plan gaps`. BLOCK only when neither shapes nor a readable script are supplied; a partial script is audited for what it shows, with the missing parts as plan gaps.

The report header carries a `Mode: plan | audit` line so consumers can tell findings about a supplied plan from self-identified holes.

## Required Inputs

- Current shape and target shape (schema, format, or store).
- Data volume and write traffic on the affected surface, when known; both drive batching and window decisions.
- Availability requirement: can the surface take downtime, and how much.
- Consumers of the affected data (services, jobs, reports), when supplied.

In plan mode, if current or target shape is missing, emit the BLOCK template; do not invent the data model. In audit mode, shapes may be inferred from the supplied plan, script, or DDL per the Input modes rules; BLOCK only when neither shapes nor a readable script are supplied.

## Phase Contract

Sequence the work expand-contract; every phase row carries an Action, a Rollback, and a Verification. A phase that does not apply (for example no dual-write window on an offline migration) keeps its row with `n/a — <reason>` in the Action cell and `n/a` in the other two.

1. `expand`: add the new shape alongside the old (new columns/tables/store), nothing reads or writes it yet. Reversible by dropping the addition.
2. `dual-write` (or dual-read): writes land in both shapes (or reads fall back across shapes); name the consistency story for failures between the two writes.
3. `backfill`: copy existing data into the new shape. Must be idempotent (safe to re-run from any point), batched (named batch size with the basis), rate-limited against production traffic, and resumable with progress tracking.
4. `verify`: named queries or checks proving old and new agree — row counts, checksums or sampled field-level comparison, and the divergence threshold that blocks cutover (default: zero unexplained divergence).
5. `cutover`: reads (then writes) move to the new shape, behind a flag or config where possible. Names its rollback: what flips back and what happens to writes that landed during the attempt.
6. `contract`: the old shape is removed. Only after a stated soak period and the verification checks passing on live traffic; this is the point of no return and is labeled as such.

## Rules

- Every phase before `contract` that mutates state has a rollback path with a stated test plan: in plan mode, each rollback names how it will be tested before its phase runs; a rollback that will reach execution untested is a plan gap. Read-only phases (such as `verify`) carry `Rollback: n/a — read-only` instead. "We'll restore from backup" counts only if the restore has actually been exercised and the data-loss window is stated.
- When the availability requirement and locking needs cannot both be met (zero downtime, hot table, no online-migration path), record the conflict under `### Open decisions` with both constraints quoted; do not pick silently.
- Schema steps that lock tables name the expected lock scope and duration basis; locking steps on hot tables need an online-migration approach or a stated downtime window.
- The backfill never runs unbounded against production without rate limiting; batch size and pause criteria are taken from input volume numbers, marked `(inferred — <basis>)`, or routed to `### Open decisions`.
- Writes that occur during the backfill are accounted for explicitly (dual-write, change capture, or a final delta pass) — name which.
- Consumers are enumerated and each is mapped to the phase where it switches; a consumer nobody switches is a plan gap.
- Numbers (batch sizes, soak duration, thresholds) follow the sourcing rule: input-sourced, `(inferred — <basis>)`, or open decision — never silently invented.

## Output Format

```markdown
## Data Migration Plan

- Migration: <one sentence: from what to what>
- Mode: plan | audit
- Volume / traffic basis: <supplied numbers, or `none supplied`>
- Availability requirement: <downtime tolerance>

| Phase | Action | Rollback | Verification |
|-------|--------|----------|--------------|
| expand | <addition> \| n/a — <reason> | <how it reverts> | <check> |
| dual-write | <both-shapes story; failure consistency> \| n/a — <reason> | <how it reverts> | <check> |
| backfill | <batched, rate-limited, idempotent, resumable copy; during-writes accounting> \| n/a — <reason> | <safe to stop/re-run from any point> | <progress + spot checks> |
| verify | <agreement checks and divergence threshold> | n/a — read-only | <the checks themselves> |
| cutover | <flagged switch> \| n/a — <reason> | <flip-back story incl. interim writes> | <post-cutover checks> |
| contract | <old-shape removal after soak> \| n/a — <reason> | point-of-no-return — <soak period, final checks> | <final verification> |

For any phase whose Action is `n/a — <reason>`, write `n/a` in its Rollback and Verification cells.

### Consumers

- <consumer>: switches at <phase> — <how>

### Plan gaps

- <missing phase content, untested rollback, unaccounted consumer>

### Open decisions

- <number or choice the input does not settle, who decides>
```

Empty sections are written with `None`. Emit exactly one value for each enum field; do not copy enum lists or angle-bracket placeholders into the report. The report has no verdict line; `Verdict: BLOCK` appears only in the insufficient-input template below.

## Error Handling (BLOCK Template)

Use this reduced template only for missing or unreadable input.

```markdown
## Data Migration Plan

Verdict: BLOCK

- Missing input: <current or target shape not provided / no readable plan or script in audit mode / text unreadable>
- Smallest addition to proceed: <concrete ask>
```

## Example

Migration: move user avatars from a `BLOB` column to object storage with a `avatar_url` column. Volume: 4 M rows, ~2 k avatar writes/day. Availability: no downtime.

Selected table rows:

| Phase | Action | Rollback | Verification |
|-------|--------|----------|--------------|
| expand | add nullable `avatar_url` column | drop column | column exists, all values NULL |
| backfill | copy blobs to object storage, set `avatar_url`; batches of 1000 `(inferred — keeps each transaction under 1 s at measured row size)`; keyed by user id, re-runnable | stop anytime; re-run skips rows with non-NULL `avatar_url` | progress count + sampled byte-compare of 1-in-1000 objects vs blobs |
| cutover | reads prefer `avatar_url` behind `avatars_v2` flag, fall back to blob | flag off; writes dual-written so nothing is lost | error rate and fallback-hit rate dashboards |

Consumers line:

- nightly profile-export job: switches at cutover — reads `avatar_url` with blob fallback until contract.

## Anti-Patterns

- Big-bang migrate-in-place with no expand phase and no rollback but optimism.
- A backfill that is not idempotent — re-running it after a crash corrupts or duplicates.
- "Verified" by row count alone when values could diverge.
- Contracting the old shape in the same release as cutover, before any soak.
- Ignoring writes that arrive during the backfill window.
- Rollback stories that have never been executed anywhere.

## Definition of Done

All six phases are present or explicitly `n/a — <reason>`, every pre-contract phase that mutates state has a rollback path (read-only phases carry `n/a — read-only`) and every phase has a verification check, the backfill is idempotent, batched, and accounts for concurrent writes, every consumer maps to a switch phase, `contract` is labeled point-of-no-return with a soak period, and every number is sourced, inferred-with-basis, or an open decision.
