# Boost.Beast Review Checklist

Use this reference when producing a Beast-focused code review. Lead with concrete findings; use the checklist to avoid missing common protocol and lifetime risks.

## Review Output Shape

```markdown
Findings:
- Severity: file/path and behavior. Explain the protocol, lifetime, security, or test risk.

Open questions:
- Only include questions that affect correctness or risk.

Summary:
- Short description of what was reviewed and residual test gaps.
```

## Checklist

### Beast Boundary

- The code's Beast boundary is clear: parser, serializer, session, adapter, proxy bridge, WebSocket, or TLS stream.
- Beast-specific objects do not leak into public API unless that is the intended abstraction.
- Public request/response objects are built only after protocol policy passes.

### Lifetime

- Stream, parser, serializer, message, body storage, buffers, and file handles outlive outstanding async operations.
- Handlers or coroutines do not capture raw `this` unless object lifetime is otherwise guaranteed.
- String views and buffer views do not outlive Beast message or backing storage.

### Operation Serialization

- There is at most one active read per stream.
- Writes are awaited, queued, or serialized by one writer path.
- WebSocket close, ping/pong, and writes do not race in unsupported ways.

### Limits And Backpressure

- Parser body/header limits are configured before reading untrusted input.
- Flat buffers, dynamic bodies, write queues, and WebSocket messages are bounded.
- Slow-client behavior is explicit and tested.

### HTTP Semantics

- Method, target form, version, `Host`, and body expectations are validated.
- `Content-Length`, transfer encoding, chunked framing, keep-alive, close, and EOF are handled deliberately.
- No-body statuses and `HEAD` responses cannot accidentally emit bodies.
- Rejected ambiguous messages do not allow hidden bytes to poison a reused connection.

### Proxy/Gateway Security

- Hop-by-hop headers are stripped or handled according to policy.
- Parser differential and request-smuggling cases are tested.
- Raw ambiguous framing is not forwarded after parsed policy decisions.

### TLS And WebSocket

- TLS handshake, HTTP, upgrade, WebSocket, and shutdown phases have separate error mapping.
- TLS truncation behavior matches the security boundary.
- WebSocket message size, text/binary policy, ping/pong, close, and outbound queue behavior are explicit.

### Tests

- Tests include malformed and boundary traffic, not only happy paths.
- Tests cover EOF, timeout, disconnect, keep-alive, pipelining, rejected first request, oversized header/body, and slow write where relevant.
- Parser adapters have byte-level tests or fuzzing for ambiguous framing.

## Severity Guide

- High: request smuggling exposure, unbounded untrusted memory growth, use-after-free, overlapping stream operations, hidden bytes accepted after rejection, TLS truncation suppressed across a sensitive boundary.
- Medium: missing parser limits on trusted-only paths, incomplete timeout handling, ambiguous keep-alive behavior, missing WebSocket queue cap, poor error mapping that affects operations.
- Low: diagnostics gaps, minor output formatting issues, missing narrow tests for low-risk compatibility behavior.