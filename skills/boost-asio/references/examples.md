# Boost.Asio Examples

These snippets are intentionally small. Adapt naming, logging, error types, and ownership to the target codebase.

Snippet assumptions: session methods shown here run on the session's owning executor or strand unless a snippet says otherwise; server methods shown here run on the server or acceptor executor unless a snippet says otherwise; `close()` is idempotent and executor-affine; shown `m_` fields are session- or server-owned and live until all outstanding operations complete. If producers or shutdown callers can call these methods from other threads or executors, dispatch the state mutation onto the owning executor/strand or protect the state with a documented synchronization boundary.

## Coroutine Error Handling

Use `as_tuple(use_awaitable)` when expected transport errors should stay local instead of becoming exceptions.

```cpp
using boost::asio::awaitable;
using boost::asio::use_awaitable;
using boost::asio::as_tuple;
using boost::asio::ip::tcp;

awaitable<void> read_some(tcp::socket& socket, std::span<char> buffer) {
  auto [ec, n] = co_await socket.async_read_some(
      boost::asio::buffer(buffer), as_tuple(use_awaitable));

  if (ec == boost::asio::error::operation_aborted) {
    co_return;
  }
  if (ec == boost::asio::error::eof || ec == boost::asio::error::connection_reset) {
    co_return;
  }
  if (ec) {
    // Map to the local transport/session error model.
    co_return;
  }

  // Process buffer[0..n) while the backing storage is still alive.
}
```

## Callback Lifetime Capture

Use `shared_from_this()` when a callback-style operation can outlive the initiating member call.

```cpp
class session : public std::enable_shared_from_this<session> {
public:
  void start() { this->read(); }

private:
  void read() {
    auto self = shared_from_this();
    this->m_socket.async_read_some(boost::asio::buffer(this->m_buffer),
        [self](boost::system::error_code ec, std::size_t n) {
          self->on_read(ec, n);
        });
  }

  void on_read(boost::system::error_code ec, std::size_t n) {
    if (ec) {
      this->close();
      return;
    }
    // Process m_buffer[0..n), then schedule the next read if still open.
    this->read();
  }

  void close();

  boost::asio::ip::tcp::socket m_socket;
  std::array<char, 8192> m_buffer{};
};
```

## Bounded Write Queue

Serialize writes and choose an explicit slow-client policy.

If producers can call `send()` from another thread or executor, first `post` or `dispatch` onto the session strand/executor before reading or mutating `m_outbox`.

```cpp
void session::send(std::string message) {
  if (this->m_outbox.size() >= this->m_max_queued_messages) {
    this->close(); // Or reject/drop/coalesce, but make the policy explicit.
    return;
  }

  const bool write_in_flight = !this->m_outbox.empty();
  this->m_outbox.push_back(std::move(message));
  if (!write_in_flight) {
    this->write_next();
  }
}

void session::write_next() {
  auto self = shared_from_this();
  boost::asio::async_write(this->m_socket, boost::asio::buffer(this->m_outbox.front()),
      [self](boost::system::error_code ec, std::size_t) {
        if (ec) {
          self->close();
          return;
        }
        self->m_outbox.pop_front();
        if (!self->m_outbox.empty()) {
          self->write_next();
        }
      });
}
```

## Timeout Generation Token

Use a generation counter so stale timers cannot mutate the next operation.

```cpp
void session::arm_read_timeout(std::chrono::steady_clock::duration timeout) {
  const auto generation = ++this->m_read_generation;
  this->m_read_timer.expires_after(timeout);

  auto self = shared_from_this();
  this->m_read_timer.async_wait([self, generation](boost::system::error_code ec) {
    if (ec == boost::asio::error::operation_aborted) {
      return;
    }
    if (generation != self->m_read_generation) {
      return;
    }
    self->close();
  });
}

void session::read_completed() {
  ++this->m_read_generation;
  this->m_read_timer.cancel();
}
```

## Graceful Accept Loop Shutdown

Close the acceptor, stop admitting new sessions, and let outstanding accepts complete through the normal error path.

```cpp
awaitable<void> server::accept_loop() {
  auto executor = co_await boost::asio::this_coro::executor;

  for (;;) {
    auto [ec, socket] = co_await this->m_acceptor.async_accept(executor,
        as_tuple(use_awaitable));

    if (ec == boost::asio::error::operation_aborted || !this->m_accepting) {
      co_return;
    }
    if (ec) {
      // Log and continue or break according to local server policy.
      continue;
    }

    this->start_session(std::move(socket));
  }
}

void server::stop_accepting() {
  // If called from another thread or executor, dispatch this body onto the
  // server/acceptor executor before mutating m_accepting or m_acceptor.
  this->m_accepting = false;
  boost::system::error_code ignored;
  this->m_acceptor.close(ignored);
}
```

## Strand-Bound Session Construction

Bind all session operations to one strand when multiple I/O threads can run handlers for the same session.

```cpp
auto strand = boost::asio::make_strand(io_context);
auto socket = boost::asio::ip::tcp::socket(strand);

// Or move an accepted socket into a session that consistently dispatches work
// through the session strand before touching shared session state.
```