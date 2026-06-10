# Boost.Asio Package Index

Use this map to load the smallest useful part of the Boost.Asio skill package. Start with the main `SKILL.md`; load these files only when the task needs the detail. If the user describes a concrete symptom, suspicious pattern, or failure mode, start with [debugging](./debugging.md) before choosing task-oriented references.

## Quick Routing

| Task | Load first | Then load when needed |
|---|---|---|
| Choose an executor, ownership, cancellation, or shutdown approach | [decision trees](./decision-trees.md) | [patterns](./patterns.md), [testing](./testing.md) |
| Implement an Asio session, loop, timer, write queue, or coroutine flow | [patterns](./patterns.md) | [examples](./examples.md), [testing](./testing.md) |
| Review Asio code | [review checklist](./review-checklist.md) | [decision trees](./decision-trees.md), [debugging](./debugging.md) |
| Debug hangs, leaks, timeout races, interleaved writes, or shutdown stalls | [debugging](./debugging.md) | [observability](./observability.md), [testing](./testing.md) |
| Plan deterministic async tests | [testing](./testing.md) | [examples](./examples.md), [debugging](./debugging.md) |
| Integrate Beast, TLS, WebSocket, or parser adapters | [Beast and TLS](./beast-and-tls.md) | Boost.Beast skill, [testing](./testing.md) |
| Add production diagnostics | [observability](./observability.md) | [debugging](./debugging.md) |
| Harden existing code or migrate sync/callback code | [hardening and migration](./hardening-and-migration.md) | [decision trees](./decision-trees.md), [patterns](./patterns.md) |

## Overlap Rules

- Use [decision trees](./decision-trees.md) to choose; use [patterns](./patterns.md) and [examples](./examples.md) to implement.
- Use [debugging](./debugging.md) when the starting point is observed behavior rather than planned design.
- Use [testing](./testing.md) for deterministic loopback tests, fake timers, cancellation checks, and sanitizer guidance.
- Use [Beast and TLS](./beast-and-tls.md) only for Asio-facing transport concerns; use the Boost.Beast skill for HTTP/WebSocket parser and serializer policy.
- Use [observability](./observability.md) after the lifecycle, cancellation, and backpressure model is understood.
- Use [hardening and migration](./hardening-and-migration.md) when improving existing callback, synchronous, or fragile async code.

## Terminology

- **Executor:** The Asio scheduling context that decides where handlers and coroutine continuations run.
- **Strand:** A serialization wrapper that prevents concurrent handler execution for shared state on a multi-threaded executor.
- **Composed operation:** A higher-level async operation built from one or more lower-level async operations with one completion result.
- **Tracked task:** A coroutine or async operation whose completion, failure, and shutdown are observed by an owner.
- **Detached task:** A coroutine whose lifecycle is not joined by the immediate caller. Use only when another owner observes completion, cancellation, and failures.
- **Backpressure:** A visible limit or await point that prevents unbounded read, write, or message accumulation.
