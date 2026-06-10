# C++ Coroutine Concepts

Use this reference for language-level mechanics before applying a library-specific coroutine abstraction.

## Transformation Model

When a function contains `co_await`, `co_yield`, or `co_return`, the compiler transforms it into a coroutine. The return type's `promise_type` controls creation, suspension, result publication, exception behavior, and the object returned to the caller.

## Keyword Refresher

- `co_return` publishes the coroutine result through `return_value` or `return_void`, then moves the coroutine toward final suspend.
- `co_yield` publishes an intermediate value through `yield_value`, usually suspends, and lets a consumer resume the coroutine later.
- `co_await` evaluates an awaitable, may suspend through an awaiter, and returns or throws through `await_resume` when execution continues.

## Coroutine Frame

The coroutine frame contains the promise object, parameters, locals that survive suspension, and compiler bookkeeping. It may be heap allocated, elided, pooled, or custom allocated depending on the promise and compiler optimization.

Review implications:

- Any reference or pointer stored in the frame must outlive every suspension that uses it.
- Destroying the frame destroys suspended local objects.
- A coroutine handle behaves like a raw capability to resume or destroy the frame; it is not ownership by itself.

## Frame Size And Allocation

- Large locals that live across suspension points increase coroutine frame size.
- Values used only before a suspension point should leave scope before `co_await` when practical.
- Moving or clearing large containers before suspension can reduce retained memory, but do not clear data that is still needed after resume.
- Inspect generated code when frame size matters. With Clang LLVM IR, look for coroutine size intrinsics or allocation calls; with assembly, look for the coroutine frame allocation size.
- Heap allocation elision depends on compiler, optimization level, coroutine shape, and whether lifetime can be proven by the compiler.

## Promise Type Responsibilities

The promise type typically defines:

- `get_return_object()` to create the public coroutine object.
- `initial_suspend()` to choose eager or lazy start.
- `final_suspend()` to publish completion, resume continuations, or keep the frame available for result retrieval.
- `return_value`, `return_void`, or `yield_value` for value publication.
- `unhandled_exception()` for exception storage, translation, termination, or propagation.

## Awaiter Protocol

`co_await expr` resolves to an awaiter and uses:

- `await_ready()` to decide whether to suspend.
- `await_suspend(handle)` to publish the continuation, schedule resumption, transfer control, or decline suspension.
- `await_resume()` to return a value or throw after resumption.

`await_suspend` is a high-risk function. It may run before suspension is fully visible to other threads, may schedule the coroutine, may return a handle for symmetric transfer, or may throw depending on the awaiter design.

## Suspension Points

Reason about these separately:

- `initial_suspend`: whether the coroutine starts immediately or waits for a consumer.
- Each `co_await`: whether it resumes inline, later, on another thread, or through a scheduler.
- Each `co_yield`: whether yielded storage remains valid until consumed.
- `final_suspend`: whether continuations resume safely and whether result state remains readable.

## Core Invariants

- A coroutine frame is resumed only while alive and not already running.
- A coroutine frame is destroyed exactly once.
- A continuation is resumed at most once unless explicitly reusable.
- Exceptions are observable, translated, or intentionally terminating.
- Cancellation and early destruction leave no callbacks with dangling handles.