# Failure-Mode Scenarios

Use this reference when the user reports a concrete coroutine symptom, code smell, failed test, or production behavior. It maps observed behavior to the smallest useful reference set.

## Lifetime And Resume

| Observed pattern | Primary risk | Load first | Then load |
|---|---|---|---|
| Callback-backed awaiter stores a raw `std::coroutine_handle<>` and the owning task can be destroyed first | Use-after-free, late resume into destroyed frame | [debugging](./debugging.md) | [review checklist](./review-checklist.md), [testing](./testing.md), [interoperability](./interoperability.md) |
| Coroutine resumes twice | Double completion, state corruption | [debugging](./debugging.md) | [testing](./testing.md), [patterns](./patterns.md) |
| Coroutine never resumes | Lost continuation, scheduler stopped, cancellation path forgot completion | [debugging](./debugging.md) | [testing](./testing.md), [concepts](./concepts.md) |
| Task destructor destroys frame while callback still owns continuation | Dangling handle, crash after callback fires | [interoperability](./interoperability.md) | [examples](./examples.md), [review checklist](./review-checklist.md) |
| Detached coroutine has no observable completion or exception path | Leaked work, swallowed failure, shutdown hang | [review checklist](./review-checklist.md) | [debugging](./debugging.md), [testing](./testing.md) |

## Promise And Awaiter Semantics

| Observed pattern | Primary risk | Load first | Then load |
|---|---|---|---|
| `unhandled_exception` stores or ignores exceptions but `await_resume` never reports them | Swallowed exception | [concepts](./concepts.md) | [review checklist](./review-checklist.md), [testing](./testing.md) |
| `final_suspend` resumes a continuation that reads destroyed state | Use-after-final-suspend | [concepts](./concepts.md) | [patterns](./patterns.md), [debugging](./debugging.md) |
| `await_suspend` can resume inline but caller assumes asynchronous resume | Reentrancy, stack-depth, ordering bug | [concepts](./concepts.md) | [decision trees](./decision-trees.md), [testing](./testing.md) |
| Awaiter captures references to stack objects across suspension | Dangling reference | [review checklist](./review-checklist.md) | [debugging](./debugging.md), [testing](./testing.md) |

## Generators

| Observed pattern | Primary risk | Load first | Then load |
|---|---|---|---|
| Generator yields references to locals or temporary storage | Dangling yielded value | [concepts](./concepts.md) | [examples](./examples.md), [review checklist](./review-checklist.md) |
| Generator crashes when iteration stops early | Early destruction bug | [testing](./testing.md) | [examples](./examples.md), [debugging](./debugging.md), [interoperability](./interoperability.md) |
| Generator exception disappears or terminates unexpectedly | Broken exception path | [review checklist](./review-checklist.md) | [testing](./testing.md) |
| Generator is backed by callbacks, external iterator state, or a range adapter | Boundary lifetime mismatch | [interoperability](./interoperability.md) | [testing](./testing.md), [review checklist](./review-checklist.md), [examples](./examples.md) |

## Scheduler And Interop

| Observed pattern | Primary risk | Load first | Then load |
|---|---|---|---|
| Coroutine resumes on the wrong thread or executor after `co_await` | Thread-affinity violation | [interoperability](./interoperability.md) | [debugging](./debugging.md), [testing](./testing.md) |
| Asio awaitable is adapted into a generic task and loses executor affinity | Broken Asio contract | [interoperability](./interoperability.md) | Boost.Asio skill, [review checklist](./review-checklist.md) |
| Future bridge blocks an event loop or I/O thread | Deadlock, latency spike | [interoperability](./interoperability.md) | [decision trees](./decision-trees.md), [testing](./testing.md) |
| Sender/receiver adapter drops stopped or error channel | Lost cancellation/error signal | [interoperability](./interoperability.md) | [review checklist](./review-checklist.md) |

## Performance And Allocation

| Observed pattern | Primary risk | Load first | Then load |
|---|---|---|---|
| Coroutine frame is unexpectedly large | Memory overhead, cache pressure | [performance](./performance.md) | [concepts](./concepts.md), [testing](./testing.md) |
| Hot coroutine path allocates per call | Allocation overhead | [performance](./performance.md) | [interoperability](./interoperability.md) |
| Large object lives across `co_await` unnecessarily | Retained frame memory | [performance](./performance.md) | [concepts](./concepts.md), [review checklist](./review-checklist.md) |

## Review Output Shortcut

For review tasks that start from any scenario above:

1. Lead with findings ordered by severity.
2. For each finding, name the observed behavior, primary risk, and minimal fix direction.
3. Add targeted tests using [testing](./testing.md).
4. End with residual risk and open questions that affect ownership, cancellation, scheduler behavior, or API contract.