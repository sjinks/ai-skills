# Boost.Asio Testing Recipes

Use deterministic async tests. Avoid sleeps as assertions; prefer event-loop progress, explicit synchronization, deadlines, and loopback peers.

## Unit Tests For Composed Operations

- Test success and every expected error branch with controlled completion handlers or test doubles.
- Verify completion is called exactly once.
- Verify buffers and user callbacks remain alive until completion and are released afterward.
- Verify cancellation completes promptly with the expected result.

## Event Loop Control

- Use a local `io_context` or test executor when the behavior fits in-process.
- Use `run()`, `run_one()`, `poll()`, and `restart()` deliberately; assert when no more progress is expected.
- Keep `executor_work_guard` lifetime explicit so tests do not pass because the event loop exits early.
- Prefer condition variables, promises, channels, or test hooks over arbitrary sleep intervals.

## Loopback Integration Tests

- Use localhost sockets or connected socket pairs where supported.
- Exercise accept, handshake, read, write, peer disconnect, timeout, and shutdown behavior through real Asio operations.
- Force partial reads/writes where protocol framing or buffering matters.
- Test slow-client behavior with bounded writes and explicit backpressure expectations.

## Timeout And Cancellation Tests

- A deadline may be used as a fail-fast guard or as the behavior under test, but not as the observation mechanism. Tests should wait for explicit completion signals, test hooks, loopback peer events, fake-clock/test-executor advancement, or bounded `io_context` progress; do not use `sleep_for` to create the condition being asserted.
- Test operation success before timeout, timeout before success, cancellation before completion, and cancellation racing with completion.
- Assert stale timers cannot mutate advanced session state.
- Treat `operation_aborted` as expected when canceling timers or operations during shutdown.
- Keep test deadlines short but deterministic; avoid depending on wall-clock sleeps for correctness.

## Backpressure Tests

- Fill write queues to the configured bound and assert the selected policy: wait, close, reject, drop, or coalesce.
- Verify queued buffers retain ownership until their writes complete.
- Verify slow peers cannot produce unbounded memory growth.
- Verify producers observe cancellation or rejection when the connection closes.

## Sanitizers And Race Tools

- Run ASan and UBSan for lifetime, buffer, and undefined-behavior risks.
- Run TSan for session lifecycle, shared counters, connection registries, timeout state, write queues, and shutdown paths.
- Treat sanitizer suppressions as exceptional and document scope, owner, rationale, and revisit condition.
- For parser or protocol adapters, add fuzz tests with persisted regression corpora when input grammar is complex or security-sensitive.