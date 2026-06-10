# C++ Coroutine Decision Trees

Use this reference before designing or changing coroutine abstractions.

## Task Or Generator

- Use a task-like abstraction when the coroutine represents one eventual result or completion.
- Use a generator-like abstraction when the coroutine yields a sequence pulled by a consumer.
- Use a callback or iterator instead of a coroutine if local style, performance constraints, or toolchain support make coroutine behavior harder to verify.

## Lazy Or Eager Start

- Use lazy start when the caller should control execution by awaiting, iterating, or explicitly starting the coroutine.
- Use eager start when starting work immediately is part of the API contract.
- Avoid accidental eager start when construction can throw, allocate, enqueue work, or capture references before the caller can attach cancellation or continuations.

## Owning Or Borrowed Handle

- Use an owning coroutine object when public code receives a coroutine handle or task-like object.
- Use borrowed handles only inside tightly scoped awaiter/continuation code where owner lifetime is proven.
- Avoid storing raw `std::coroutine_handle<>` in callbacks unless cancellation or destruction unregisters that callback first. Use [interoperability](./interoperability.md) for shared-state callback adapter guidance.

## Exception Model

- Store and rethrow exceptions from `await_resume` when callers expect normal C++ exception propagation.
- Convert exceptions into result types when the local API is error-code or `expected` based.
- Terminate only for invariant violations or APIs that explicitly cannot report errors.

## Exception Storage Decision

| Exception model | Use when | Implementation | Observable path |
|---|---|---|---|
| Store and rethrow | Caller expects normal C++ exception propagation | `unhandled_exception()` stores `std::current_exception()`; `await_resume()` rethrows | Exceptions propagate naturally to caller |
| Translate to result type | Local API is `std::expected<T, E>` or error-code based | `unhandled_exception()` translates to an error; `await_resume()` returns the result type | Caller reads the result type |
| Terminate | Invariant violations or APIs that explicitly cannot report errors | `unhandled_exception()` calls `std::terminate()` or asserts | Unobserved by normal caller; document in API contract |

Exception storage without an `await_resume` rethrow or result-type publication is a bug.

## Cancellation Model

- Use cooperative cancellation when awaited operations can observe cancellation tokens or stop sources.
- Use early destruction only when destroying the frame cannot leave external operations with dangling handles.
- Use explicit cancel-and-join semantics when external callbacks or operations may still complete later.

## Scheduler Strategy

- Resume inline only when reentrancy is safe and documented.
- Resume through a scheduler or executor when thread affinity, fairness, or stack-depth control matters.
- Preserve third-party library thread-affinity rules when adapting library awaitables.

## Build Or Reuse

- Reuse the local task, generator, executor, or cancellation abstraction when one exists.
- Build a new coroutine return type only when ownership, result, cancellation, and scheduler behavior cannot be expressed by existing local types.