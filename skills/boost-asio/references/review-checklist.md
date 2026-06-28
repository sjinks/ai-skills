# Boost.Asio Review Checklist

Use this template for Asio code review. Lead with concrete defects and risks, then summarize the concurrency model.

Use `unknown` when the supplied code or context does not prove an answer; do not infer. For any `no` or safety-critical `unknown`, add either a Finding or Test Gap with the evidence needed. Order Findings by severity: critical, high, medium, low.

```markdown
## Findings

- [severity] [file/path or symbol]: [bug or risk]. Evidence: [specific code behavior]. Impact: [runtime failure]. Fix: [targeted correction].

## Lifetime Model

- Owner of socket/stream:
- Owner of buffers:
- Owner of timers:
- Owner of queued writes:
- Outstanding operations can outlive initiating scope: yes/no/unknown
- Raw `this`, references, views, or stack buffers captured by async operations: yes/no/unknown

## Executor Model

- Owning executor or strand:
- Shared mutable state touched from multiple handlers: yes/no/unknown
- Cross-thread or cross-executor access: yes/no/unknown
- Locks or atomics used correctly: yes/no/not applicable/unknown
- Blocking work on I/O executor: yes/no/unknown

## Cancellation And Timeouts

- Shutdown path cancels outstanding operations: yes/no/unknown
- Timers are paired with specific operations: yes/no/unknown
- Timer handlers ignore stale generations/state: yes/no/unknown
- `operation_aborted` treated as normal where expected: yes/no/unknown
- Peer disconnect and timeout paths clean up resources: yes/no/unknown
- Handlers re-check the teardown flag before re-arming or re-installing handlers (a cancelled read can still complete successfully from buffered bytes after close, and re-arming then resurrects torn-down state): yes/no/unknown
- That teardown flag is the one set by every close path, not just the graceful/draining one (error-path close and graceful close can set different flags): yes/no/unknown

## Backpressure And Buffering

- Concurrent writes serialized: yes/no/unknown
- Outbound queues bounded: yes/no/unknown
- Slow-client policy explicit: yes/no/unknown
- Queued buffers own their bytes until completion: yes/no/unknown
- Producers observe close/cancellation/rejection: yes/no/unknown

## Protocol And Parser Boundaries

- Parser behavior normalized behind an adapter: yes/no/not applicable/unknown
- Limits enforced before public/application objects are constructed: yes/no/not applicable/unknown
- Malformed input cannot advance hidden state or reuse rejected bytes: yes/no/not applicable/unknown
- Upgrade, TLS, or WebSocket state transitions explicit: yes/no/not applicable/unknown

## Test Gaps

- Success path:
- Peer disconnect:
- Timeout before completion:
- Cancellation before completion:
- Cancelled read completing successfully from buffered bytes after close:
- Shutdown with outstanding operations:
- Slow client/backpressure:
- Race-prone shared state:
- Parser malformed/split input:

## Suggested Fix Plan

1. [highest-risk correction]
2. [next correction]
3. [tests or verification]
```

## Severity Guidance

- `critical`: use-after-free, data race, unbounded memory growth from remote input, parser bypass, or corrupt protocol output.
- `high`: leaked sessions/tasks, shutdown hang, missing timeout, concurrent stream operations, blocking I/O executor, or uncaught coroutine exceptions.
- `medium`: unclear ownership, weak test coverage for races, inconsistent error mapping, or overly broad locking.
- `low`: style, naming, local simplification, or documentation that does not affect runtime safety.

## Review Procedure

1. Identify the async boundary and all outstanding operations.
2. Trace object lifetime from operation start to completion, cancellation, and destruction.
3. Trace executor or strand affinity for every mutable field touched by handlers.
4. Check timeout and cancellation races before API ergonomics.
5. Check write serialization and queue bounds.
6. Check parser/TLS/WebSocket state transitions if present.
7. Map every finding to a focused test gap or existing validation evidence.