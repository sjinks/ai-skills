# Decision Trees

Use this reference when a Beast task needs quick routing from a design question to the right implementation shape.

## Parser API Choice

Question: Do you need to inspect headers before committing to body handling?

- Yes: use `http::request_parser` or `http::response_parser`, set limits, read headers first if the surrounding flow supports it, then decide whether and how to read the body.
- No: `http::async_read` into a full message can be acceptable for small, trusted, bounded messages.

Question: Is the peer untrusted?

- Yes: use parser APIs with explicit limits and policy validation before public object construction.
- No: still set limits unless the transport is fully internal and bounded by another layer.

Question: Is a strictness gate required beyond Beast defaults?

- Yes: parse with Beast, then run an explicit strictness gate before adaptation or forwarding.
- No: document which leniency is accepted and why.

## Body Type Choice

Question: Must the message have no body?

- Yes: use `http::empty_body` and verify no-body semantics for the method or status.

Question: Is the full payload small and bounded?

- Yes: `http::string_body` is usually simplest for text-like payloads.

Question: Is the full payload unknown-size but buffering is acceptable under a hard limit?

- Yes: `http::dynamic_body` with parser limits and buffer accounting can fit.

Question: Is the payload large or produced incrementally?

- Yes: use `file_body`, `buffer_body`, custom body, or serializer-driven streaming with explicit backpressure.

## Close, Drain, Or Keep Alive After Rejection

Question: Was framing ambiguous, malformed, oversized, or parser-differential-sensitive?

- Yes: close the connection. Hidden bytes can poison keep-alive or pipelined requests.

Question: Was the message well-framed but rejected by application policy, and is the full body already consumed or intentionally skipped safely?

- Yes: keeping the connection alive may be acceptable if tests prove the next message starts cleanly.

Question: Is the body large, slow, or attacker-controlled?

- Yes: avoid draining by default. Close unless a product requirement demands reuse and the drain policy is bounded by size and time.

## Beast Types In Public APIs

Question: Is the surrounding library explicitly Beast-based?

- Yes: exposing Beast types may be acceptable if the API documents ownership, lifetime, and version coupling.

Question: Is Beast an implementation detail behind an application framework or transport adapter?

- Yes: hide Beast types and expose normalized request/response models or result types.

Question: Do public objects contain string views into Beast storage?

- Yes: either carry the backing storage with the public object or copy the data.

## HTTP Streaming Choice

Question: Is the data one-way server-to-client and text/event-like?

- Consider SSE or chunked HTTP streaming if browser/client compatibility fits.

Question: Does the application need bidirectional messages?

- Consider WebSocket, with explicit message size, close, ping/pong, and single-writer policy.

Question: Does the application need large file transfer?

- Prefer `file_body` or streaming serializers over fully buffered bodies.

## Timeout Ownership

Question: Does the stream stack include `tcp_stream` or a Beast lowest layer with expiry support?

- Yes: apply phase timeouts to the lowest layer and reset them between phases as appropriate.

Question: Is timeout handled by an external timer or composed operation?

- Ensure the timer cancels the active operation, cannot corrupt state after success, and maps cancellation as local timeout rather than peer failure.