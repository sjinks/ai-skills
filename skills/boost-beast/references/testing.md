# Testing Boost.Beast Code

Use this reference to plan deterministic tests for Beast parser, serializer, session, WebSocket, TLS, proxy, and parser adapter behavior. For protocol security and threat overview, consult [threat model](./threat-model.md) first.

## Test Seams

- Parser adapter: byte input to normalized request or rejection result.
- Serializer adapter: response object to exact bytes or validated HTTP response.
- Session loop: loopback socket or Beast test stream with partial I/O and disconnects.
- Proxy/gateway boundary: inbound bytes, normalized state, outbound serialized bytes.
- WebSocket endpoint: upgrade request, frame sequence, close behavior, queue behavior.

## Byte-Level Parser Fixtures

Use raw byte fixtures for malformed or ambiguous HTTP. Include complete and partial inputs.

Cases to cover:

- Valid minimal HTTP/1.1 request with `Host`.
- Missing `Host` under HTTP/1.1 if rejected by policy.
- Duplicate matching and conflicting `Content-Length`.
- `Transfer-Encoding: chunked` with `Content-Length`.
- Malformed chunk size and missing terminating chunk.
- Oversized header block.
- Oversized body that fails before full buffering.
- EOF before complete header block.
- EOF before complete body.
- Pipelined request after a rejected first request.

## Serializer Tests

- `Content-Length` matches body bytes for `string_body` responses.
- `empty_body` responses emit no body for no-body statuses.
- Keep-alive and close headers match the connection policy.
- Chunked streaming emits valid chunks and terminator.
- Partial write simulation does not corrupt response bytes.

## Session Tests

- One complete request receives one complete response.
- Keep-alive handles multiple sequential requests without leaking bytes.
- Slow or partial header read times out.
- Slow or blocked write triggers the chosen slow-client policy.
- Peer disconnect during header, body, and response write is cleaned up deterministically.
- Server shutdown cancels outstanding reads/writes without reporting application failures.

## WebSocket Tests

- Upgrade succeeds only for allowed target, host/origin, authentication, and subprotocol policy.
- Oversized message is rejected with the expected close behavior.
- Concurrent send attempts are serialized through one writer.
- Ping/pong and idle timeout behavior is deterministic.
- Normal close handshake differs from abnormal disconnect.
- Text messages validate UTF-8 when the application requires text semantics.

## TLS Tests

- Handshake failure is reported before HTTP state is created.
- HTTP read/write failures after handshake include phase-specific diagnostics.
- TLS shutdown behavior matches the security boundary.
- Certificate reload or context changes do not mutate active streams unexpectedly.

## Fuzzing Targets

- Parser adapters are excellent fuzz targets because input is just bytes and output can be accept/reject plus normalized fields.
- Keep fuzz targets deterministic: no network, filesystem, time, random IDs, or global state.
- Assert invariants: no crash, no unbounded allocation, no accepted ambiguous framing, and no public request construction on rejected input.

## Evidence To Report

- Test layer and seam used.
- Exact protocol behavior covered.
- Boundary values for body/header/message limits.
- Whether tests include malformed, partial, timeout, disconnect, and keep-alive cases.
- Any untested behavior that remains risky.