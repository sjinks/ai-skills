---
name: boost-asio
description: 'Use when: designing, implementing, reviewing, or debugging Boost.Asio, asio, async I/O, boost::asio::awaitable, co_spawn, io_context, executor, strand, cancellation, timer, socket, TLS, backpressure, or thread-pool code.'
argument-hint: 'Describe the Asio design, bug, review target, or code you want help with.'
user-invocable: true
---

# Boost.Asio Skill

Use this skill for C++ networking and concurrency work built on Boost.Asio, including `boost::asio::awaitable`, composed operations, executors, strands, timers, sockets, TLS streams, and sessions. HTTP and WebSocket protocol semantics and parser/serializer policy are out of scope; transport-layer work that carries those protocols (such as WebSocket/SSE transport flows) stays in scope.

This skill focuses on Asio-specific constructs. The term `awaitable` here refers to `boost::asio::awaitable<T>`, Asio's coroutine return type. General C++20 awaitable design and the awaiter protocol are out of scope.

## Routing

- **WORKFLOW SKILL**: use for Boost.Asio design, implementation, review, debugging, and test-planning tasks.
- INVOKES: inspect local code patterns first for implementation or review; load reference packs only when the task needs their detail.
- FOR SINGLE OPERATIONS: answer narrow Asio questions directly after identifying the async boundary, executor model, and lifetime/cancellation risk.
- Use this skill for Asio execution, I/O, timers, cancellation, socket/stream lifetime, strands, and `boost::asio::awaitable` flows.
- Out of scope: tasks where the hard part is HTTP, WebSocket, parser/serializer policy, request smuggling, body limits, or Beast stream behavior.
- Out of scope: tasks where the hard part is language-level coroutine mechanics, custom `promise_type`, custom awaiters, generators, symmetric transfer, or frame ownership outside Asio.

## DO NOT USE FOR:

- Generic C++ threading, thread pools, locks, or atomics without Asio.
- HTTP, WebSocket, or parser policy questions that do not involve Asio execution or transport behavior.
- Standalone coroutine library design where `boost::asio::awaitable`, executors, sockets, timers, or Asio cancellation are not part of the task.

## Operating Posture

- Treat Asio code as concurrency-sensitive infrastructure. Prioritize lifetime, cancellation, backpressure, executor affinity, and deterministic cleanup before API polish.
- Prefer C++20 coroutine APIs for new asynchronous flows unless the surrounding codebase already uses callback-style composed operations.
- Keep low-level transport concerns below application or protocol layers. Let the transport layer own Asio objects, sockets, TLS streams, sessions, parser adapters, security limits, streaming primitives, and connection lifecycle.
- When using Boost.Beast or another protocol parser, place it behind a parser adapter. Normalize parser behavior there, enforce the strictness gate before constructing public application request objects, and keep parser-specific leniency from leaking into higher layers.
- Pure C++20 coroutine language mechanics — `promise_type`, `std::coroutine_handle`, awaiter protocol, suspension points, frame lifetime, and scheduler-agnostic coroutine design — are out of scope for this skill.

## When To Use

- Designing an Asio server, session, accept loop, connection pool, timer workflow, TLS handshake, WebSocket/SSE transport, or streaming response path.
- Implementing or reviewing `co_await`, `co_spawn`, `awaitable`, `async_*`, `use_awaitable`, `redirect_error`, `as_tuple`, cancellation slots, timers, strands, or thread-pool code.
- Debugging hangs, races, leaked sessions, premature destruction, missing cancellation, broken timeout behavior, unbounded buffering, or executor/strand misuse.
- Translating synchronous networking logic into nonblocking Asio flows.
- Choosing test seams for async behavior, timeouts, backpressure, and transport failures.

## Task Modes

- **Design mode:** produce the executor model, ownership model, cancellation model, backpressure policy, shutdown sequence, and verification plan before suggesting code.
- **Implementation mode:** inspect existing local patterns first, then implement the smallest change that preserves executor affinity, lifetimes, error handling, and testability.
- **Review mode:** lead with correctness risks: lifetime, concurrent operations on one stream, unobserved errors, timeout races, cancellation gaps, blocking calls, and unbounded buffers.
- **Debug mode:** build a hypothesis table from symptoms, outstanding operations, executor state, timers, cancellation signals, and logs before proposing fixes.
- **Test-planning mode:** select deterministic tests for success, timeout, cancellation, disconnect, shutdown, backpressure, and race-prone paths.

## Reference Packs

Load these only when the task needs the extra detail:

- Use [package index](./references/index.md) to choose the smallest useful reference set for design, implementation, review, debugging, testing, migration, or observability tasks.
- Use [patterns](./references/patterns.md) for canonical session, write queue, timer, shutdown, strand, and coroutine patterns.
- Use [debugging](./references/debugging.md) for playbooks covering hangs, leaks, timeout races, write interleaving, shutdown stalls, and TSan reports.
- Use [testing](./references/testing.md) for deterministic async test recipes, loopback integration tests, cancellation checks, and sanitizer guidance.
- Use [Beast and TLS](./references/beast-and-tls.md) for Boost.Beast, OpenSSL, TLS stream, WebSocket, and parser-adapter review notes.
- Use [examples](./references/examples.md) for compact coroutine, callback, write-queue, timeout, shutdown, and error-handling snippets.
- Use [decision trees](./references/decision-trees.md) for choosing strands, locks, coroutines, callbacks, tracked tasks, cancellation, and parser adapter boundaries.
- Use [review checklist](./references/review-checklist.md) for a reusable Asio code-review output template.
- Use [observability](./references/observability.md) for logs, metrics, traces, close reasons, and async state signals that make Asio failures diagnosable.
- Use [hardening and migration](./references/hardening-and-migration.md) for failure injection, sync-to-async migration, callback-to-coroutine migration, version notes, and glossary terms.

