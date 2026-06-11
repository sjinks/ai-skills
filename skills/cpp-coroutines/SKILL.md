---
name: cpp-coroutines
description: 'Use when: designing, implementing, reviewing, or debugging C++20 coroutines, co_await, co_return, co_yield, promise_type, coroutine_handle, awaiter, awaitable, task, generator, scheduler, cancellation, exception propagation, coroutine lifetime, frame allocation, symmetric transfer, or async control-flow code.'
argument-hint: 'Describe the coroutine design, bug, review target, awaitable/task type, generator, scheduler, or lifetime issue.'
user-invocable: true
---

# C++ Coroutines Skill

Use this skill for standalone C++ coroutine work: coroutine type design, `promise_type`, awaiters, awaitables, tasks, generators, cancellation, scheduler integration, exception propagation, frame lifetime, allocation behavior, and coroutine-heavy control flow.

This skill is standalone. Do not assume Boost.Asio, cppcoro, Folly, Qt, Unreal, or any specific coroutine library unless the local codebase already uses one. Tasks that are specifically about Boost.Asio `awaitable`, executors, strands, sockets, timers, or I/O cancellation are out of scope.

## Routing

- **WORKFLOW SKILL**: use for C++20 coroutine design, implementation, review, debugging, and test-planning tasks.
- INVOKES: inspect local coroutine abstractions first for implementation or review; load reference packs only when the task needs their detail.
- FOR SINGLE OPERATIONS: answer narrow coroutine questions directly after identifying frame ownership, suspension/resume behavior, and lifetime risk.
- Use this skill for language-level C++ coroutine design: custom `promise_type`, awaiters, coroutine handles, frame lifetime, generators, cancellation contracts, scheduler bridges, symmetric transfer, and allocation behavior.
- Out of scope: tasks mainly about Asio executors, sockets, timers, strands, `co_spawn`, or `boost::asio::awaitable` I/O flow.
- Out of scope: tasks mainly about Beast HTTP/WebSocket parser, serializer, body, stream, or protocol behavior.

## DO NOT USE FOR:

- Ordinary callback, future, thread-pool, or synchronous control-flow code unless coroutine mechanics or coroutine migration are part of the task.
- Boost.Asio `awaitable` I/O work where executor affinity, sockets, timers, strands, or Asio cancellation are the main concern.
- Boost.Beast HTTP/WebSocket parser, serializer, body, stream, or protocol behavior.

## Operating Posture

Treat coroutine code as lifetime-sensitive control-flow infrastructure. For nontrivial design or review work, use [decision trees](./references/decision-trees.md) to define ownership, eagerness, result/error model, cancellation strategy, and scheduler behavior before suggesting code. For detailed mechanics and implementation shapes, use [concepts](./references/concepts.md) and [patterns](./references/patterns.md) when the main file is not enough.

## Terminology Baseline

- **Coroutine frame:** Compiler-created storage containing parameters, locals that survive suspension, promise object, and bookkeeping.
- **Promise type:** The type that controls coroutine creation, result publication, exception handling, suspension policy, and returned coroutine object.
- **Coroutine handle:** A `std::coroutine_handle<>` that can resume, destroy, or inspect a coroutine frame according to its promise type.
- **Awaiter:** The object used by `co_await` after `operator co_await` resolution, with `await_ready`, `await_suspend`, and `await_resume`.
- **Awaiter lifetime:** The interval during which an awaiter object must remain accessible: from the start of `await_suspend()` until `await_resume()` completes or throws. Callback-backed awaiters must be stored safely or use shared state if completion can outlive the coroutine frame.
- **Awaitable:** A type that can be awaited directly or can produce an awaiter.
- **Owning coroutine type:** A return object such as `task<T>` or `generator<T>` that owns or shares responsibility for destroying the coroutine frame. Ownership determines when the frame is freed and must be tracked across move operations.
- **Borrowed handle:** A `std::coroutine_handle<>` used temporarily in a tightly scoped context, such as an awaiter or callback, where the owner's lifetime is proven by construction. It must not outlive the owner.
- **Detached coroutine:** A coroutine whose completion, exceptions, cancellation, and lifetime are not joined by the caller. Treat detachment as a design decision, not a convenience default.
- **Final suspend:** The suspension point after coroutine completion where continuations are often resumed and frame destruction policy becomes critical.

