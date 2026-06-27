---
name: boost-beast
description: 'Use when: designing, implementing, reviewing, or debugging Boost.Beast, beast::http, websocket, HTTP/1.1, parser, serializer, flat_buffer, tcp_stream, ssl_stream, async_read, async_write, body limits, keep-alive, chunked encoding, pipelining, upgrades, or protocol adapter code.'
argument-hint: 'Describe the Beast design, bug, review target, parser behavior, HTTP/WebSocket flow, or code you want help with.'
user-invocable: true
---

# Boost.Beast Skill

Use this skill for C++ networking work that uses Boost.Beast for HTTP, WebSocket, parser/serializer handling, message bodies, stream wrappers, TLS integration, protocol upgrades, and protocol-facing adapters.

This skill is standalone for Beast-specific design and review. Do not assume any particular repository layout, framework, request type, response type, build system, or house style. Code examples assume Boost.Asio coroutine familiarity with `co_await`, `use_awaitable`, and `as_tuple`; executor and Asio coroutine foundations, as well as pure C++20 coroutine language mechanics, are out of scope here. Inspect the local codebase first when editing, then apply these Beast-specific rules through the codebase's existing conventions.

## Routing

- **WORKFLOW SKILL**: use for Boost.Beast HTTP/WebSocket design, implementation, review, debugging, hardening, and test-planning tasks.
- INVOKES: inspect local Beast usage first for implementation or review; load reference packs only when the task needs their detail.
- FOR SINGLE OPERATIONS: answer narrow Beast questions directly after identifying the protocol role, stream stack, parser/serializer policy, and lifecycle risk.
- Use this skill when Beast is the protocol boundary: HTTP parsing/serialization, WebSocket upgrade and frames, Beast stream wrappers, Beast body types, or Beast-specific error/EOF behavior.
- Out of scope: tasks where the hard part is executor affinity, strands, timers, socket lifecycle, generic cancellation, or non-HTTP Asio transport flow.
- Out of scope: tasks where the hard part is custom coroutine machinery, awaiter protocol, `promise_type`, generator behavior, or scheduler-independent frame ownership.

## DO NOT USE FOR:

- Generic REST, API, browser WebSocket, or web security design with no Boost.Beast code or Beast parser behavior.
- Pure Boost.Asio executor, timer, socket, cancellation, or shutdown work where HTTP/WebSocket protocol behavior is not the hard part.
- Standalone C++ coroutine library mechanics such as custom `promise_type`, awaiters, generators, symmetric transfer, or frame allocation.

## Operating Posture

- Treat Beast as protocol infrastructure. Prioritize protocol correctness, resource limits, stream ownership, buffer lifetime, cancellation, timeout behavior, and deterministic cleanup before API polish.
- Keep Beast-specific leniency and parser details behind parser adapters. Public application objects should receive normalized, policy-checked requests rather than raw parser artifacts unless the API intentionally exposes Beast.
- Make HTTP semantics explicit: method, target, version, headers, body limits, transfer encoding, keep-alive, connection close, upgrade, and EOF handling should not be accidental side effects.
- Bound memory and queued output. Configure parser body/header limits, cap buffers and queues, and make slow-client behavior intentional.
- Preserve stream serialization rules. Do not run overlapping reads on one stream, and do not run overlapping writes unless the abstraction explicitly serializes them.
- Prefer clear ownership over clever composition. Know who owns the socket or stream, parser, serializer, buffer, timers, request/response messages, and any outstanding asynchronous operation.

## Terminology Baseline

- **Parser adapter:** The boundary that converts Beast parser/message state into public application request or response objects after policy validation.
- **Parser differential:** A disagreement between Beast and another HTTP parser, proxy, gateway, upstream server, or framework about whether input is valid, malformed, or policy-rejected.
- **Strictness gate:** The explicit validation step after Beast parsing and before public application object construction or forwarding.
- **Trusted input:** Messages from known, controlled, or verified peers whose size and shape are bounded by another layer.
- **Untrusted input:** Messages from clients, proxies, or external sources that may be malformed, oversized, slow, or intentionally ambiguous. Configure limits before reading untrusted input.
- **Close/drain/keep-alive decision:** The policy decision after rejection that determines whether to close immediately, drain bounded bytes, or safely reuse the connection.

## When To Use

