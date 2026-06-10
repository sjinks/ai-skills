# Debugging Boost.Beast

Use this reference when diagnosing Beast failures, hangs, parser surprises, memory growth, EOF behavior, WebSocket failures, or TLS shutdown noise.

## First Facts To Collect

- Protocol role: client, server, proxy/gateway, tunnel, parser adapter, or WebSocket endpoint.
- Stream stack: plain TCP, `tcp_stream`, TLS stream, WebSocket stream, or test stream.
- Protocol phase: accept, connect, TLS handshake, HTTP read headers, HTTP read body, HTTP write, upgrade, WebSocket read/write, shutdown.
- Operation currently outstanding and whether another read/write is also active.
- Parser state, message limits, buffer size, keep-alive state, and close policy.
- Sanitized wire bytes for parser issues, especially headers and framing.

## Symptom Table

| Symptom | Likely causes | Confirming checks | Targeted fixes |
|---|---|---|---|
| `end_of_stream` noise | Normal keep-alive close treated as error | Parser complete? prior response sent? peer idle close? | Map EOF by state and lower log severity |
| EOF before request | Peer disconnect or partial malformed input | Header/body completion state | Reject or close according to parser state |
| Stuck read | Missing timeout, waiting for body, parser expects more bytes | Parser need, declared length, timer state | Add header/body timeout and body policy |
| Stuck write | Slow peer, overlapping write, unbounded queue | Active writer flag, queue length, socket backpressure | Serialize writes and bound queue |
| Memory growth | Unbounded `dynamic_body`, flat buffer not consumed, queued output | Body limit, buffer size, queue size | Configure limits and consume/clear at boundaries |
| Bad keep-alive | Wrong close policy, hidden bytes after rejection, parser reuse bug | Response headers, parser state, remaining buffer bytes | Set keep-alive explicitly; close after ambiguous rejection |
| TLS shutdown warning | Peer truncation, missing close_notify, local close race | TLS phase and security boundary | Map by context; do not suppress sensitive truncation |
| WebSocket close failure | Concurrent write, close racing with send, protocol error | Writer state, close code, pending queue | Gate sends after close and serialize close/write |

## Parser Debugging

- Reproduce with the smallest raw byte fixture.
- Check whether the parser accepted bytes that application policy should reject.
- Inspect body/header limits and whether they were set before reading.
- Verify no public application request object is constructed on rejection.
- Check remaining bytes in the buffer after rejection before reusing the connection.

## Timeout Debugging

- Identify which layer owns cancellation: lowest TCP layer, TLS wrapper, WebSocket stream, composed operation, or external timer.
- Confirm timeout expiry cancels the active operation and cannot fire after success in a way that corrupts state.
- Reset deadlines between protocol phases when needed.
- Treat timeout diagnostics as phase-specific, not just generic I/O failure.

## Memory Debugging

- Log or inspect parser body limit, header limit, flat buffer size, body storage size, outbound queue size, and WebSocket message size.
- Look for code that appends to buffers without consuming after successful parse.
- Look for queued responses or WebSocket messages that remain after disconnect.
- Prefer tests that simulate slow clients and partial writes.

## Minimal Reproduction Shape

Use this report shape when handing off a Beast bug:

```markdown
Role:
Stream stack:
Protocol phase:
Input bytes or peer action:
Expected behavior:
Actual behavior:
Parser/body/header limits:
Keep-alive/close policy:
Outstanding operation:
Targeted next check:
```