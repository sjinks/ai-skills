# Boost.Asio Patterns

Use these patterns as review and implementation templates. Prefer the local codebase style when it already has a correct equivalent.

## Session Lifetime

- A session object owns the socket or stream, protocol buffers, timers, cancellation state, and write queue.
- If callback-style operations can outlive the initiating call, own the session with `std::shared_ptr` and capture `shared_from_this()` in handlers.
- If coroutine-style operations own the session through a top-level `co_spawn`, keep the owning `shared_ptr` alive for the whole coroutine and make shutdown completion observable.
- Avoid mixed ownership where the accept loop, protocol layer, and application layer can each destroy the same session.

## Read Loop

- Start at most one read on a stream at a time unless the stream abstraction explicitly supports concurrent reads.
- Keep read buffers as session members or stable heap objects that outlive the async operation.
- Enforce protocol limits while reading, before constructing higher-level application objects.
- On peer disconnect, cancel timers, release buffered state, stop scheduling reads, and treat expected EOF/reset according to protocol semantics.

## Serialized Write Queue

- Treat writes as a single-lane resource for TCP, TLS, Beast HTTP, and WebSocket streams unless documented otherwise.
- Append outbound messages to a bounded queue and start a write only when no write is in flight.
- Complete or cancel the active write before starting the next queued write.
- Define a slow-client policy: wait, bound-and-close, drop/coalesce, or backpressure the producer.
- Never pass views into queued messages unless the backing storage is owned by the queue entry.

## Timeout Pairing

- Pair each timeout with the specific operation it guards: handshake, header read, body read, write, idle, or shutdown.
- Cancel the timer after operation success and make the timer handler check whether it still owns the current operation generation.
- On timeout, cancel or close the underlying stream and let the operation complete through its normal cancellation path.
- Avoid independent timeout handlers that mutate session state after the guarded operation has already advanced.

## Shutdown Sequence

1. Stop accepting new work.
2. Signal sessions to stop producing new reads/writes.
3. Cancel timers and outstanding operations.
4. Close or shutdown sockets/TLS streams according to protocol needs.
5. Drain or fail bounded queues deterministically.
6. Join worker threads or task groups.
7. Assert no sessions, timers, or work guards remain unexpectedly alive.

## Strand And Executor Choice

- Use a single-threaded executor when all related state can live on one event loop.
- Use a strand when multiple worker threads may run handlers that touch the same session state.
- Use locks only when state must be shared across independent executors; keep locked regions small and never hold locks across `co_await` or callbacks into user code.
- Record which executor owns each object that starts asynchronous operations.

## Coroutine Boundaries

- Put exception handling at top-level coroutine boundaries such as session `run()`, accept loop, and background maintenance tasks.
- Prefer local `error_code` handling for expected transport outcomes: EOF, reset, timeout cancellation, and shutdown.
- Use `co_spawn` with `detached` only when another owner observes lifecycle and failure.
- Make server shutdown wait for important coroutines or explicitly document fire-and-forget behavior.