- Designing an HTTP client, HTTP server, proxy, reverse proxy, WebSocket endpoint, protocol adapter, request parser, response serializer, upload/download flow, or upgrade path with Boost.Beast.
- Implementing or reviewing `boost::beast::http::async_read`, `async_write`, `parser`, `serializer`, `message`, `request`, `response`, `dynamic_body`, `string_body`, `file_body`, `buffer_body`, `flat_buffer`, `tcp_stream`, `ssl_stream`, or `websocket::stream` code.
- Debugging parse failures, unexpected EOF, stuck reads/writes, truncated responses, bad keep-alive behavior, invalid chunk handling, websocket close failures, TLS shutdown errors, buffer growth, or memory spikes.
- Hardening HTTP handling against oversized headers, oversized bodies, request smuggling, ambiguous framing, slow clients, malformed upgrades, and parser leniency mismatches.
- Planning deterministic tests for HTTP parsing, serialization, keep-alive, pipelining, chunked bodies, upgrades, close semantics, TLS, and WebSocket frames.

## Task Modes

- **Design mode:** define the protocol surface, stream model, parser/serializer policy, resource limits, connection lifecycle, timeout/cancellation behavior, and verification plan before suggesting code.
- **Implementation mode:** inspect local patterns first, then make the smallest change that preserves Beast object lifetimes, stream serialization, parser limits, error handling, and testability.
- **Review mode:** lead with correctness and security risks: parser policy gaps, unbounded buffers, lifetime bugs, overlapping operations, bad EOF handling, keep-alive mistakes, smuggling exposure, and missing tests.
- **Debug mode:** build a symptom-driven hypothesis table from observed errors, bytes on the wire, parser state, stream state, timeouts, and connection lifecycle before proposing fixes.
- **Test-planning mode:** specify deterministic tests for valid traffic, malformed traffic, limits, slow or partial I/O, disconnects, EOF, timeout, keep-alive, pipelining, upgrade, TLS, and WebSocket close paths.

## Reference Packs

Load these only when the task needs the extra detail. For broad or unclear tasks, start with [package index](./references/index.md); for a narrow task, load only the directly relevant reference.

- Use [package index](./references/index.md) to choose the smallest useful reference set for design, implementation, review, debugging, hardening, or testing tasks.
- Use [scenarios](./references/scenarios.md) when the user reports a concrete symptom, code smell, failure mode, or suspicious HTTP/WebSocket behavior.
- Use [HTTP strictness](./references/http-strictness.md) for request smuggling, framing ambiguity, parser leniency, proxy boundaries, and strictness gates.
- Use [HTTP patterns](./references/http-patterns.md) for parser setup, serializer lifetime, write queues, streaming bodies, and timeout wrappers.
- Use [WebSocket patterns](./references/websocket-patterns.md) for WebSocket write queues, message lifetime, close-aware send paths, and session patterns.
- Use [patterns](./references/patterns.md) only as a compatibility map to the split HTTP and WebSocket pattern references.
- Use [decision trees](./references/decision-trees.md) for choosing parser/message APIs, body types, close/drain/keep-alive behavior, adapter exposure, and streaming approaches.
- Use [body types](./references/body-types.md) for choosing `empty_body`, `string_body`, `dynamic_body`, `file_body`, `buffer_body`, and streaming serializers.
- Use [error mapping](./references/error-mapping.md) for translating Beast, Asio, TLS, parser, timeout, EOF, and WebSocket outcomes into application behavior.
- Use [testing](./references/testing.md) for byte-level parser fixtures, partial I/O, keep-alive, pipelining, malformed input, fuzzing, and WebSocket/TLS test recipes.
- Use [role playbooks](./references/role-playbooks.md) for server, client, proxy/gateway, parser adapter, and WebSocket endpoint decisions.
- Use [threat model](./references/threat-model.md) for request smuggling, slowloris, memory exhaustion, response splitting, proxy differentials, WebSocket flooding, and TLS truncation risks.
- Use [observability](./references/observability.md) for safe logs, metrics, traces, redaction, close reasons, queue depth, parser rejection, and timeout diagnostics.
- Use [version notes](./references/version-notes.md) for Boost.Beast API/version caveats, coroutine support, timeout behavior, parser limits, and TLS shutdown differences.
- Use [implementation checklist](./references/implementation-checklist.md) before and after making Beast code changes.
- Use [debugging](./references/debugging.md) for EOF, timeout, TLS shutdown, stuck writes, memory growth, and parser failure investigation.
- Use [review checklist](./references/review-checklist.md) for a reusable Beast review output template.

