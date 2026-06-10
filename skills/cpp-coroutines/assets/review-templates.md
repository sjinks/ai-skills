# C++ Coroutine Review Templates

Use these templates as starting points for repeatable coroutine reviews and test planning. Replace bracketed placeholders with task-specific context.

## Coroutine Lifetime Review

```markdown
Review the coroutine code in [files/diff]. Prioritize coroutine frame ownership, handle lifetime, suspension points, awaiter lifetime, cancellation, exception propagation, scheduler behavior, and tests.

Context:
- Coroutine boundary: [task/generator/awaiter/callback adapter/scheduler bridge]
- Start policy: [lazy/eager/unknown]
- Frame owner: [type/object/unknown]
- Scheduler or thread-affinity contract: [summary]

Output:
- Findings first, ordered by severity.
- For each finding, include the concrete lifetime or resume risk and a minimal fix direction.
- Then list open questions that affect correctness.
- End with residual test gaps.
```

## Promise Type Review

```markdown
Review the `promise_type` in [files/diff]. Focus on `get_return_object`, `initial_suspend`, `final_suspend`, result storage, `unhandled_exception`, continuation handling, frame destruction, and move/destruction behavior of the returned coroutine object.

Output findings by severity and include tests for success, exception, early destruction, and final-suspend continuation behavior.
```

## Awaiter Review

```markdown
Review the awaiter or awaitable in [files/diff]. Focus on `await_ready`, `await_suspend`, `await_resume`, continuation storage, inline resume, cancellation, scheduler handoff, exception behavior, and awaiter storage lifetime.

Check specifically:
- Can `await_suspend` resume inline?
- Can completion race with cancellation?
- Can a callback resume a destroyed coroutine frame?
- Is completion single-shot?
- Does `await_resume` report errors correctly?
```

## Generator Review

```markdown
Review the generator in [files/diff]. Focus on yielded value lifetime, partial iteration, early destruction, exception propagation, iterator behavior, and `final_suspend` cleanup.

Output findings by severity, then list tests for full iteration, partial iteration, exception during iteration, and destroy-before-exhaustion.
```

## Callback Adapter Review

```markdown
Review the callback-to-coroutine adapter in [files/diff]. Focus on raw coroutine handles, callback unregistration, shared state, task destructor coordination with callbacks, detached execution, late completion, cancellation, error propagation, and scheduler/thread-affinity preservation.

Output findings by severity and include tests for success, error, cancellation before completion, late callback after destruction, and callback racing with cancellation.
```

## Coroutine Test Plan Prompt

```markdown
Create a deterministic test plan for the coroutine behavior in [files/feature/bug].

Include:
- Test seam: return type, promise type, awaiter, callback adapter, scheduler bridge, or generator.
- Setup and scheduler/callback control.
- Action.
- Assertions.
- Failure mode covered.
- Required sanitizer, fake scheduler, or fixture.

Cover success, exception, cancellation, early destruction, move ownership, double-resume prevention, scheduler hop, and final-suspend continuation behavior where relevant.
```