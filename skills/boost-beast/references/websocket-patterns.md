# WebSocket Patterns

Use these as small WebSocket implementation patterns to adapt to the surrounding codebase. They assume the upgrade request has already passed the strictness gate and role-specific WebSocket policy.

## Single Writer

```cpp
std::deque<std::shared_ptr<std::string const>> outgoing;
bool write_active = false;

boost::asio::awaitable<void> send(std::string message)
{
    outgoing.push_back(std::make_shared<std::string const>(std::move(message)));
    if (write_active) {
        co_return;
    }

    write_active = true;
    while (!outgoing.empty()) {
        auto current = outgoing.front();
        co_await websocket.async_write(boost::asio::buffer(*current), boost::asio::use_awaitable);
        outgoing.pop_front();
    }
    write_active = false;
}
```

Bound the queue, define the overflow policy, and handle close/cancel paths that wake or discard queued writers.

## Close-Aware Send Gate

```cpp
if (closing || closed) {
    co_return;
}
```

Gate new sends once a close is requested or observed. A WebSocket close frame, timeout, protocol error, or transport disconnect should transition the session into a state where new application messages are rejected or dropped according to policy.

## Message Lifetime

```cpp
auto message = std::make_shared<std::string const>(std::move(payload));
co_await websocket.async_write(boost::asio::buffer(*message), boost::asio::use_awaitable);
```

Any buffer passed to `async_write` must remain valid until the operation completes. Shared ownership is one simple pattern; coroutine-frame storage is also valid when the coroutine owns the message until completion.