## Assets

Use these copy/paste resources when a task benefits from a stable starting point:

- Use [review templates](./assets/review-templates.md) for Beast code review, parser hardening review, WebSocket review, proxy/request-smuggling review, and test-plan prompts.
- Use [HTTP fixtures](./assets/http-fixtures.md) for raw HTTP request/response examples covering valid traffic, malformed framing, keep-alive, pipelining, and strictness edge cases.

## Procedure

1. Identify the Beast boundary: HTTP parser, HTTP serializer, request/response adapter, client session, server session, proxy bridge, WebSocket session, TLS stream, or test fixture.
2. State the protocol role: client, origin server, proxy, gateway, tunnel, WebSocket endpoint, or parser adapter. Different roles have different HTTP target, authority, connection, and upgrade rules; use [role playbooks](./references/role-playbooks.md) for role-specific details.
3. Name the stream stack and ownership model. Examples: `tcp_stream`, `net::ssl::stream<tcp_stream>` (`net` is the common alias for `boost::asio`; this is the canonical TLS stream; `beast::ssl_stream` is deprecated for new code since Boost 1.86), `websocket::stream<tcp_stream>`, or a test stream. Identify who owns the stream, buffer, parser, serializer, timer, and message objects.
4. Define operation serialization. Confirm there is at most one outstanding read per stream and that writes are awaited, queued, or otherwise serialized.
5. Define parser and serializer policy before constructing public objects. Include header limit, body limit, eager parsing, skip behavior, chunk handling, transfer encoding, keep-alive, upgrade, and close behavior.
6. Enforce resource limits at the parser or body boundary, not after the full message is already buffered.
7. Map Beast and Asio errors deliberately. Treat `http::error::end_of_stream`, `net::error::operation_aborted`, TLS shutdown codes, and WebSocket close codes according to connection state rather than as generic failures.
8. For implementation work, add or update tests at the narrowest stable seam that observes the behavior. For design, review, debugging, or test-planning work, describe the required tests and verification commands without editing files unless requested.

## HTTP Parser Guidelines

- Set `body_limit` intentionally for every parser used on untrusted input. Use `header_limit` when available or enforce equivalent header-size policy at the read boundary.
- Validate method, target, HTTP version, header syntax policy, host/authority requirements, and body expectations before passing a request to application logic.
- Treat transfer framing as security-sensitive. Reject ambiguous, conflicting, or policy-forbidden combinations such as invalid `Content-Length`, unsupported transfer codings, or bodies where the method/status forbids them.
- Decide whether parser leniency is acceptable. If strict behavior is required, normalize or reject before public request construction.
- Keep parser buffers alive until reads complete. Do not store string views into temporary Beast fields unless the backing message outlives the view.
- Handle partial messages and EOF explicitly. EOF before a complete message is usually malformed input; EOF after a complete response may be normal depending on HTTP version and connection policy.
- Trailers are version-sensitive: Boost 1.90+ `http::parser` rejects non-standard trailer fields by default. After validating the `Trailer` header, opt in on the parser instance via `parser.merge_all_trailers(true)` if non-standard trailers are required.
- For custom parsers derived from `http::basic_parser`, Boost 1.90+ routes trailer fields to a separate `on_trailer_field_impl` callback instead of `on_field_impl`; override that callback when custom trailer handling is required. See [version notes](./references/version-notes.md) for the exact behavior change and the older-release difference.

## HTTP Serializer Guidelines

- Keep the message or serializer object alive until `async_write` completes.
- Set status, version, keep-alive, content length, chunked encoding, and close behavior explicitly for generated responses.
- Use `prepare_payload()` when it matches the body type and response policy, but do not let it hide intentional streaming, chunking, or no-body semantics.
- For streaming bodies, define backpressure and lifetime rules for every buffer sequence passed to Beast.
- Do not reuse serializers after completion unless Beast's documented state model permits it for the exact type and flow.

### Serialization Cost And The Fast-Path Bypass

