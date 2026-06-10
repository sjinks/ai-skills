# C++ Coroutine Review Checklist

Use this reference when producing a coroutine-focused code review. Lead with findings; use the checklist to avoid missing lifetime and resume bugs.

## Review Output Shape

```markdown
Findings:
- Severity: file/path and behavior. Explain the coroutine lifetime, suspension, cancellation, exception, or scheduler risk.

Open questions:
- Only include questions that affect correctness or API contract.

Summary:
- Short description of what was reviewed and residual test gaps.
```

## Checklist

### Ownership And Lifetime

- Coroutine frame owner is explicit.
- Return object destructor destroys or deliberately does not own the frame.
- Move operations transfer ownership safely.
- References and pointers crossing suspension points outlive their use.

### Promise Type

- `initial_suspend` matches lazy/eager API contract.
- `final_suspend` safely handles continuations and frame lifetime.
- `unhandled_exception` makes errors observable.
- `return_value`, `return_void`, or `yield_value` stores data safely.

### Awaiters

- `await_ready` does not hide required asynchronous behavior.
- `await_suspend` handles inline resume, scheduling failure, cancellation, and exceptions.
- `await_resume` returns or throws according to the API contract.
- Awaiter storage remains alive until completion or cancellation.

### Cancellation And Destruction

- Early destruction cannot leave external callbacks with dangling handles.
- Cancellation races with success are single-completion.
- Detached coroutines have explicit ownership, logging, and failure policy.

### Scheduler And Thread Affinity

- Resumption thread or scheduler is documented by behavior.
- Inline resume is safe from reentrancy and stack-depth surprises.
- Library adapters preserve source library thread-affinity contracts.

### Tests

- Tests cover success, exception, cancellation, early destruction, move ownership, scheduler hop, and double-resume prevention.
- Generator tests include full iteration, partial iteration with early destruction, destroy-before-exhaustion, and exceptions thrown during iteration.
- Sanitizers or stress tests cover lifetime-sensitive paths where practical.

## Severity Guide

- High: use-after-free, double resume, leaked frame, swallowed exception across public API, cancellation leaving dangling callback, wrong-thread resume violating contract.
- Medium: missing tests for cancellation/final suspend, unclear eager/lazy contract, weak scheduler documentation, detached coroutine without clear observation.
- Low: naming, minor ergonomics, or documentation gaps that do not affect lifetime or correctness.