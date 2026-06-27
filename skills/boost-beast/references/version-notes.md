# Version Notes

Use this reference when code must work across Boost.Beast or Boost.Asio versions, or when an API appears unavailable in a target environment.

## General Guidance

- Check the actual Boost version and local compile errors before assuming an API is available.
- Prefer local project compatibility patterns over introducing newer Beast APIs into an older supported version.
- When writing standalone guidance, mention the API intent and ask the builder to verify exact signatures against the target Boost release.

## Common Version-Sensitive Areas

### Parser Limits

- `body_limit` is the common first line of defense for Beast HTTP parsers.
- Header limit APIs and exact names can vary by Boost release. If unavailable, enforce equivalent aggregate header caps around parser input and public adapter construction.
- Boost.Beast 1.91 enforces an 8KB sanity limit on HTTP chunk headers. Untrusted-input servers on older releases should enforce an equivalent cap themselves rather than assume the parser bounds chunk-extension size.

### Coroutine Support

- `boost::asio::awaitable`, `use_awaitable`, `as_tuple`, and cancellation behavior depend on the Boost.Asio version and compiler mode.
- Older codebases may use callbacks, `spawn`/stackful coroutines, or custom composed operations. Match the existing style unless the task explicitly asks for migration.

### Timeout Behavior

- `beast::tcp_stream` provides Beast-style timeout helpers in many modern Beast versions.
- Streams wrapped in TLS or WebSocket may require applying expiry to the lowest layer. Verify the correct `get_lowest_layer` usage for the stream stack.
- External timers must handle success/timeout races explicitly.

### TLS Shutdown

- OpenSSL and Asio behavior around stream truncation and shutdown errors can vary across versions and peer ecosystems.
- Decide whether truncation is acceptable based on the security boundary and transfer semantics, not only on what a sample server happens to do.
- `beast::ssl_stream` and `beast::flat_stream` are documented as deprecated since Boost 1.86; `net::ssl::stream` (`boost::asio::ssl::stream`) is canonical in current snippets and examples. New code should prefer `net::ssl::stream`; existing `ssl_stream` usage still works but should not be introduced fresh.

### WebSocket Options

- Timeout and decorator APIs exist in common Beast versions, but signatures and defaults may vary.
- Always verify message limit, close, ping/pong, and timeout configuration against the target release.

### Body Types

- `file_body` availability and platform behavior may depend on the target Boost release and filesystem environment.
- Custom body concepts are powerful but version-sensitive; use minimal documented interfaces and tests.

### HTTP Trailers

- As of Boost 1.90, `http::parser` **rejects non-standard trailer fields by default** and merges only well-known trailer fields unless configured otherwise. Code that relied on a non-standard trailer field must validate the `Trailer` header in the header section and then opt in via `http::parser::merge_all_trailers(true)` before the trailer section is parsed. On Boost < 1.90 this rejection does not happen — verify the target version before relying on either behavior.
- Also as of Boost 1.90, custom parsers derived from `http::basic_parser` must override the new virtual `on_trailer_field_impl` (trailer fields no longer reach `on_field_impl`). A custom parser written against an older Beast will silently miss trailer fields on 1.90+.

### Field Lookup And Constants

- `http::basic_fields::contains` exists from Boost 1.90; on older releases use `find(...) != end()`.
- The `http::field` enum gains constants over time (for header names such as `HTTP2-Settings` in 1.91); some non-protocol constants were removed in 1.90. Do not assume a given enumerator exists across versions — fall back to the string-literal field name.

### Response Generation: `message_generator`

- From Boost 1.81, `http::message_generator` provides a type-erased way to write a response of any body type with a single `async_write(stream, std::move(generator))`, avoiding templating the write path on the body type. Prefer it over hand-managing `serializer` lifetime when the response body type varies; it is unavailable on older releases.

## Review Prompt

When version compatibility matters, ask:

- What Boost version is compiled in CI and production?
- Are examples copied from documentation for the same version?
- Are coroutine APIs available under the selected C++ standard?
- Are timeout and cancellation semantics tested on the actual target platform?