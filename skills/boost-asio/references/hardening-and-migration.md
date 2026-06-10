# Boost.Asio Hardening And Migration

Use this reference for failure injection, migration planning, version gotchas, and terminology checks. It is intentionally compact so it can support implementation, review, and debugging tasks without becoming a second manual.

## Failure Injection Scenarios

- Peer closes before handshake completes.
- Peer closes mid-read after a partial frame or partial application message.
- Peer stops reading while the server writes enough data to fill the outbound queue.
- Timer fires at the same time the guarded operation completes successfully.
- Server shutdown starts while accept, handshake, read, write, and timer operations are outstanding.
- TLS peer omits `close_notify` or drops TCP during shutdown.
- Parser receives malformed input split across byte-by-byte reads.
- Resolver, connect, or TLS handshake fails with a real error code rather than cancellation.
- Application callback throws or blocks longer than the operation deadline.
- Work guard is reset while external code can still schedule work.

For each scenario, define the expected close reason, cleanup behavior, observable logs/counters, and test seam before changing implementation.

## Migration: Synchronous To Async

1. Identify blocking calls: accept, connect, resolve, read, write, TLS handshake, shutdown, filesystem, logging, compression, and application callbacks.
2. Choose the executor model before changing control flow.
3. Replace one blocking boundary at a time with an async operation and preserve the old error behavior in tests.
4. Move buffers and state from stack scope to session-owned storage when operations can outlive the initiating function.
5. Add cancellation and timeout handling at the same time as each async operation.
6. Add backpressure before exposing async writes to producers.

## Migration: Callbacks To Coroutines

1. Keep the external behavior and public API stable unless the task explicitly changes it.
2. Convert one operation chain at a time: accept loop, handshake, read loop, write loop, or shutdown.
3. Replace callback captures with coroutine-owned state or session-owned fields.
4. Convert expected transport errors to local `error_code` handling through `as_tuple(use_awaitable)` or equivalent patterns.
5. Put exception handling at top-level coroutine boundaries.
6. Keep shutdown observable; do not turn tracked callback work into untracked detached coroutines.

## Migration: Unbounded Writes To Bounded Queues

1. Identify all producers that can enqueue outbound data.
2. Define the queue bound in messages, bytes, or both.
3. Define the slow-client policy: backpressure producer, reject, drop, coalesce, or close.
4. Ensure each queue entry owns its bytes until completion.
5. Serialize writes through one in-flight write operation.
6. Notify producers when the session closes or queued data is rejected.

## Version And Dependency Notes

- Boost.Asio and standalone Asio have similar concepts but different namespaces, integration defaults, and release cadence. Match the project dependency choice before writing examples or fixes.
- Coroutine support depends on compiler, standard library, and Boost/Asio version. Verify local support for `awaitable`, `use_awaitable`, `co_spawn`, `this_coro::executor`, and cancellation features before relying on them.
- Operation cancellation support varies by operation, platform, and object type. Do not assume every async operation supports fine-grained cancellation.
- Beast operations have stream-specific serialization requirements. Avoid concurrent reads or writes unless the Beast abstraction explicitly permits the pattern.
- OpenSSL/TLS shutdown behavior can differ across peer implementations. Bound graceful shutdown with a timer and document fallback close behavior.
- Resolver and DNS behavior may involve blocking system facilities depending on platform and configuration; verify before placing resolver work on latency-sensitive executors.

## Glossary

- **Executor:** The execution context or handle that determines where completion handlers run.
- **Strand:** An executor adapter that serializes handler execution for shared state without requiring one OS thread.
- **Work guard:** An object that keeps an event loop alive while work may still be scheduled.
- **Initiating function:** The function that starts an async operation, such as `async_read_some` or `async_write`.
- **Completion handler:** The callback invoked when an async operation completes.
- **Composed operation:** An async operation built from multiple lower-level async operations but exposed as one logical operation.
- **Outstanding operation:** An async operation that has been started and has not completed yet.
- **Cancellation slot:** A mechanism for associating cancellation requests with an operation or handler.
- **Lowest layer:** The underlying transport object beneath wrappers such as TLS or Beast streams.
- **Backpressure:** A bounded mechanism that prevents producers from generating unbounded pending work when consumers or peers are slow.