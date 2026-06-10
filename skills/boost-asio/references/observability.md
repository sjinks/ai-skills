# Boost.Asio Observability

Use this reference when designing, reviewing, or debugging telemetry for asynchronous networking systems. Keep labels low-cardinality and avoid logging secrets, raw payloads, authorization headers, cookies, private keys, certificate material, or attacker-controlled strings without redaction.

## Logging Principles

- Log lifecycle transitions with stable identifiers: server start, accept start, session start, handshake start/end, read start/end, write queued, write start/end, timeout armed/fired/canceled, shutdown requested, close completed.
- Include a session or connection id generated locally; do not rely on remote address as the only correlation key.
- Include operation names such as `accept`, `connect`, `handshake`, `read_header`, `read_body`, `write`, `idle_wait`, `shutdown`, and `close`.
- Include close reason and cancellation source as controlled enums, not free-form exception text.
- Log expected transport endings at debug level by default: EOF, connection reset, and `operation_aborted` during shutdown.
- Log unexpected protocol, parser, TLS, and invariant failures at warning or error level with enough state to reproduce the path.

## Useful Counters And Gauges

- Active sessions.
- Accepted connections.
- Rejected connections by controlled reason.
- Bytes read and written.
- Queued write messages and queued write bytes.
- Outstanding operations by operation type.
- Timeouts by phase.
- Cancellations by source: shutdown, timeout, peer disconnect, application abort, overload.
- Backpressure events by policy: waited, rejected, dropped, coalesced, closed.
- Event-loop or worker-thread unexpected exits.

## Trace Or Span Boundaries

- Use spans around externally visible operations: connection handling, TLS handshake, request handling, WebSocket message handling, long-running streaming writes, and graceful shutdown.
- Keep span attributes low-cardinality. Prefer route templates, operation names, protocol phase, and controlled error classes over raw URLs, payloads, peer-supplied headers, or exception messages.
- Record cancellation and timeout as explicit span events when they are expected control flow.
- Do not make telemetry emission part of the critical I/O path unless the sink is nonblocking and bounded.

## Debug State Snapshot

When debugging a hang, leak, or race, collect a point-in-time snapshot with:

- Session id and state.
- Owning executor or strand, if available.
- Active read/write/timer/shutdown operation flags.
- Current operation generation tokens.
- Write queue length and queued bytes.
- Last operation start time and last completion time.
- Close reason, if set.
- Cancellation requested flag and source.

## Invariant Checks

- Assert or log if a second read starts while a read is already in flight.
- Assert or log if a second write starts while a write is already in flight and no queue serialization exists.
- Assert or log if a handler runs on the wrong executor or outside the expected strand.
- Assert or log if a timer fires for a stale operation generation.
- Assert or log if shutdown completes while tracked sessions, tasks, timers, or work guards remain alive.

## Redaction And Cardinality

- Redact or hash remote addresses when privacy requirements demand it.
- Do not attach raw request targets, query strings, payload snippets, authorization data, cookies, certificates, or private keys to logs, metrics, or traces.
- Bound label cardinality by mapping errors to controlled reason codes.
- Sample or rate-limit repeated per-connection warnings from attacker-controlled traffic.