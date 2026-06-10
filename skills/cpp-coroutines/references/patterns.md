# C++ Coroutine Patterns

Use these as implementation-shape references, not drop-in library code. Match the local codebase's coroutine abstraction before inventing a new one.

## Owning Task Shape

An owning task should make frame ownership visible:

```cpp
struct task {
    struct promise_type;

    std::coroutine_handle<promise_type> m_handle{};

    explicit task(std::coroutine_handle<promise_type> handle) : m_handle(handle) {}
    task(task&& other) noexcept : m_handle(std::exchange(other.m_handle, {})) {}
    task(task const&) = delete;
    ~task() { if (this->m_handle) this->m_handle.destroy(); }
};
```

The exact result, exception, scheduler, and continuation behavior belongs in `promise_type`. The key invariant is that the public return object has a clear destruction policy.

## Awaiter Lifetime

Awaiters that store continuation handles must define who clears or invalidates those handles on cancellation or destruction:

```cpp
bool await_suspend(std::coroutine_handle<> continuation)
{
    this->m_continuation = continuation;
    return this->m_scheduler.enqueue(this);
}
```

Review whether `enqueue` can fail, whether it can resume inline, and whether `this` remains alive until resume or cancellation.

## Final Suspend Continuation

Continuation resume usually belongs in `final_suspend`, but the promise must remain valid while the continuation is selected:

```cpp
auto final_suspend() noexcept
{
    struct awaiter {
        bool await_ready() noexcept { return false; }
        std::coroutine_handle<> await_suspend(std::coroutine_handle<promise_type> handle) noexcept
        {
            return handle.promise().m_continuation ? handle.promise().m_continuation : std::noop_coroutine();
        }
        void await_resume() noexcept {}
    };
    return awaiter{};
}
```

Ensure continuations are resumed at most once and do not access destroyed result storage.

## Generator Pull Model

For generators, the consumer usually owns resumption. Check yielded references and values carefully:

```cpp
auto yield_value(value_type value)
{
    this->m_current = std::move(value);
    return std::suspend_always{};
}
```

Avoid yielding references to locals that will be invalidated before the consumer reads them.

## Cancellation Hook

Cooperative cancellation should be visible at suspension points:

```cpp
if (token.stop_requested()) {
    co_return cancelled{};
}
```

If an external operation owns completion, cancellation must also unregister callbacks or arrange for late completion to see a safe shared state rather than a destroyed coroutine frame.

## Scheduler-Aware Awaiter

When an awaiter changes execution context, name the scheduler boundary:

```cpp
void await_suspend(std::coroutine_handle<> continuation)
{
    this->m_scheduler.post([continuation] { continuation.resume(); });
}
```

Review whether `post` can run inline, whether it preserves ordering, and whether cancellation can happen before the posted continuation runs.