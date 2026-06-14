# cpp-coroutines

> Use when: designing, implementing, reviewing, or debugging C++20 coroutines, co_await, co_return, co_yield, promise_type, coroutine_handle, awaiter, awaitable, task, generator, scheduler, cancellation, exception propagation, coroutine lifetime, frame allocation, symmetric transfer, or async control-flow code.

This skill is aimed at standalone C++20 coroutine mechanics where coroutine frame ownership, promise behavior, awaiter lifetime, scheduler interaction, exception propagation, cancellation, and allocation behavior determine correctness.

It helps an assistant:

- distinguish language-level coroutine design from Boost.Asio `awaitable` I/O flow and Beast protocol work
- design or review `task`, `generator`, custom awaiters, callback adapters, `promise_type`, `final_suspend`, continuation chaining, symmetric transfer, and custom frame allocation
- identify lifetime bugs such as dangling frames, dangling awaiters, double resume, missed resume, swallowed exceptions, detached work, and scheduler surprises
- plan deterministic tests for suspension, resumption, cancellation, early destruction, exception paths, scheduler hops, and frame-lifetime invariants

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- [`references/`](references/) — extended workflow and reference material.
- [`assets/`](assets/) — review templates.
