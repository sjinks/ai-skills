# Coroutine Interoperability

Use this reference when C++ coroutine code crosses library, framework, executor, callback, future, generator, or ABI boundaries.

## Boost.Asio

- `boost::asio::awaitable`, `co_spawn`, executors, strands, sockets, timers, and I/O cancellation specifics are out of scope here; this reference covers only the bridging contract.
- Preserve executor affinity. Do not adapt an Asio operation into a generic coroutine if resumption might occur on the wrong executor.
- Treat `operation_aborted` and cancellation according to the Asio operation's contract.

## Callback Adapters

- Use shared state when callbacks may outlive the awaiting coroutine object.
- Define behavior for success, error, cancellation, and late completion after destruction.
- Ensure callbacks complete the awaiter exactly once.

## Callback Ownership Model Decisions

- If the operation can be unregistered, destruction or cancellation should unregister before the coroutine frame can be destroyed.
- If the operation cannot be unregistered, completion must target shared state that outlives both the coroutine frame and the callback.
- If cleanup waits for a worker or detached execution path, decide whether destruction may block, must cancel-and-join, or must mark state for late completion.
- Never let a detached thread or callback own only a raw coroutine handle unless another owner guarantees the frame remains alive until completion.

## Futures And Promises

- Bridging to `std::future` can block if consumers call `get()` synchronously.
- Prefer nonblocking completion channels when integrating with coroutine schedulers.
- Preserve exception propagation behavior when converting between future-like and coroutine-like APIs.

## Generators And Ranges

- `std::generator` is C++23, not C++20. Verify target standard and library support before using it.
- Generator references must remain valid until the consumer observes them.
- Partial iteration and early destruction are required test cases.

## Senders/Receivers

- If the codebase uses sender/receiver abstractions, do not bypass their cancellation, scheduler, or completion-channel model with an unrelated task type.
- Adapters should preserve value, error, and stopped channels explicitly.

## ABI And Toolchain Notes

- Coroutine ABI, allocation behavior, and optimization quality vary by compiler and standard library.
- Avoid exposing custom coroutine frame details across stable ABI boundaries.
- Verify support for `<coroutine>`, `std::coroutine_handle`, `std::noop_coroutine`, and any library coroutine type in the target toolchain.
- Heap allocation elision is an optimization, not a contract. Do not rely on allocation-free coroutine creation unless benchmarks and generated-code checks confirm it for the target compiler and build flags.
- Compiler Explorer or local generated IR/assembly can help inspect frame size and allocation behavior for hot coroutine paths.

## Library Boundary Questions

- Which library owns scheduling?
- Which library owns cancellation?
- Which library owns frame destruction or callback unregistration?
- Are exceptions allowed across the boundary?
- Does the boundary preserve thread affinity and ordering?