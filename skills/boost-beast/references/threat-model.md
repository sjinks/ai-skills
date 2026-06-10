# Threat Model

Use this reference when designing, reviewing, or testing Beast code exposed to untrusted peers, proxies, gateways, or browsers.

## Primary Threats

| Threat | Attack shape | Required defenses |
|---|---|---|
| Request smuggling | Ambiguous `Content-Length`, `Transfer-Encoding`, chunking, or parser differential behavior | Strict framing policy, parser adapter, close on ambiguous rejection, proxy tests |
| Slowloris | Peer sends headers or body too slowly | Header/body deadlines, minimum progress policy, connection caps |
| Memory exhaustion | Oversized headers, body, flat buffer, dynamic body, WebSocket messages, or write queues | Parser limits, buffer caps, bounded queues, streaming with backpressure |
| Response splitting | Unsanitized header values or target-derived response headers | Header value validation, no raw CR/LF in generated headers |
| Header confusion | Duplicate `Host`, auth, forwarding, or hop-by-hop headers | Duplicate policy, canonicalization, hop-by-hop stripping at proxy boundaries |
| Proxy differential parsing | Beast accepts a message differently than upstream or downstream parser | Normalize before forwarding, strictness tests, raw ambiguous framing rejection |
| WebSocket flooding | Peer sends large messages or floods frames faster than application consumes | Message limits, read backpressure, outbound queue caps, idle and close policy |
| TLS truncation | Peer closes without authenticated TLS shutdown | Contextual TLS shutdown policy, sensitive-transfer checks, diagnostics |

## Trust Boundaries

- Internet client to origin server.
- Client to reverse proxy or gateway.
- Reverse proxy to upstream application server.
- Parser adapter to public application request object.
- WebSocket peer to message dispatcher.
- TLS stream to HTTP or WebSocket protocol layer.

## Security Invariants

- No public application request object is constructed from malformed, oversized, ambiguous, or policy-rejected input.
- No raw ambiguous framing is forwarded to another HTTP implementation.
- No untrusted peer can cause unbounded memory growth in body storage, flat buffers, queues, or WebSocket messages.
- No normal shutdown path suppresses errors that matter for authenticated or integrity-sensitive transfers.
- No rejected first request on a keep-alive connection can become a hidden accepted second request.

## Review Questions

- What is the most hostile peer this code accepts traffic from?
- Does this code bridge Beast to another parser, proxy, framework, or upstream server?
- Which exact malformed framing cases are rejected?
- Which limits are enforced before allocation or buffering grows too large?
- Is the close/drain/keep-alive decision safe for rejected input?
- Are sensitive headers and bodies redacted from logs?

## Test Requirements

- Request smuggling fixtures for conflicting length and transfer framing.
- Slow header and slow body tests.
- Oversized header, body, WebSocket message, and write queue tests.
- Proxy/gateway tests that inspect outbound serialized bytes after normalization.
- TLS truncation tests when integrity-sensitive downloads or uploads matter.