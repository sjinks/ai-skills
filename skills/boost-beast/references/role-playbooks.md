# Role Playbooks

Use this reference when Beast behavior depends on whether the code acts as a server, client, proxy/gateway, parser adapter, or WebSocket endpoint.

## Origin Server

- Accept only target forms and methods the server supports.
- Require `Host` for HTTP/1.1 unless a documented compatibility mode says otherwise.
- Enforce header/body limits before application routing.
- Decide per route whether request bodies are allowed.
- Set response version, status, keep-alive, body semantics, and close behavior explicitly.
- On ambiguous or malformed framing, reject and usually close the connection.

## HTTP Client

- Serialize request target and `Host` from a validated URI model.
- Set request version, body framing, and keep-alive intentionally.
- Validate response status/body rules, content length, transfer encoding, and EOF behavior.
- Bound response body size unless streaming to a controlled sink.
- Keep DNS, connect, TLS handshake, write, read, and shutdown phases distinct for errors and timeouts.

## Proxy Or Gateway

- Normalize inbound messages before forwarding. Do not forward raw ambiguous framing.
- Remove hop-by-hop headers and headers named by `Connection` unless the design explicitly preserves them for a tunnel.
- Decide how to rewrite `Host`, absolute-form targets, scheme, forwarding headers, and authority.
- Treat request smuggling as a primary threat. Parser differentials between inbound and upstream systems are release blockers.
- Close on rejected ambiguous input unless the recovery policy is proven and tested.

## CONNECT Tunnel

- Treat `CONNECT` as a mode switch after policy approval.
- Validate authority, destination allowlist, authentication, and port policy before tunneling.
- Stop normal HTTP parsing after tunnel establishment.
- Define byte forwarding, half-close, timeout, and shutdown behavior separately from HTTP request handling.

## Parser Adapter

- Keep Beast types behind the adapter unless the public API intentionally exposes them.
- Convert only after limits, framing, version, method/status, target, host, and body policy pass.
- Avoid views into Beast-owned storage unless the public object carries that storage.
- Return structured rejection reasons suitable for tests and sanitized diagnostics.

## WebSocket Endpoint

- Validate the HTTP upgrade request before `accept`.
- Configure message size, timeout, text/binary policy, ping/pong, and close behavior.
- Serialize writes through one writer path.
- Define overflow behavior for outbound queues.
- Treat close handshake, protocol error, timeout, and transport disconnect as different lifecycle states.