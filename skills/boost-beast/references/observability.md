# Observability

Use this reference when adding or reviewing logs, metrics, traces, and diagnostics for Beast-based systems.

## Logging Principles

- Log protocol phase, role, close reason, and local decision, not just raw error codes.
- Redact secrets by default: `Authorization`, `Cookie`, `Set-Cookie`, API keys, bearer tokens, and request or response bodies.
- Avoid logging complete raw HTTP messages in production. Prefer sanitized method, target category, status, selected headers, and byte counts.
- Log parser rejection reasons in structured form that tests can assert without exposing sensitive data.
- Distinguish local cancellation, timeout, peer disconnect, parser rejection, TLS failure, and application failure.

## Useful Fields

- `role`: client, server, proxy, gateway, tunnel, parser-adapter, websocket.
- `phase`: accept, connect, tls_handshake, read_headers, read_body, write_headers, write_body, upgrade, websocket_read, websocket_write, shutdown.
- `remote_endpoint` or a privacy-preserving peer identifier.
- `http_version`, `method`, target class or route name, status code.
- `keep_alive`, `connection_close`, `upgrade_requested`, `upgrade_accepted`.
- `bytes_read`, `bytes_written`, `header_bytes`, `body_bytes`.
- `body_limit`, `header_limit`, `message_limit`, `queue_depth`.
- `close_reason`, `error_category`, `error_code`, `parser_reject_reason`.

## Metrics

- Accepted connections, active sessions, and closed sessions by reason.
- Parser rejects by reason.
- Header limit, body limit, and WebSocket message limit failures.
- Timeout counts by phase.
- Read and write latency by phase.
- Outbound queue depth and dropped/coalesced messages.
- Keep-alive reuse count and pipelined request count if supported.
- TLS handshake failures by reason class.

## Trace Events

- Session start and end.
- Protocol phase transitions.
- Header complete, body complete, response queued, response flushed.
- Upgrade accepted or rejected.
- WebSocket close initiated, received, and completed.
- Timeout armed, canceled, and fired.

## Redaction Checklist

- Never log authorization credentials, cookies, raw tokens, private keys, or full bodies by default.
- Scrub CR/LF from log fields derived from headers or targets to avoid log injection.
- Consider hashing high-cardinality identifiers before metrics labels.
- Use route names or target classes instead of full URLs when query strings may contain secrets.

## Debug Mode Escalation

If raw wire bytes are needed, make capture opt-in, scoped, time-limited, and safe for the environment. Prefer reproducing with local fixtures over capturing production traffic.