## Procedure

1. Identify the async boundary: accept loop, session read/write loop, composed operation, application callback, or background maintenance task.
2. Name the execution context, handler serialization mechanism, and thread model separately. State whether handlers run on a single-threaded `io_context`, a strand on a multi-threaded context, or multiple executors/threads with explicit locking or atomics.
3. Define object ownership and lifetimes before editing code. For sessions, make clear who owns the socket/stream, timers, buffers, cancellation state, and outstanding operations.
4. Define cancellation paths for normal close, timeout, peer disconnect, application abort, server shutdown, and exception unwinding.
5. Preserve backpressure. Await writes, bound queues, avoid unbounded buffering, and document any drop/coalesce policy for SSE, WebSocket, or streaming responses.
6. Keep blocking work off I/O executors. Move CPU-heavy, filesystem, DNS, certificate reload validation, or compression work to an appropriate executor or precomputed state.
7. Map errors into local result types or deterministic transport errors. Do not let `operation_aborted` look like an application failure.
8. For implementation tasks, add or update tests at the highest stable seam that observes the behavior. For design, review, debugging, or test-planning tasks, identify required test seams and verification steps without editing files unless the user requested implementation.

## Design Checklist

- Executor ownership is explicit and stable across async operations.
- Shared mutable session state is confined to one executor or protected by a strand/lock with a clear reason.
- Every outstanding async operation has a shutdown or cancellation story.
- Timers are canceled or expired deterministically, and timeout races are handled intentionally.
- Buffers live until the async operation completes; views do not outlive backing storage.
- Write paths serialize concurrent writes and bound pending output.
- Read paths enforce maximum header/body/target limits before public application request object construction.
- TLS handshakes, reads, writes, shutdown, and reload behavior do not mutate active TLS contexts unexpectedly.
- Public callbacks cannot block the I/O loop without an explicit offload strategy.
- Tests cover success, peer disconnect, timeout, cancellation, parser rejection, backpressure, and server shutdown where relevant.

## Coroutine Guidelines

- Use `co_spawn(executor, task(), detached)` only when lifecycle is owned elsewhere and failures are logged or captured. Prefer explicit completion handlers or task groups for operations that must be joined during shutdown.
- Treat Asio executors as the scheduler mechanism for Asio coroutine resumption; preserve executor affinity when adapting generic coroutine awaiters into Asio sessions.
- Use `this_coro::executor` inside coroutine flows instead of passing executors through deep call chains when it improves clarity.
- Prefer `as_tuple(use_awaitable)` or `redirect_error(use_awaitable, ec)` when expected transport errors should be handled locally without exceptions.
- Catch exceptions at coroutine boundaries where they can be mapped to session close, response error handling, or server diagnostics.
- Avoid starting multiple simultaneous reads on the same stream. Serialize writes unless the stream abstraction guarantees otherwise.

## Common Anti-Patterns

- Capturing raw `this` in async handlers when the operation can outlive the object.
- Passing stack buffers or temporary strings into async operations.
- Running concurrent reads or writes on a stream without a documented serialization guarantee.
- Detaching coroutines whose exceptions, cancellation, and shutdown completion are never observed.
- Letting timeout timers outlive the operation they guard without checking generation/state.
- Calling blocking filesystem, DNS, logging, compression, or application code on an I/O executor.
- Treating `operation_aborted` as a failure during normal shutdown or timeout cancellation.
- Building unbounded read, write, SSE, WebSocket, or message queues.

## Review Heuristics

- Look first for use-after-free risks: captures of `this`, stack buffers passed to async operations, and cancellation paths that destroy owners while operations are pending.
- Look for hidden blocking: filesystem calls, certificate parsing, logging sinks, DNS, compression, or application callbacks on I/O executors.
- Check whether all `async_*` results are observed and whether `operation_aborted` is treated as normal during shutdown.
- Check that timeouts cancel the operation they guard and cannot fire after success in a way that corrupts state.
- Check that backpressure is real, not just a comment: queue sizes, write awaiting, cancellation on slow clients, and cleanup on disconnect should be visible.
- For Beast HTTP/1.1 paths, verify strictness gates run before public application request creation and rejected pipelines do not reuse hidden bytes.

## Output Expectations

When producing substantive output, match the active task mode:

- Design: include async boundary, executor model, ownership/lifetime, cancellation/timeout, backpressure/buffering, error mapping/cleanup, and verification plan.
- Implementation: state the local pattern inspected, the async boundary changed, lifetime/cancellation/backpressure/error-handling decisions, and tests run or still needed.
- Review: lead with findings ordered by severity, then summarize executor, lifetime, cancellation/timeout, backpressure, parser/TLS, and test-gap evidence.
- Debug: provide a hypothesis table with Symptom, Evidence to collect, Likely cause, Confirming check, and Targeted fix; end with the next minimal reproduction or logging step.
- Test planning: provide deterministic test cases with seam, setup, action, assertions, failure mode, and required tool/sanitizer where relevant.

Keep recommendations concrete enough for a builder to implement without inventing the concurrency model.