# Failure-Mode Scenarios

Use this reference when the user reports a concrete symptom, suspicious code pattern, failed test, or production behavior. It maps observed behavior to the smallest useful reference set.

## HTTP Parser And Smuggling

| Observed pattern | Primary risk | Load first | Then load |
|---|---|---|---|
| Accepts both `Transfer-Encoding` and `Content-Length` | Request smuggling, parser differential | [HTTP strictness](./http-strictness.md) | [threat model](./threat-model.md), [HTTP fixtures](../assets/http-fixtures.md), [testing](./testing.md) |
| Accepts conflicting duplicate `Content-Length` | Ambiguous framing, hidden bytes | [HTTP strictness](./http-strictness.md) | [HTTP fixtures](../assets/http-fixtures.md), [testing](./testing.md) |
| Reuses connection after malformed or ambiguous request rejection | Keep-alive poisoning, request smuggling | [decision trees](./decision-trees.md) | [HTTP strictness](./http-strictness.md), [threat model](./threat-model.md), [testing](./testing.md) |
| Public application request object is built before validation | Policy bypass | [implementation checklist](./implementation-checklist.md) | [HTTP strictness](./http-strictness.md), [role playbooks](./role-playbooks.md) |
| Beast parser behavior differs from an upstream or downstream parser | Parser differential | [threat model](./threat-model.md) | [HTTP strictness](./http-strictness.md), [testing](./testing.md) |

## Limits And Resource Exhaustion

| Observed pattern | Primary risk | Load first | Then load |
|---|---|---|---|
| Parser reads untrusted input without `body_limit` | Memory exhaustion | [HTTP patterns](./http-patterns.md) | [body types](./body-types.md), [threat model](./threat-model.md), [testing](./testing.md) |
| Headers can grow without an aggregate cap | Header exhaustion, slowloris amplification | [HTTP strictness](./http-strictness.md) | [threat model](./threat-model.md), [testing](./testing.md) |
| `dynamic_body` is used for arbitrary uploads | Unbounded memory growth | [body types](./body-types.md) | [HTTP patterns](./http-patterns.md), [implementation checklist](./implementation-checklist.md) |
| Outbound write or WebSocket message queue is unbounded | Slow-client memory exhaustion | [threat model](./threat-model.md) | [HTTP patterns](./http-patterns.md), [WebSocket patterns](./websocket-patterns.md), [observability](./observability.md) |

## EOF, Timeout, And Shutdown

| Observed pattern | Primary risk | Load first | Then load |
|---|---|---|---|
| EOF is always treated as success or always treated as failure | State-insensitive error mapping | [error mapping](./error-mapping.md) | [debugging](./debugging.md), [testing](./testing.md) |
| Timeout fires after operation success and corrupts state | Timeout race | [debugging](./debugging.md) | [HTTP patterns](./http-patterns.md), [error mapping](./error-mapping.md) |
| `operation_aborted` is logged as application failure during shutdown | Noisy or incorrect cancellation mapping | [error mapping](./error-mapping.md) | [debugging](./debugging.md), [observability](./observability.md) |
| TLS shutdown errors are suppressed everywhere | Truncation hidden across sensitive boundary | [error mapping](./error-mapping.md) | [threat model](./threat-model.md), [version notes](./version-notes.md) |

## WebSocket

| Observed pattern | Primary risk | Load first | Then load |
|---|---|---|---|
| Multiple application paths can call `async_write` concurrently | WebSocket stream corruption or assertion failure | [WebSocket patterns](./websocket-patterns.md) | [review checklist](./review-checklist.md), [testing](./testing.md) |
| No message size limit is configured | Memory exhaustion or flooding | [role playbooks](./role-playbooks.md) | [threat model](./threat-model.md), [testing](./testing.md) |
| Sends continue after close is requested or received | Close race, lost messages, shutdown hang | [WebSocket patterns](./websocket-patterns.md) | [debugging](./debugging.md), [error mapping](./error-mapping.md) |
| Upgrade accepts any target, origin, host, or subprotocol | Unauthorized WebSocket access | [role playbooks](./role-playbooks.md) | [HTTP strictness](./http-strictness.md), [threat model](./threat-model.md) |

## Proxy And Gateway

| Observed pattern | Primary risk | Load first | Then load |
|---|---|---|---|
| Raw inbound headers are forwarded after parsed policy decisions | Parser differential, request smuggling | [role playbooks](./role-playbooks.md) | [HTTP strictness](./http-strictness.md), [threat model](./threat-model.md) |
| Hop-by-hop headers are forwarded unchanged | Connection-state confusion | [role playbooks](./role-playbooks.md) | [HTTP strictness](./http-strictness.md), [testing](./testing.md) |
| Absolute-form and origin-form targets are accepted without role checks | Authority confusion | [HTTP strictness](./http-strictness.md) | [role playbooks](./role-playbooks.md), [HTTP fixtures](../assets/http-fixtures.md) |

## Review Output Shortcut

For review tasks that start from any scenario above:

1. Lead with findings ordered by severity.
2. For each finding, name the observed behavior, primary risk, and minimal fix direction.
3. Add targeted tests using [HTTP fixtures](../assets/http-fixtures.md) or [testing](./testing.md).
4. End with residual risk and any open questions that affect protocol policy.