## When To Use

- Designing a `task`, `generator`, async operation wrapper, lazy coroutine, eager coroutine, scheduler-aware awaitable, or coroutine-based pipeline.
- Implementing or reviewing `promise_type`, `std::coroutine_handle`, `operator co_await`, custom awaiters, `co_yield`, `co_return`, `initial_suspend`, `final_suspend`, or continuation chaining.
- Debugging use-after-free, leaked coroutine frames, double resume, missed resume, dangling awaiters, swallowed exceptions, cancellation gaps, scheduler hops, or shutdown hangs.
- Migrating callbacks, state machines, or generators into coroutine-based code.
- Planning deterministic tests for suspension, resumption, cancellation, exception propagation, destruction, and scheduler behavior.

## Task Modes

- **Design mode:** define coroutine ownership, eagerness, suspension policy, result/error model, cancellation model, scheduler/executor model, continuation behavior, and verification plan before suggesting code.
- **Implementation mode:** inspect local coroutine abstractions first, then make the smallest change that preserves frame lifetime, awaiter lifetime, cancellation, exceptions, and testability.
- **Review mode:** lead with correctness risks: dangling frames, dangling awaiters, double resume, unobserved exceptions, missing cancellation, final-suspend bugs, detached work, and scheduler/thread-affinity surprises.
- **Debug mode:** build a hypothesis table from symptoms, coroutine state, owner lifetime, handle state, awaiter state, scheduler state, cancellation source, and exception path.
- **Test-planning mode:** select tests for success, exception, cancellation, early destruction, double-resume prevention, scheduler hop, lazy/eager start, and final-suspend continuation behavior.

## Reference Packs

Load these only when the task needs the extra detail:

- Use [package index](./references/index.md) to choose the smallest useful reference set for design, implementation, review, debugging, or testing tasks.
- Use [scenarios](./references/scenarios.md) when the user reports a concrete symptom, code smell, failed test, or suspicious coroutine behavior.
- Use [concepts](./references/concepts.md) for the language-level coroutine model: promise, frame, awaiter protocol, handles, and suspension points.
- Use [decision trees](./references/decision-trees.md) for choosing task vs generator, lazy vs eager start, owning vs borrowed handles, exceptions vs result types, and scheduler strategy.
- Use [patterns](./references/patterns.md) for compact ownership, awaiter, generator, continuation, cancellation, and scheduler integration patterns.
- Use [examples](./references/examples.md) for safer guarded sketches of owning handles, exception storage, callback shared state, fake schedulers, and generator storage.
- Use [performance](./references/performance.md) for frame-size, allocation, pooling, generated-code inspection, and hot-path review guidance.
- Use [debugging](./references/debugging.md) for playbooks covering leaked frames, dangling awaiters, double resume, missed resume, swallowed exceptions, and scheduler surprises.
- Use [testing](./references/testing.md) for deterministic coroutine tests, fake schedulers, lifecycle probes, cancellation checks, and sanitizer guidance.
- Use [review checklist](./references/review-checklist.md) for a reusable C++ coroutine review output template.
- Use [interoperability](./references/interoperability.md) for Boost.Asio, senders/receivers, futures, callbacks, generators, ABI/version notes, and library-boundary concerns.

## Assets

Use [review templates](./assets/review-templates.md) for coroutine lifetime review, promise type review, awaiter review, generator review, callback adapter review, and test-plan prompts.

## Procedure

