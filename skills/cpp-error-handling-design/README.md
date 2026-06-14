# cpp-error-handling-design

> Use when: designing, reviewing, or refactoring C++ error handling policy, exceptions vs std::expected vs error codes, exception safety guarantees (basic, strong, nothrow), RAII rollback, noexcept and move semantics interactions, error propagation across module or ABI or thread or coroutine boundaries, std::error_code categories, terminate paths, or destructor and swap exception rules.

This skill is aimed at C++ code and APIs that must choose, implement, or review an error-reporting strategy and deliver stated exception-safety guarantees across boundaries.

It helps an assistant:

- establish an explicit error policy per layer: which channel (exceptions, `std::expected`, `std::error_code`) reports which failure class, with translation rules at boundaries
- separate recoverable failures from programming-bug contract violations and from unrepresentable states
- verify basic/strong/nothrow guarantees, requiring commit-rollback for strong claims and RAII ownership on throwing paths
- place `noexcept` deliberately on moves, swap, and destructors, including the container fallback consequences of throwing moves
- stop exceptions at `extern "C"`, thread, callback, and destructor boundaries, and carry errors across async hops with `std::exception_ptr` or `std::expected`
- enforce consumption: `[[nodiscard]]` error channels, no silent catch-and-swallow, every failure class has a consumer
- return `BLOCK`, `CONCERNS`, or `CLEAN` with the policy, findings, checklist status, failure-path test expectations, and an insufficient-context template

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
