# Boost.Asio Debugging Playbooks

Use these playbooks to turn symptoms into targeted checks. Prefer evidence from logs, counters, outstanding operations, and minimal reproductions over broad rewrites.

## Request Or Session Hangs Forever

- Check whether an async operation is outstanding but its completion handler cannot run because the `io_context` stopped, no work guard exists, or all worker threads are blocked.
- Check whether a timer was armed but never started, canceled too early, or guards the wrong operation generation.
- Check for blocking callbacks on the I/O executor.
- Check whether a coroutine is waiting on a write queue that is full and has no consumer progress.

## Session Leaks

- Look for `shared_ptr` cycles between session, callbacks, timers, queues, and application observers.
- Confirm all timers and async operations are canceled during shutdown and disconnect.
- Verify `co_spawn(..., detached)` coroutines do not keep a `shared_ptr` alive after the server has stopped tracking the session.
- Add lifecycle logging for create, start, stop requested, close, final handler, and destructor.

## Timeout Fires After Success

- Verify success paths cancel the timer.
- Add an operation generation token and make the timer handler ignore stale generations.
- Ensure timer cancellation results, including `operation_aborted`, are treated as normal.
- Check whether the same timer is reused for multiple operations without resetting state.

## Writes Interleave Or Corrupt Output

- Check for multiple simultaneous `async_write` calls on the same socket, TLS stream, Beast stream, or WebSocket stream.
- Require a single write queue with one in-flight write.
- Confirm queued buffers own their bytes until completion.
- Check whether application code can call response/write APIs concurrently from multiple executors.

## Server Does Not Stop

- Confirm the acceptor is closed or canceled.
- Confirm work guards are reset after shutdown starts.
- Confirm sessions receive a stop signal and close their streams.
- Confirm detached coroutines are not keeping work alive forever.
- Confirm all worker threads are joined after the event loop drains.

## TSan Reports A Race

- Identify the shared variable and the executors that access it.
- If all accesses should be serialized, route them through the same strand or executor and assert that invariant.
- If cross-executor sharing is required, add a lock or atomic with a small, documented synchronization boundary.
- Avoid holding locks across callbacks, `co_await`, or user-provided handlers.

## TLS Shutdown Stalls

- Distinguish graceful TLS shutdown from TCP close; peers often disconnect without completing TLS close notify.
- Put a timeout around TLS shutdown and fall back to closing the lowest layer when the peer does not respond.
- Treat expected EOF, stream truncated, or operation cancellation according to the project protocol policy.
- Ensure shutdown does not block the I/O executor.