# HTTP Strictness

Use this reference when Beast code must handle untrusted HTTP/1.x traffic, bridge to another parser, act as a proxy/gateway, or enforce behavior stricter than Beast's default parser acceptance.

## Core Rule

Define the accepted wire grammar and framing policy before creating public application request objects. Beast can parse HTTP; the application must still decide which parsed messages are acceptable for its role.

For threat context, use [threat model](./threat-model.md). For test fixtures covering these cases, use [testing](./testing.md) and [HTTP fixtures](../assets/http-fixtures.md).

## Validation Order

1. Configure parser limits before reading: body limit, header limit when available, and any buffer cap around the read loop.
2. Read through Beast into a parser or message object whose lifetime is explicit.
3. Validate framing, method/status/body rules, target form, host/authority, version, connection options, upgrade state, and header policy.
4. Normalize into the public request/response type only after the message passes policy.
5. On rejection, drain or close according to the connection policy. Do not keep a connection alive after ambiguous framing unless the policy proves hidden bytes cannot poison the next message.

## Request-Smuggling Checklist

- Reject or explicitly define handling for `Transfer-Encoding` plus `Content-Length` on inbound requests.
- Reject duplicate `Content-Length` unless all values are byte-for-byte identical and the selected policy permits duplicates.
- Reject invalid, signed, overflowing, comma-joined, or whitespace-mutated `Content-Length` values.
- Reject unsupported transfer codings. For HTTP/1.1 requests, only `chunked` is generally expected as the final transfer coding.
- Reject malformed chunk sizes, invalid chunk extensions when unsupported, missing chunk terminators, and trailers that violate local policy.
- Reject obsolete line folding if the surrounding system requires strict HTTP parsing.
- Reject whitespace before the colon in header field names and other known parser-differential syntax if bridging to another HTTP implementation.
- Enforce a single selected interpretation before proxying or translating a message.

## Target And Authority Policy

- Origin servers usually accept origin-form targets such as `/path?query`; proxies may also accept absolute-form targets.
- `CONNECT` uses authority-form and has special tunnel semantics. Do not pass it through normal request-body handling by accident.
- Asterisk-form is only valid for specific server-wide requests such as `OPTIONS *`.
- HTTP/1.1 requests normally require `Host`. If HTTP/1.0 is accepted, define whether missing `Host` is allowed.
- Normalize or reject userinfo, invalid percent-encoding, path traversal forms, and scheme/authority mismatches at the application boundary.

## Header Policy

- Decide whether header names are case-normalized in public objects.
- Define duplicate-header behavior for security-sensitive fields such as `Host`, `Content-Length`, `Transfer-Encoding`, `Connection`, `Upgrade`, `Authorization`, and forwarding headers.
- Strip or reject hop-by-hop headers at proxy boundaries according to the `Connection` header and local policy.
- Set maximum count, maximum aggregate size, and maximum value length for headers accepted from untrusted peers.

## Body Semantics

- Some methods and response statuses have special body rules. `HEAD`, `CONNECT`, `1xx`, `204`, and `304` need explicit treatment.
- Do not infer application meaning from the presence of a body alone. Validate method, status, content type, and declared length against the endpoint contract.
- Reject bodies on endpoints that do not accept them if hidden bytes could affect keep-alive or pipelined traffic.

## Proxy And Adapter Boundaries

- Treat parser-to-parser bridges as hostile until proven equivalent. Beast, upstream servers, reverse proxies, and application frameworks may disagree on malformed framing.
- Normalize once, then serialize from normalized state. Avoid forwarding raw header blocks after policy decisions were made on parsed fields.
- On rejection caused by ambiguous framing, prefer closing the connection over attempting to recover pipelined traffic.
- Preserve enough diagnostics to explain what was rejected without logging credentials or full bodies.

## Acceptance Tests

- `Transfer-Encoding: chunked` plus `Content-Length` is rejected or handled exactly as documented.
- Conflicting duplicate `Content-Length` is rejected.
- Oversized headers fail before public request construction.
- Oversized bodies fail before full buffering.
- Malformed chunked requests close or reject deterministically.
- A rejected first request on a keep-alive connection cannot let hidden bytes become a second accepted request.
- Proxy/gateway paths strip hop-by-hop headers and do not forward raw ambiguous framing.