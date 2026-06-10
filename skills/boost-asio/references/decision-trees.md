# Boost.Asio Decision Trees

Use these compact trees when design choices are unclear. Prefer existing project conventions when they already solve the same problem safely.

## Strand, Mutex, Or Single Executor

- Use a single-threaded `io_context` or executor only when all handlers that touch the state are guaranteed to run serially on one event-loop thread.
- Use a strand when multiple I/O threads may run handlers that touch the same object state.
- Use a mutex when state must be shared across independent executors or non-Asio threads.
- Use atomics only for small independent values with simple invariants.
- Do not hold a mutex across `co_await`, callbacks into user code, or blocking operations.

## Coroutines Or Callbacks

- Use coroutines for new linear async flows: accept loops, session read/write loops, handshake sequences, and request pipelines.
- Use callbacks when integrating with an existing callback-heavy codebase or implementing low-level composed operations that match local style.
- Keep callback APIs if public compatibility matters more than internal readability.
- Avoid mixing callbacks and coroutines in the same operation unless there is a clear boundary and ownership model.

## Detached Or Tracked Task

- Use tracked tasks when shutdown must wait for completion, errors matter, or resource ownership is tied to task lifetime.
- Use `detached` only when another owner observes lifecycle, cancellation, and failures.
- Use a task group, session registry, or explicit join/drain mechanism for server-owned background tasks.
- Never hide important exceptions in detached coroutines.

## Cancel Operation Or Close Socket

- Cancel the specific operation when the stream can remain usable afterward and the operation supports cancellation semantics you rely on.
- Close the socket or lowest layer when timeout or protocol failure means the connection is no longer trustworthy.
- For TLS streams, decide whether graceful shutdown is required or best-effort before falling back to closing the lowest layer.
- Treat cancellation completion as part of the normal operation lifecycle.

## Use Error Codes Or Exceptions

- Use local `error_code` handling for expected transport outcomes: EOF, reset, timeout, operation canceled, connection refused.
- Use exceptions for unexpected programming/configuration failures only if the surrounding code has clear coroutine-boundary handling.
- Convert external library errors into local domain errors at module boundaries.
- Do not let raw transport errors leak into application behavior unless they are intentionally part of the public contract.

## Beast Or Raw Asio Protocol Handling

- Use Beast for HTTP/1.1, WebSocket, and HTTP serialization/parsing when its behavior matches the product security policy or can be normalized behind a parser adapter.
- Use raw Asio when implementing a small custom binary/text protocol or when complete control over framing is required.
- Put any parser behind a boundary that owns framing, limits, malformed-input policy, and public object construction.
- Add fuzz or split-input tests when parser behavior is security-sensitive.

## Graceful Or Hard Shutdown

- Use graceful shutdown when protocol correctness, data delivery, or peer experience matters and bounded deadlines exist.
- Use hard close when the peer violates protocol, exceeds limits, times out, or shutdown must be prompt.
- Always bound graceful shutdown with a timer.
- Define whether queued outbound data is drained, failed, or discarded.

## Work Guard Or Natural Drain

- Use a work guard when the event loop must stay alive while operations are being scheduled from outside the loop.
- Reset the work guard during shutdown after no new work should be admitted.
- Prefer natural drain when all work is already represented by outstanding async operations.
- If an event loop exits early, check missing work guard or missing outstanding operation ownership first.