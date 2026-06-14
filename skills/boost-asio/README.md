# boost-asio

> Use when: designing, implementing, reviewing, or debugging Boost.Asio, asio, async I/O, boost::asio::awaitable, co_spawn, io_context, executor, strand, cancellation, timer, socket, TLS, backpressure, or thread-pool code.

This skill is aimed at Boost.Asio networking and concurrency work where executor affinity, operation lifetime, cancellation, timeout behavior, backpressure, and deterministic shutdown matter.

It helps an assistant:

- distinguish Asio execution, transport, and cancellation concerns from Beast protocol policy and generic C++ coroutine mechanics
- design or review accept loops, socket sessions, timers, write queues, TLS streams, `co_spawn` flows, strands, thread pools, and shutdown models
- identify common async bugs such as raw `this` captures, stack-buffer lifetime, overlapping stream operations, unobserved detached coroutine failures, timeout races, and unbounded queues
- route to focused references for patterns, debugging, testing, observability, Beast/TLS integration, and migration work

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- [`references/`](references/) — extended workflow and reference material.
