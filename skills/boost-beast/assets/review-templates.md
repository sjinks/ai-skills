# Boost.Beast Review Templates

Use these templates as starting points for repeatable Beast reviews, hardening reviews, WebSocket reviews, proxy reviews, and test-plan requests. Replace bracketed placeholders with the task-specific context.

## Beast Code Review

```markdown
Review the Boost.Beast code in [files/diff]. Prioritize correctness, security, lifetime, operation serialization, parser/serializer policy, limits, timeout/cancellation, backpressure, and tests.

Context:
- Role: [client/server/proxy/gateway/parser-adapter/websocket]
- Stream stack: [tcp_stream/ssl_stream/websocket/test stream]
- Beast boundary: [parser/serializer/session/adapter]
- Expected behavior: [short summary]

Output:
- Findings first, ordered by severity.
- For each finding, include the concrete behavior risk and the smallest credible fix direction.
- Then list open questions that affect correctness.
- End with residual test gaps.
```

## Parser Hardening Review

```markdown
Review the Beast HTTP parser adapter in [files/diff]. Focus on strictness gates, request smuggling, malformed framing, body/header limits, public application request construction, and close/drain/keep-alive behavior.

Check specifically:
- `Transfer-Encoding` plus `Content-Length`
- Duplicate or invalid `Content-Length`
- Malformed chunked input
- Missing or duplicate `Host`
- Oversized headers and bodies
- Pipelined bytes after rejected input
- Parser leniency mismatches with upstream/downstream systems

Output findings by severity, then give a targeted test plan for uncovered strictness cases.
```

## WebSocket Session Review

```markdown
Review the Beast WebSocket code in [files/diff]. Focus on upgrade validation, message limits, text/binary policy, ping/pong, close handshake, timeout behavior, write serialization, outbound queue bounds, and disconnect cleanup.

Output:
- Findings ordered by severity.
- Lifecycle summary: upgrade, read, write, close, timeout, shutdown.
- Missing tests for concurrency, oversize messages, close races, and abnormal disconnects.
```

## Proxy And Request-Smuggling Review

```markdown
Review the Beast proxy/gateway path in [files/diff]. Treat parser differentials and request smuggling as primary risks.

Check:
- Whether inbound bytes are normalized before forwarding.
- Whether hop-by-hop headers are stripped.
- Whether target, authority, scheme, and forwarding headers are rewritten intentionally.
- Whether ambiguous framing closes instead of reusing the connection.
- Whether outbound serialized bytes can preserve raw ambiguous input.

Output findings by severity and include exact malicious fixture ideas for tests.
```

## Beast Test Plan Prompt

```markdown
Create a deterministic test plan for the Boost.Beast behavior in [files/feature/bug].

Include:
- Test seam: parser adapter, serializer adapter, session loop, proxy bridge, WebSocket endpoint, or TLS stream.
- Setup and wire input or peer action.
- Assertions.
- Failure mode covered.
- Required tools or fixtures.

Cover happy path, malformed input, limits, partial I/O, EOF, timeout, disconnect, keep-alive, pipelining, upgrade, TLS, and WebSocket cases where relevant.
```