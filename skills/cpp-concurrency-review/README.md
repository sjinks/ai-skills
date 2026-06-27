# cpp-concurrency-review

> Use when: reviewing, designing, implementing, or debugging C++ multithreaded code using std::thread, std::jthread, std::mutex, std::atomic, condition variables, memory ordering, data races, deadlock, lock ordering, double-checked locking, thread_local, call_once, shared_ptr cross-thread aliasing, false sharing, cross-thread signal/observer/callback dispatch, or shutdown/join semantics.

This skill is aimed at C++ code that shares mutable state across threads with standard primitives, where the question is whether every access is provably ordered and shutdown is deterministic.

It helps an assistant:

- inventory shared mutable state and assign each item a named synchronization regime, then verify every access follows it
- check lock discipline: global acquisition order or `std::scoped_lock`, bounded hold times, and no calls into unknown code under locks
- verify condition-variable protocols (predicate loops under the right mutex, notify-after-change, shutdown wakes all waiters)
- review atomic protocols: acquire/release pairing, when `relaxed` is acceptable, double-checked initialization, ABA and `compare_exchange_weak` loops
- enforce thread lifecycle rules: join-on-all-paths or justified detach, explicit shutdown order, destruction races prevented by join or `weak_ptr`
- review cross-thread observer/callback dispatch: a race-free callback container during emission (verified, not assumed) and slot-captured-object lifetime across the emission via slot tracking or join/drain ordering
- return `BLOCK`, `CONCERNS`, or `CLEAN` with shared-state inventory, findings, checklist status, test expectations, and an insufficient-context template

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
