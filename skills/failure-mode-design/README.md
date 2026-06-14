# failure-mode-design

> Use when: designing failure behavior for an architecture or component design before implementation: per-dependency failure modes (slow, down, wrong, partial), degradation policy, retry, timeout, idempotency and backpressure decisions, blast-radius containment, and failure observability.

This skill is aimed at architecture sketches, component designs, and integration plans whose failure behavior needs explicit decisions before implementation.

It helps an assistant:

- sweep every component→dependency edge across four failure shapes: `slow`, `down`, `wrong`, and `partial`
- assign exactly one policy per edge × shape row — `fail-fast`, `degrade`, `queue-and-retry`, `block`, `as-decided`, or `n/a — <reason>` — with a concrete blast radius and an observability signal
- permit retries only where the operation is idempotent under retry, and settle the duplicate-application outcome for every mutating flow
- treat unbounded retries, queues, and fan-out as findings, and source every number or mark it inferred-with-basis or an open decision
- record supplied failure decisions `as-decided` with remarks instead of re-litigating them
- emit a deterministic BLOCK template when no design is supplied

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
