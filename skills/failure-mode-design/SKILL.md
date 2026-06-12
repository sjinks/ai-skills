---
name: failure-mode-design
description: "Use when: designing failure behavior for an architecture or component design before implementation: per-dependency failure modes (slow, down, wrong, partial), degradation policy, retry, timeout, idempotency and backpressure decisions, blast-radius containment, and failure observability."
argument-hint: "The design or architecture sketch to harden, its components and dependencies, and any known SLOs or operational constraints."
user-invocable: true
---

# Failure Mode Design

Decide at design time what every part of a system does when the things it depends on misbehave. Failure behavior that is not designed gets improvised in production, one incident at a time.

## When to Use

Use when an architecture sketch, component design, or integration plan is being finalized and its failure behavior needs explicit decisions. Out of scope: reviewing finished code for failure handling, incident retrospectives for failures that already happened, generic red-team critique of whether the design is the right design, and language-specific error-mechanism choices (exception policy, error-code types) — this skill decides system-level behavior those mechanisms implement.

## Required Inputs

- The design: components, the dependencies of each (services, stores, queues, third parties), and the main flows.
- SLOs, latency budgets, and operational constraints, when supplied.
- Existing failure-handling decisions, when supplied; recorded, not re-litigated.

If no design is provided, emit the BLOCK template; do not invent the system.

## Failure Sweep

For each dependency edge in the design (component → dependency), sweep four failure shapes:

1. `slow`: latency above budget but responding. Decide: timeout value and what the caller does when it fires.
2. `down`: unreachable or erroring hard. Decide: retry policy (or none), circuit-breaking, and the fallback behavior.
3. `wrong`: responding with corrupt, stale, or contract-violating data. Decide: what validation catches it and what the caller does.
4. `partial`: some of a batch/fan-out succeeded. Decide: whether the operation is retryable as a whole, resumable, or compensated.

For each flow that mutates state, additionally decide idempotency under retry: what happens when the same request is applied twice.

## Decision Per Swept Edge-Shape Pair

Each swept edge × shape pair produces a decision row with exactly one policy:

- `fail-fast`: propagate the failure immediately; caller deals with it.
- `degrade`: serve reduced functionality (stale cache, partial results, feature off) and say what "reduced" concretely is.
- `queue-and-retry`: absorb the failure and retry later; bounded by what (queue depth, TTL, dead-letter)?
- `block`: this failure must stop the flow entirely (correctness over availability); name why.
- `as-decided`: an existing decision supplied in the input, recorded rather than re-litigated; disagreement goes in the row's detail line as a remark.
- `n/a — <reason>`: this edge × shape pair does not apply (for example `partial` on a non-batch call); the reason stays in the Policy cell.

Each decision also names its blast radius: what stays working when this failure happens, stated concretely ("checkout degrades, browsing unaffected"). For `as-decided` rows, take blast radius and signal from the input when given; otherwise mark them `(inferred)` or route them to `### Open decisions`.

## Rules

- Sweep edges in the supplied design only; do not invent components. When the input names components but no flows, derive candidate mutating flows from edges that write state, mark each `(inferred)`, and list the missing flow definitions under `### Open decisions`.
- Every timeout, retry count, and bound is either taken from the input, marked `(inferred)` with a stated basis, or left as an open decision — never silently invented.
- Retries are only permitted on edges whose operation is idempotent under retry; otherwise choose a policy without retry. Every retry-bearing row (`queue-and-retry`, or any row whose details mention retries) gets a mandatory `### Decision details` line naming the duplicate-safety basis.
- Never output an unbounded policy (retries, queues, fan-out): replace it with a bounded version marked `(inferred)` or route the bound to `### Open decisions`; for `as-decided` policies with no bound, note the missing bound as the row's remark.
- Each decision names its observability signal: how operators learn this failure mode is active (metric, alert, log event).
- Decisions the input does not give enough basis to make go under `### Open decisions` with who decides.
- Large designs: when the sweep would exceed roughly 20 rows, sweep mutating and user-facing flows first and list the unswept edges under `### Open decisions` as deferred sweep work.

## Output Format

```markdown
## Failure Mode Design Report

- Design: <one sentence>
- SLOs / budgets considered: <list, or `none supplied`>

| # | Edge (component → dependency) | Shape | Policy | Blast radius | Signal |
|---|-------------------------------|-------|--------|--------------|--------|
| 1 | <component → dependency> | slow \| down \| wrong \| partial | fail-fast \| degrade \| queue-and-retry \| block \| as-decided \| n/a — <reason> | <what stays working> | <metric/alert/log> |

### Decision details

- Row <#>: <timeout/retry/bound values, fallback content, duplicate-safety basis, remarks>

### Mutating flows: idempotency under retry

- <flow>: <duplicate-application outcome>

### Open decisions

- <decision, basis missing, who decides>
```

Empty sections are written with `None`. One table row per swept edge × shape pair. Include a `### Decision details` line for every retry-bearing row, and for any other row needing more than the table line; when no row needs one, write `None`. The report has no verdict line; `Verdict: BLOCK` appears only in the insufficient-input template below.

## Error Handling (BLOCK Template)

Use this reduced template only for missing or unreadable input.

```markdown
## Failure Mode Design Report

Verdict: BLOCK

- Missing input: <no design provided / components and dependencies unreadable>
- Smallest addition to proceed: <concrete ask>
```

## Example

Design: checkout service calls a payment provider and writes orders to Postgres; a worker fans out confirmation emails.

Sample table rows:

| # | Edge (component → dependency) | Shape | Policy | Blast radius | Signal |
|---|-------------------------------|-------|--------|--------------|--------|
| 1 | checkout → payment provider | slow | degrade | order is saved as pending-payment; browsing and cart unaffected | p99 latency alert on provider client |
| 2 | worker → email API | partial | queue-and-retry | orders and checkout unaffected; some confirmations delayed | dead-letter queue depth alert |

Matching details (row 2 is retry-bearing, so its line is mandatory):

- Row 1: timeout 2 s `(inferred — half the 4 s checkout budget supplied)`; no automatic retries (charge is not idempotent without a provider idempotency key — open decision below); fallback shows "payment processing" state to the user.
- Row 2: retries 3× with backoff, then dead-letter; duplicate-safety basis: email send is keyed by order id, redelivery sends no second mail.

Under `### Open decisions`:

- Adopt the provider's idempotency-key API so payment retries become safe — owner: payments team.

## Anti-Patterns

- "We retry three times" on a non-idempotent mutation with no duplicate-safety story.
- Policies without bounds: infinite retries, unbounded queues, fan-out without limits.
- Blast radius stated as a hope ("should be fine") instead of what concretely stays working.
- Failure handling with no observability signal, discovered only by user reports.
- Inventing timeout and retry numbers with no stated basis instead of marking them inferred or open.
- Re-litigating failure decisions the input already settled instead of recording them with a remark.

## Definition of Done

Every component→dependency edge in the supplied design is swept across all four shapes — one row per edge × shape pair, with non-applicable pairs carrying `n/a — <reason>` in the Policy cell (or deferred under the large-design rule); every row has exactly one policy value, a concrete blast radius, and a signal; every retry-bearing row has a `### Decision details` line with its duplicate-safety basis; every mutating flow has a duplicate-application outcome; all numbers are sourced, inferred-with-basis, or open decisions; and nothing unbounded is presented as a policy.
