# Boost.Beast And TLS Notes

Use this reference when Asio work involves Boost.Beast, OpenSSL, TLS streams, WebSockets, or HTTP parser adapter boundaries.

## Beast Integration

- Treat Beast as a protocol implementation behind a parser adapter, not as the public application API.
- Enforce application security policy through a strictness gate before constructing public application request objects: header limits, body limits, request-target limits, framing rules, and upgrade rules.
- Keep Beast parser state, buffers, and message objects owned by the transport/protocol layer.
- Verify rejected messages cannot smuggle hidden pipelined bytes into later accepted requests.
- Keep HTTP/1.1 read and write operations serialized according to Beast stream requirements.

## HTTP Parser Boundary

- Normalize parser behavior at one boundary and document which malformed inputs are rejected.
- Reject ambiguous framing before application callbacks run.
- Preserve enough raw metadata for protocol policy only when required; avoid exposing parser internals as public API.
- Test one-shot input, split input, byte-by-byte input, valid pipelining, rejected pipelining, upgrade requests, and body-limit paths.

## TLS Stream Guidelines

- Own `ssl::context` lifetime separately from active `ssl::stream` objects; do not mutate active contexts unexpectedly.
- For client TLS, set SNI before handshake, configure `verify_peer` with the intended trust store, verify the peer hostname, and fail closed on verification errors unless the task explicitly identifies a test-only insecure mode.
- For server TLS, define where minimum protocol version, cipher policy, ALPN, certificate chain, private-key loading, and optional mTLS client-certificate verification are configured; validate replacements before applying them to future handshakes.
- Put timeouts around TLS handshake, reads, writes, and shutdown as separate phases.
- Treat TLS shutdown as best-effort when peers disconnect abruptly, but make the policy explicit.
- Keep certificate reload validation off the I/O executor when parsing or filesystem work can block.
- Apply new TLS contexts to future handshakes; do not surprise active connections unless the product explicitly requires termination.

## WebSocket Guidelines

- Serialize WebSocket reads and writes according to Beast requirements.
- Bound outgoing message queues and define slow-client behavior.
- Handle ping, pong, close, peer disconnect, cancellation, and server shutdown as first-class states.
- Disable compression by default unless the project has explicit memory, CPU, and security limits.
- Test text, binary, close handshake, ping/pong, oversized messages, and slow consumer behavior.

## Review Questions

- Which layer owns the Beast parser, TLS stream, buffers, and public application request objects?
- What malformed or ambiguous protocol inputs are rejected before application code runs?
- Are read, write, timeout, and shutdown operations serialized and cancellable?
- Are TLS contexts immutable for active streams?
- Can a slow client create unbounded queued output or retained parser state?