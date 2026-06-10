# Testing C++ Coroutines

Use this reference to plan deterministic tests for coroutine return types, awaiters, generators, cancellation, exceptions, schedulers, and lifetime behavior.

## Test Seams

- Return type seam: construct, move, destroy, await, and observe result.
- Awaiter seam: call `await_ready`, `await_suspend`, and `await_resume` through a tiny coroutine harness.
- Scheduler seam: fake scheduler records posted continuations and resumes them deterministically.
- Callback adapter seam: trigger success, failure, cancellation, and late completion.
- Generator seam: iterate partially, exhaust fully, destroy early, and propagate exceptions.

## Required Cases

- Success result is delivered exactly once.
- Exception is rethrown, translated, or reported according to policy.
- Cancellation before suspension, during suspension, and racing with completion is deterministic.
- Destroying a not-yet-started coroutine frees the frame.
- Destroying a suspended coroutine unregisters or safely neutralizes callbacks.
- Continuation resumes at most once.
- Scheduler hop occurs on the expected scheduler or thread.
- Move construction transfers ownership and moved-from objects are harmless.

## Generator Tests

- Full iteration consumes all yielded values and reports completion.
- Partial iteration followed by generator destruction cleans up safely.
- Destroy-before-exhaustion does not leave dangling yielded references or external callbacks.
- Exceptions thrown during iteration are propagated, translated, or reported according to the generator contract.
- Dangling-yield and early-destruction tests should run under ASan; callback-backed or cross-thread generators should also use TSan where practical.

## Avoid Timing Tests

Do not use sleeps to prove coroutine ordering. Prefer explicit completion hooks, fake schedulers, deterministic queues, and observable state transitions.

## Test Evidence To Report

- Coroutine type and promise behavior under test.
- Suspension point being exercised.
- Owner of frame destruction.
- Cancellation or exception path.
- Scheduler or thread-affinity assertion.
- Sanitizers or stress checks used.