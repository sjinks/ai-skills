# Body Types

Use this reference when choosing or reviewing Beast message body types.

## Decision Table

| Body type | Good for | Watch for |
|---|---|---|
| `http::empty_body` | Requests or responses that must not carry a body | Do not use for methods/statuses where a body is required later |
| `http::string_body` | Small text payloads, simple APIs, tests | Copies data into memory; not suitable for large or untrusted bodies without limits |
| `http::dynamic_body` | Moderate unknown-size data when buffering is acceptable | Can grow memory quickly; always set parser limits and consume buffers intentionally |
| `http::file_body` | Serving or receiving files with filesystem-backed storage | File lifetime, path policy, partial sends, platform errors, and blocking file operations |
| `http::buffer_body` | Incremental streaming with caller-owned buffers | Buffer lifetime and `more` semantics are easy to get wrong |
| Serializer plus custom body | Advanced streaming, generated output, backpressure-sensitive flows | More code surface; requires tests for partial writes and cancellation |

## Selection Questions

- Is the body allowed by HTTP semantics for this method or status?
- Is the payload size known before sending?
- Can the payload be fully buffered safely?
- Who owns the backing storage during `async_read`, `async_write`, or `async_write_some`?
- Where is backpressure applied if the peer reads slowly?
- What happens on cancellation or peer disconnect halfway through the body?

## Inbound Request Guidance

- Use `string_body` only when the maximum accepted body is small and enforced by the parser.
- Use `dynamic_body` only with clear memory caps and tests for cap enforcement.
- Use file or streaming approaches for large uploads; do not let untrusted bodies accumulate in RAM by default.
- Validate content type and endpoint body policy after parsing headers and before expensive body handling when the design allows header-first decisions.

## Outbound Response Guidance

- Use `empty_body` for `204`, `304`, most `1xx`, and normal responses to `HEAD` where only headers should be sent.
- Use `string_body` for small generated bodies where `prepare_payload()` can safely set `Content-Length`.
- Use `file_body` or streaming serializers for large downloads.
- Use chunked encoding only when the protocol role and clients support it; test intermediaries if a proxy or gateway is involved.

## Review Smells

- `dynamic_body` appears on untrusted input with no `body_limit`.
- `string_body` is used for arbitrary uploads.
- `buffer_body` references temporary storage.
- `prepare_payload()` is used on responses with intentionally absent bodies.
- Large file open/read work happens on the I/O executor without an offload or pre-open strategy.