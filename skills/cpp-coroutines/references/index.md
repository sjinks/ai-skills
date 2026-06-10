# C++ Coroutines Package Index

Use this map to load the smallest useful part of the C++ coroutines skill package. Start with the main `SKILL.md`; load these files only when the task needs the detail. If the user describes a concrete symptom, failed test, or suspicious pattern, start with [scenarios](./scenarios.md).

## Quick Routing

| Task | Load first | Then load when needed |
|---|---|---|
| Investigate a concrete coroutine symptom | [scenarios](./scenarios.md) | Scenario-specific references from the table |
| Understand coroutine mechanics | [concepts](./concepts.md) | [patterns](./patterns.md) |
| Choose an abstraction | [decision trees](./decision-trees.md) | [concepts](./concepts.md), [interoperability](./interoperability.md) |
| Implement a task, awaiter, or generator | [patterns](./patterns.md) | [examples](./examples.md), [testing](./testing.md), [review checklist](./review-checklist.md) |
| Review coroutine code | [review checklist](./review-checklist.md) | [review templates](../assets/review-templates.md), [concepts](./concepts.md), [debugging](./debugging.md) |
| Debug coroutine lifetime or resume bugs | [debugging](./debugging.md) | [concepts](./concepts.md), [testing](./testing.md) |
| Plan tests | [testing](./testing.md) | [patterns](./patterns.md), [debugging](./debugging.md) |
| Bridge to libraries | [interoperability](./interoperability.md) | Boost.Asio skill when async I/O/executors are involved |
| Investigate frame size or allocation overhead | [performance](./performance.md) | [concepts](./concepts.md), [interoperability](./interoperability.md) |

## Overlap Rules

- Use [concepts](./concepts.md) for language mechanics; use [patterns](./patterns.md) for implementation shapes.
- Use [scenarios](./scenarios.md) when the starting point is observed bad behavior rather than planned design.
- Use [decision trees](./decision-trees.md) before writing a new coroutine abstraction.
- Use [examples](./examples.md) only after the ownership and cancellation model is chosen; the examples are guarded sketches, not a complete library.
- Use [interoperability](./interoperability.md) when adapting callbacks, futures, Boost.Asio, senders/receivers, or third-party coroutine libraries.
- Use [debugging](./debugging.md) when the starting point is a concrete symptom rather than a planned design.
- Use [performance](./performance.md) only after correctness and lifetime are understood.

## Terminology

- **Coroutine frame:** Compiler-created storage for coroutine state.
- **Promise type:** The type that controls coroutine creation, result publication, exception handling, suspension policy, and returned coroutine object.
- **Coroutine handle:** A `std::coroutine_handle<>` that can resume, destroy, or inspect a coroutine frame according to its promise type.
- **Awaiter:** The object used by `co_await` after `operator co_await` resolution, with `await_ready`, `await_suspend`, and `await_resume`.
- **Awaiter lifetime:** The interval during which an awaiter object must remain accessible: from `await_suspend()` until `await_resume()` completes or throws.
- **Owning coroutine type:** A return object such as `task<T>` or `generator<T>` that owns or shares responsibility for destroying the coroutine frame.
- **Borrowed handle:** A `std::coroutine_handle<>` used temporarily where the owner's lifetime is proven by construction.
- **Detached coroutine:** A coroutine whose completion, exceptions, cancellation, and lifetime are not joined by the caller. Treat detachment as a design decision, not a convenience default.