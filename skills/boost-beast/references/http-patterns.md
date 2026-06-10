# HTTP Patterns

Use these as small HTTP implementation patterns to adapt to the surrounding codebase. They are intentionally minimal and omit project-specific logging, result types, dependency injection, and executor ownership.

## Parser With Limits

```cpp
namespace beast = boost::beast;
namespace http = beast::http;

beast::flat_buffer buffer;
http::request_parser<http::string_body> parser;
parser.body_limit(1024 * 1024);
parser.eager(false);

auto bytes = co_await http::async_read(stream, buffer, parser, boost::asio::use_awaitable);
auto request = parser.release();
```

Set limits before the read. Validate framing, method, target, version, host, and body policy in a strictness gate before adapting `request` into public application state.

## Serializer Lifetime

```cpp
namespace http = boost::beast::http;

auto response = std::make_shared<http::response<http::string_body>>();
response->version(11);
response->result(http::status::ok);
response->keep_alive(keep_alive);
response->body() = payload;
response->prepare_payload();

co_await http::async_write(stream, *response, boost::asio::use_awaitable);
```

The response object must outlive `async_write`. In coroutine code, stack lifetime is also acceptable if the coroutine frame outlives the operation and the object is not moved before completion.

## Explicit No-Body Response

```cpp
http::response<http::empty_body> response{http::status::no_content, request.version()};
response.keep_alive(request.keep_alive());
response.set(http::field::server, "example");
co_await http::async_write(stream, response, boost::asio::use_awaitable);
```

Prefer `empty_body` for statuses and methods that must not emit a body. Do not call `prepare_payload()` as a substitute for understanding no-body semantics.

## Serialized Write Queue

```cpp
struct outbound_message {
    std::shared_ptr<void const> keep_alive_storage;
    std::function<boost::asio::awaitable<void>()> write;
};

std::deque<outbound_message> queue;
bool writing = false;

boost::asio::awaitable<void> pump_writes()
{
    if (writing) {
        co_return;
    }

    writing = true;
    while (!queue.empty()) {
        auto item = std::move(queue.front());
        queue.pop_front();
        co_await item.write();
    }
    writing = false;
}
```

Use a real bounded queue in production. The important property is one active writer per stream and storage that outlives each write.

## Streaming Response Shape

```cpp
http::response_serializer<http::buffer_body> serializer{response};

while (!serializer.is_done()) {
    auto chunk = co_await next_chunk();
    response.body().data = chunk.data();
    response.body().size = chunk.size();
    response.body().more = !chunk.last;
    co_await http::async_write_some(stream, serializer, boost::asio::use_awaitable);
}
```

Streaming bodies need carefully owned buffers. The chunk storage must remain valid until the write operation completes, and the producer must honor backpressure.

## Timeout Around Beast I/O

```cpp
beast::get_lowest_layer(stream).expires_after(std::chrono::seconds(30));
auto [error, bytes] = co_await http::async_read(
    stream,
    buffer,
    parser,
    boost::asio::as_tuple(boost::asio::use_awaitable));
```

Apply timeouts on the lowest layer that owns cancellation for the stream stack. Clear or reset timeouts between protocol phases when the stream type requires it.