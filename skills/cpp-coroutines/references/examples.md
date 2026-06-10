# Safer C++ Coroutine Examples

Use these examples as guarded implementation sketches. They are not a complete coroutine library. Prefer local abstractions when the codebase already has a task, generator, scheduler, or cancellation model.

## Move-Only Owning Handle

```cpp
template <typename Promise>
class owning_coroutine_handle {
public:
    explicit owning_coroutine_handle(std::coroutine_handle<Promise> handle) noexcept
        : m_handle(handle)
    {
    }

    owning_coroutine_handle(owning_coroutine_handle&& other) noexcept
        : m_handle(std::exchange(other.m_handle, {}))
    {
    }

    owning_coroutine_handle& operator=(owning_coroutine_handle&& other) noexcept
    {
        if (this != &other) {
            if (this->m_handle) {
                this->m_handle.destroy();
            }
            this->m_handle = std::exchange(other.m_handle, {});
        }
        return *this;
    }

    owning_coroutine_handle(owning_coroutine_handle const&) = delete;
    owning_coroutine_handle& operator=(owning_coroutine_handle const&) = delete;

    ~owning_coroutine_handle()
    {
        if (this->m_handle) {
            this->m_handle.destroy();
        }
    }

private:
    std::coroutine_handle<Promise> m_handle{};
};
```

This pattern makes single ownership explicit. Real task types still need result, exception, cancellation, and continuation behavior.

## Exception-Storing Promise Shape

```cpp
struct promise_base {
    std::exception_ptr m_exception;

    void unhandled_exception() noexcept
    {
        this->m_exception = std::current_exception();
    }

    void rethrow_if_exception()
    {
        if (this->m_exception) {
            std::rethrow_exception(this->m_exception);
        }
    }
};
```

The public awaiter or `get()` equivalent must call `rethrow_if_exception()` or otherwise report the stored error. Storing exceptions without an observation path is a bug.

## Callback Adapter With Shared State

```cpp
struct callback_state {
    std::mutex m_mutex;
    std::coroutine_handle<> m_continuation;
    bool m_completed = false;
    bool m_cancelled = false;
};
```

Use shared state when callbacks may outlive the coroutine object. The callback should complete exactly once, and cancellation or destruction should either unregister the callback or mark state so late completion cannot resume a destroyed frame.

Lifecycle shape:

1. Awaiter stores continuation into shared state.
2. External operation owns a copy of shared state, not just a raw coroutine handle.
3. Task destruction or cancellation unregisters the callback when possible.
4. If unregistration is impossible, destruction marks shared state as cancelled.
5. Late callback checks shared state and does not resume a destroyed frame.

## Fake Scheduler For Tests

```cpp
class fake_scheduler {
public:
    void post(std::coroutine_handle<> continuation)
    {
        this->m_ready.push_back(continuation);
    }

    void run_one()
    {
        auto continuation = this->m_ready.front();
        this->m_ready.pop_front();
        continuation.resume();
    }

private:
    std::deque<std::coroutine_handle<>> m_ready;
};
```

Fake schedulers make resume ordering deterministic. Add guards if tests need cancellation or destruction before scheduled resume.

## Generator Safety Shape

```cpp
std::suspend_always yield_value(value_type value)
{
    this->m_current = std::move(value);
    return {};
}
```

Store yielded values in promise-owned storage when possible. Yield references only when the referenced object is guaranteed to outlive the consumer observation.