- `http::async_write` over a `message` can become a dominant CPU cost in a high-throughput static-response server. The cost is often diffuse across Beast's lazy `buffers_cat_view`/`buffers_suffix` composition and the `basic_fields` writer, with no single hot symbol. Measure it with profiling and a control that writes pre-formatted bytes via plain `net::async_write` (`net` aliases `boost::asio`); the delta is the serializer cost. Do not bypass Beast unless the profile shows serialization is a real bottleneck.
- `basic_fields::clear()` removes fields and invalidates existing references, but do not rely on it to release memory to the system or on stable allocation behavior for later `set`/`insert` calls. Allocation and reuse are allocator- and implementation-dependent; treat header-field storage reuse as something to profile, not assume.
- A **serialization fast path** — hand-assembling the status line, headers, and body into a reused contiguous buffer and writing it with plain `net::async_write` — can recover most of the serializer cost for the common case. It is only safe under the strict conditions below.
- **The fast path MUST be byte-identical to Beast for the chosen Boost version and message shape, or fall back.** Verify by diffing the hand-assembled bytes against a Beast `response_serializer` **oracle** over a response matrix; do not hand-write the expected bytes or generalize one observed header order to other versions, body types, or connection policies. Use documented invariants as assumptions and treat other serialized details as oracle-captured behavior.
- **The eligibility predicate is conservative: take the fast path only when ALL of these hold; otherwise fall back.** A weaker predicate that drops any condition can emit wrong framing.
  - the response is HTTP/1.1 (not HTTP/1.0 — Beast frames 1.0 differently);
  - the response has a **known `Content-Length`** that exactly matches the bytes to write (see the inverted-eligibility warning below);
  - the body is fully in memory (not streamed/chunked);
  - the method/status combination permits payload bytes: do not write payload bytes for `HEAD`, `1xx`, `204`, or `304` responses; if supporting `HEAD`, use a separate header-only fast path with oracle-verified representation headers;
  - the reason phrase is the standard one for the status (no custom reason);
  - headers come from a fixed or tightly allowlisted template with prevalidated values: no raw CR/LF, obs-fold, invalid field names, duplicate `Content-Length`, conflicting `Transfer-Encoding`, or unexpected connection-management fields;
  - there are no response trailers.
- **Inverted-eligibility warning (the easy bug):** An unknown-length HTTP/1.1 response may use **chunked** transfer encoding when `prepare_payload()` or explicit `chunked(true)` sets that framing. The fast path described here only reproduces fixed-length framing, so it is eligible **only when a matching `Content-Length` is present — NOT merely when it is absent.** Do not invert this: "no Content-Length" is a fall-back case unless a separate close-delimited or chunked fast path has its own oracle and predicate.
- **The reused buffer MUST NOT be mutated while an outstanding `async_write` references it** — rely on the same single-write-in-flight serialization that protects a reused `message`.
- Concrete framing example (HTTP/1.1, keep-alive, body `hello`, user set `Content-Length: 5`):

  ```text
  ELIGIBLE  -> HTTP/1.1 200 OK\r\nServer: X\r\nContent-Length: 5\r\n\r\nhello
  INELIGIBLE (prepared chunked response; fixed-length fast path must fall back):
               HTTP/1.1 200 OK\r\nServer: X\r\nTransfer-Encoding: chunked\r\n\r\n5\r\nhello\r\n0\r\n\r\n
  ```

- This is an optimization with a real correctness surface (hand-rolled HTTP/1.1 framing). Gate it behind the byte-identical oracle test and the conservative predicate; treat any unproven shape as fallback. Spec/design it rather than inlining it.

## WebSocket Guidelines

- Perform HTTP upgrade validation before accepting a WebSocket connection. Confirm target, host/origin policy, subprotocols, authentication state, and maximum message size.
- Configure read message limits and timeout behavior for untrusted peers.
- Serialize writes through a queue or single writer coroutine. Concurrent WebSocket writes are a common correctness bug.
- Handle close frames, ping/pong, idle timeout, and abnormal disconnects as first-class lifecycle states.
- Decide whether messages are text or binary at the boundary, and validate UTF-8 for text messages when the application requires it.

## TLS And Stream Guidelines