1. Identify the coroutine boundary: return type, awaited operation, generator, scheduler bridge, callback adapter, or coroutine-based state machine. If the starting point is a concrete failure mode, use [scenarios](./references/scenarios.md) first.
2. Determine whether the coroutine is lazy or eager, and who owns the coroutine frame from creation until destruction.
3. Define every suspension point: `initial_suspend`, each `co_await`, each `co_yield`, and `final_suspend`.
4. Define the result and error model: returned value, stored exception, `std::expected`-style result, error code, cancellation result, or termination policy.
5. Define cancellation and early destruction behavior. State what happens when the consumer destroys the task/generator before completion.
6. Define scheduler or thread-affinity behavior. State whether resumption is inline, posted to a scheduler/executor, or controlled by the awaited operation.
7. Preserve lifetime. Awaiters, references, buffers, callbacks, and continuations must not outlive their backing objects or coroutine frames.
8. For implementation tasks, add or update tests at the narrowest stable seam that observes the behavior. For design, review, debugging, or test-planning tasks, identify required tests and verification steps without editing files unless requested.

## Design Checklist

Before implementation, verify:

- Frame ownership and destruction policy are explicit.
- `initial_suspend` and `final_suspend` behavior matches the API contract.
- Suspension points and resumption context are defined for each `co_await` and `co_yield`.
- `await_suspend` behavior is correct for inline resume, scheduler resume, failure, and cancellation paths.
- Symmetric transfer is used only when ownership, continuation lifetime, and exception propagation are explicit.
- Frame allocation, allocation failure, and frame-size costs are acceptable for the API and hot path.
- Awaiters cannot resume a destroyed coroutine; `final_suspend` awaiters may read promise state but must not publish references that outlive the frame.
- Result, exception, and cancellation paths are observable or deliberately hidden by API contract.
- Tests can verify success, exception, cancellation, early destruction, scheduler behavior, and lifetime-sensitive paths.

For a complete review template, use [review checklist](./references/review-checklist.md) after implementation.

## Common Anti-Patterns

- Returning a coroutine object that does not own or safely reference its coroutine frame.
- Destroying a coroutine handle while another callback or awaiter can still resume it.
- Capturing references to stack objects across suspension without proving lifetime.
- Capturing raw `this` in async callbacks or lambda captures when the callback can resume after the owning object is destroyed.
- Assuming `co_await` always resumes on the same thread or executor.
- Using `std::coroutine_handle<>` as a raw pointer without clear ownership rules.
- Swallowing exceptions in `unhandled_exception` without an observable error path.
- Detaching coroutines whose exceptions, cancellation, and completion are never observed.
- Calling `resume()` from multiple paths without a single-resume invariant.
- Implementing `final_suspend` so continuations can access destroyed promise state.

## Review Heuristics

- Start with ownership: who destroys the coroutine frame, and can anything resume it after destruction?
- Check every captured reference and pointer that crosses a suspension point.
- Inspect `await_suspend`: inline resume, transfer, cancellation, exceptions, and scheduler behavior often hide bugs there.
- Check `final_suspend` and continuation logic before reviewing API ergonomics.
- Verify exceptions and cancellation are observable by the caller or deliberately mapped.
- For library adapters, check that the adapter preserves the source library's thread-affinity, cancellation, and lifetime contracts.

## Output Expectations

When producing substantive output, match the active task mode:

- Design: include coroutine boundary, ownership/lifetime, laziness/eagerness, suspension points, result/error model, cancellation, scheduler behavior, and verification plan.
- Implementation: state the local coroutine abstractions inspected, lifetime and scheduler decisions, exception/cancellation behavior, and tests run or still needed.
- Review: lead with findings ordered by severity, then summarize frame ownership, awaiter lifetime, suspension/resume behavior, cancellation, exceptions, scheduler behavior, and test gaps.
- Debug: provide a hypothesis table with Symptom, Evidence to collect, Likely cause, Confirming check, and Targeted fix; end with the next minimal reproduction or logging step.
- Test planning: provide deterministic test cases with seam, setup, action, assertions, covered failure mode, and required tool/sanitizer where relevant.

Keep recommendations concrete enough for a builder to implement without inventing the coroutine ownership model.