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

### WebSocket Options

- Timeout and decorator APIs exist in common Beast versions, but signatures and defaults may vary.
- Always verify message limit, close, ping/pong, and timeout configuration against the target release.

### Body Types

- `file_body` availability and platform behavior may depend on the target Boost release and filesystem environment.
- Custom body concepts are powerful but version-sensitive; use minimal documented interfaces and tests.

## Review Prompt

When version compatibility matters, ask:

- What Boost version is compiled in CI and production?
- Are examples copied from documentation for the same version?
- Are coroutine APIs available under the selected C++ standard?
- Are timeout and cancellation semantics tested on the actual target platform?