- Keep TLS handshake, HTTP read/write, WebSocket upgrade, and shutdown states distinct in diagnostics and error mapping.
- Treat TLS shutdown errors contextually. Some truncation or stream-short-read errors may be peer behavior, but do not suppress them where authenticated close is required.
- Do not mutate TLS context or certificate state for active streams unless the application has an explicit reload model.
- Apply timeouts to the lowest stream layer that owns I/O cancellation, and make timeout cleanup race-safe.

## Design Checklist

- The role is clear: client, server, proxy, tunnel, parser adapter, or WebSocket endpoint.
- Stream, buffer, parser, serializer, timer, and message lifetimes are explicit.
- Reads and writes on each stream are serialized according to Beast's requirements.
- Parser body and header limits are configured before reading untrusted traffic.
- Message normalization and validation occur before public application object construction.
- HTTP version, keep-alive, connection close, EOF, and upgrade semantics are deliberate.
- Backpressure is visible in write queues, streaming bodies, and WebSocket send paths.
- Error mapping distinguishes normal close, timeout, peer disconnect, malformed input, protocol rejection, TLS failure, and internal failure.
- Tests cover success, malformed input, oversize input, partial input, keep-alive, close, timeout, disconnect, and upgrade paths where relevant.

## Common Anti-Patterns

- Passing temporary messages, serializers, buffers, or body storage into asynchronous operations.
- Running multiple simultaneous reads or writes on the same stream without a documented serialization layer.
- Reading untrusted requests into unbounded `dynamic_body` or unbounded buffers.
- Applying body/header limits after the full message has already been accepted.
- Treating every EOF as an error or every EOF as normal, instead of tying it to parser and connection state.
- Letting Beast parser behavior define application security policy implicitly.
- Building public application request objects from raw headers before validating framing, limits, method, target, version, and host policy.
- Forgetting `prepare_payload()` or setting inconsistent `Content-Length`, chunked, and close semantics.
- Capturing raw `this` in asynchronous Beast handlers whose operations can outlive the object.
- Suppressing TLS, WebSocket, or HTTP protocol errors without recording enough context to debug production failures.

## Review Heuristics

- Check lifetime first: stream, buffer, parser, serializer, message, file body, and captured state must outlive outstanding operations.
- Check limits next: parser body/header limits, WebSocket message limits, flat buffer growth, write queue size, and streaming backpressure.
- Inspect framing and normalization: `Content-Length`, transfer encoding, chunking, method/body rules, response body rules, keep-alive, and close behavior.
- Look for request-smuggling exposure when code bridges Beast to another parser, proxy, upstream server, gateway, or framework request type.
- Confirm EOF and cancellation paths are state-aware and do not turn normal shutdown into noisy errors or malformed input into silent success.
- Verify tests include malformed and boundary cases, not just happy-path complete messages.

## Debug Playbook

- Capture the exact role, HTTP version, request/response bytes if safe, parser state, operation in progress, and stream close state.
- Reproduce with minimal wire input when debugging parser behavior. Prefer byte-level fixtures for malformed framing, partial messages, chunking, and EOF cases.
- Separate transport failures from protocol failures. A timeout, TLS shutdown, parser rejection, and peer close can all appear as a failed read but require different fixes.
- For hangs, identify the outstanding operation, timeout ownership, pending write queue state, and whether another read/write is already active.
- For memory growth, inspect parser limits, flat buffer consumption, body type, queued responses, WebSocket message accumulation, and slow-client behavior.

## Output Expectations

When producing substantive output, match the active task mode:

- Design: include role, stream stack, ownership/lifetime, parser/serializer policy, limits, keep-alive/close semantics, cancellation/timeout, backpressure, error mapping, and verification plan.
- Implementation: state the local patterns inspected, Beast boundary changed, lifetime and serialization decisions, parser/serializer policy, error-handling behavior, and tests run or still needed.
- Review: lead with findings ordered by severity, then summarize lifetime, operation serialization, limits, HTTP/WebSocket semantics, TLS behavior, and test-gap evidence.
- Debug: provide a hypothesis table with Symptom, Evidence to collect, Likely cause, Confirming check, and Targeted fix; end with the next minimal reproduction or logging step.
- Test planning: provide test cases with seam, setup, wire input or action, assertions, covered failure mode, and required tooling where relevant.

Keep recommendations concrete enough for a builder to implement without inventing the protocol policy or connection lifecycle.