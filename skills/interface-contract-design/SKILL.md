---
name: interface-contract-design
description: "Use when: designing or auditing the contract of a boundary before implementation: API, service interface, module boundary, message schema, or webhook — operations, inputs and outputs, error semantics, idempotency, ordering, versioning posture, and invariant ownership."
argument-hint: "The boundary to design or the existing contract to audit, plus consumers, constraints, and any project API conventions."
user-invocable: true
---

# Interface Contract Design

Define what a boundary promises before anything implements or consumes it. Boundaries designed implementation-first leak internals into the contract and leave error semantics, idempotency, and versioning to be discovered by the first outage.

## When to Use

Use when a new boundary (API, service interface, module seam, message schema, webhook) needs its contract defined, or an existing contract description needs an audit, before implementation. Out of scope: implementing the boundary, generating client/server code or formal schema files (OpenAPI, protobuf) — this skill produces the contract decisions those artifacts encode; language-specific binary-compatibility concerns; and auth-protocol internals beyond naming what the contract requires from them.

Input modes:

- Design mode: boundary purpose, consumers, and constraints supplied. Produce the contract.
- Audit mode: an existing contract description supplied. Reproduce it restructured into the contract fields (full template, including the `Idempotency:` line per operation) and list every gap under `### Contract gaps`.

Missing consumers do not block either mode: write `none named in input` on the Consumers line and add a `### Contract gaps` entry naming the unconfirmed consumer set. The BLOCK template is only for a missing boundary description.

## Required Inputs

- The boundary's purpose and its known consumers, or the existing contract text to audit.
- Constraints when supplied: latency budgets, payload limits, compatibility requirements, project API conventions.

If no boundary description is provided, emit the BLOCK template; do not invent one.

## Contract Fields

Decide each field per operation, and the cross-cutting fields once per boundary:

Per operation:

1. Name and intent: one line, caller vocabulary, not implementation vocabulary.
2. Inputs: each field with type, optionality, and validation rule; who validates is stated.
3. Outputs: success shape, including empty-result shape.
4. Errors: each distinguishable failure the caller can act on, with its signal (code, type, or variant). Failures collapsed into one signal on purpose are recorded on the Errors line as `collapsed: <failures> — <why one signal suffices>`.
5. Idempotency: `idempotent`, `idempotent-with-key`, or `not-idempotent`; retries are only safe under the first two. The `— <duplicate-call outcome>` suffix is required for `idempotent-with-key` and `not-idempotent`; plain `idempotent` operations omit it.
6. Side effects: what observably changes beyond the response, including emitted events.

Per boundary:

7. Ordering and concurrency: whether callers may assume ordering between operations, and what concurrent calls to the same resource do.
8. Versioning posture: how the contract may evolve — `additive-only`, `versioned`, or `frozen` — and what counts as a breaking change for this boundary.
9. Invariant ownership: each invariant the boundary depends on, with exactly one owner: `caller`, `boundary`, or `downstream`. An invariant nobody owns is a gap.

## Rules

- Design the contract from consumer needs in the input; mark any operation or field you inferred with `(inferred)`.
- Infer-vs-defer rule: fill an unspecified detail marked `(inferred)` when any reasonable consumer would accept it (field types, validation bounds); route it to `### Open decisions` when consumers or operators would disagree about it (idempotency mechanism, pagination style, error taxonomy, versioning posture).
- Every error a caller must handle differently gets its own signal; "returns 500 with a message" is a gap, not an error design.
- An operation with `not-idempotent` and no stated duplicate-call outcome is a gap.
- For message schemas and webhooks, treat each message type as an operation: Inputs are the payload fields, Outputs are the expected consumer acknowledgment, Errors are rejection and dead-letter outcomes, and Idempotency covers redelivery of the same message.
- Do not import implementation details (table names, internal service names, framework types) into the contract unless the contract deliberately exposes them; flag them in audit mode.
- Unresolved design choices the input does not settle go under `### Open decisions` with who decides; do not pick silently.

## Output Format

```markdown
## Interface Contract

- Boundary: <name and one-line purpose>
- Consumers: <from input, or `none named in input`>
- Versioning posture: additive-only | versioned | frozen — breaking change here means: <one line>
- Ordering and concurrency: <one or two lines>

### Operations

#### <operation name>

- Name: <name> — <intent>
- Inputs: <field: type, required|optional, validation, validator>
- Outputs: <success shape; empty-result shape>
- Errors: <signal — when, caller action; `collapsed: …` entries where applicable>
- Idempotency: <idempotent | idempotent-with-key — <duplicate-call outcome> | not-idempotent — <duplicate-call outcome>>
- Side effects: <observable changes, or none>

### Invariants

| Invariant | Owner |
|-----------|-------|
| <invariant> | caller \| boundary \| downstream |

### Contract gaps

- <field or operation>: <what is missing or leaks implementation>

### Open decisions

- <choice, options, who decides>
```

Empty sections are written with `None`; for the `### Invariants` table, replace the table with `None`. Repeat the `#### <operation name>` block once per operation. In design mode `### Contract gaps` is `None` unless required input material is missing (then name it instead of inventing it). The report has no verdict line; `Verdict: BLOCK` appears only in the insufficient-input template below.

## Error Handling (BLOCK Template)

Use this reduced template only for missing or unreadable input.

```markdown
## Interface Contract

Verdict: BLOCK

- Missing input: <no boundary description provided / text unreadable>
- Smallest addition to proceed: <concrete ask>
```

## Example

Boundary: invoice-export service consumed by the billing UI and a nightly reconciliation job.

Boundary header lines:

- Versioning posture: additive-only — breaking change here means: removing or renaming a response field, or narrowing an accepted input
- Ordering and concurrency: no ordering guaranteed between exports; concurrent `startExport` calls for the same account are serialized by the boundary

Invariants table row: `| an account has at most one running export | boundary |`

Selected output lines for one operation:

- Name: `startExport` — begin an async export of one account's invoices for a date range
- Inputs: `accountId`: string, required, must be an existing account, validated by boundary; `range`: date interval, required, max 366 days, validated by boundary
- Outputs: `exportId` plus `status: accepted`; empty range is accepted and produces an empty export, not an error
- Errors: `ACCOUNT_NOT_FOUND` — caller fixes the id; `RANGE_TOO_LARGE` — caller narrows the range; `EXPORT_ALREADY_RUNNING` — caller polls the existing export
- Idempotency: idempotent-with-key — same idempotency key returns the original `exportId`
- Side effects: export job enqueued; `export.started` event emitted

## Anti-Patterns

- Error design by status code only, with all failures collapsed into one indistinguishable signal.
- `not-idempotent` operations with no stated duplicate-call outcome in a contract consumed over a retrying transport.
- Internal table, queue, or framework names leaking into operation names and fields.
- Invariants listed without an owner, or owned by "everyone".
- Deciding open design choices silently instead of routing them to the owner.

## Definition of Done

Every operation carries all six per-operation fields, the three per-boundary fields are stated, every invariant has exactly one owner, inferred content is marked `(inferred)`, implementation leakage is flagged (audit mode), and unresolved choices appear under `### Open decisions` rather than being picked silently.
