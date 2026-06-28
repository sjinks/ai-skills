---
name: cpp-concurrency-review
description: "Use when: reviewing, designing, implementing, or debugging C++ multithreaded code using std::thread, std::jthread, std::mutex, std::atomic, condition variables, memory ordering, data races, deadlock, lock ordering, double-checked locking, thread_local, call_once, shared_ptr cross-thread aliasing, false sharing, cross-thread signal/observer/callback dispatch, or shutdown/join semantics."
argument-hint: "Describe the threaded code, shared state, synchronization primitives, suspected race or deadlock, and review target."
user-invocable: true
---

# C++ Concurrency Review

Use this skill when C++ code shares mutable state across threads using standard primitives (`std::thread`, `std::jthread`, `std::mutex`, `std::atomic`, `std::condition_variable`, `std::once_flag`, `thread_local`) or dispatches observers/callbacks across threads, and the question is whether the synchronization is correct, deadlock-free, and shut down deterministically.

The goal is to make every shared access provably ordered: each piece of shared mutable state has a named synchronization regime, and every access happens under it.

**UTILITY SKILL.** INVOKES: read-only file access for supplied targets; no other tools or skills. FOR SINGLE OPERATIONS: use for focused race/deadlock review, synchronization design, memory-ordering analysis, or test planning.

## Scope

- Use this skill for data races, lock granularity and ordering, deadlock and livelock analysis, condition-variable protocols, `std::atomic` memory-ordering correctness, double-checked initialization, `thread_local` lifecycle, `shared_ptr` control-block vs pointee thread safety, false sharing, and thread lifecycle (spawn, detach, join, shutdown). For livelock, check unbounded retry loops, contended `compare_exchange` loops without backoff, and mutual yield-and-retry protocols that can starve each other.
- Apply it to raw standard-library threading code, hand-rolled thread pools, lock-free or lock-reduced structures, and producer-consumer queues built on mutexes/CVs/atomics.
- Treat object-destruction races (object destroyed while another thread still uses it) as in scope where the fix is synchronization or lifecycle ordering.
- Treat cross-thread observer/callback dispatch (e.g. Boost.Signals2 signals, hand-rolled callback registries) as in scope when slots/callbacks connect or disconnect on one thread while dispatch fires on another: the callback container, the connect/disconnect race, and slot-captured-object lifetime across the emission each need a regime.

## DO NOT USE FOR:

- Executor/strand/io_context-based async I/O design; coroutine frame mechanics; single-threaded code.
- Interpreting TSan/ASan report output when the task is tool-report triage rather than reasoning about synchronization in the code under review.
- Distributed-system or cross-process concurrency (databases, message queues, file locks).

## Required Context

Collect or infer before judging:

- Target: files, diff, design, or data structure under review.
- Shared state inventory: which variables/objects are reachable from more than one thread.
- Synchronization regime per shared item: mutex (which one), atomic (which ordering), CV protocol, immutable-after-publish, thread-confined, or unprotected.
- Thread topology: which threads exist, who spawns/joins/detaches them, and the shutdown sequence.
- Existing tests and whether TSan or stress tests run in CI.

If the target or the shared-state/thread topology cannot be established, return `Verdict: BLOCK` with one open question. Do not guess the synchronization regime. Insufficient-context mode takes precedence over pattern-level decision rules: general rules may be cited as context, but no verdict other than `BLOCK` may rest on an unseen target.

## Output Depth

Default to `standard`. `quick` still reports missing required context, blockers, unmitigated HIGH/CRITICAL findings, and target-specific concerns; it only omits non-applicable checklist expansion. `standard` covers the applicable checklist with concise evidence. `exhaustive` enumerates the full checklist only when asked or when the risk surface warrants it. Name the selected depth when the user asks for `quick` or `exhaustive`.

## Workflow

1. Inventory shared mutable state and assign each item its claimed synchronization regime.
2. Verify every access (read and write) of each item occurs under its regime; a single unprotected access is a race.
3. Check lock discipline: ordering across multiple mutexes, hold duration, calls to unknown code (callbacks, virtual functions) while holding locks.
4. Check condition-variable protocols: predicate under the same mutex, wait in a predicate loop, notify after state change, notify under or after the mutex consistently.
5. Check atomics: each atomic has a stated protocol (flag, counter, publish pointer, seqlock); orderings match the protocol; no mixed atomic/non-atomic access to the same object.
6. Check lifecycle: every thread is joined or its detachment is justified with a proven lifetime argument; shutdown wakes all waiters and prevents new work.
7. Classify findings by severity, map to a verdict, and state the test or TSan coverage each fix needs.

## Decision Rules

The Checklist below is the gating source of truth when these rules overlap; the rules explain rationale.

- When any thread writes a shared object while another thread reads or writes it without both accesses being ordered by the same mutex, atomic, or happens-before edge, it is a data race and undefined behavior regardless of how "benign" it looks; `volatile` provides no ordering.
- When two or more mutexes can be held simultaneously, fix a global acquisition order or use `std::scoped_lock` on all of them at once; document the order where it cannot be expressed in code.
- When code calls user callbacks, virtual methods, or signals while holding a lock, assume re-entry and lock-inversion are possible; release the lock first or document why the callee can never take locks.
- When a condition variable is used, the waiting thread must check the predicate in a loop under the same mutex that protects the predicate state; bare `wait()` without a predicate, or predicate state mutated outside the mutex, are findings (lost wakeup, spurious wakeup).
- When `notify_one` is used, prove one waiter is sufficient and that the right waiter wakes; prefer `notify_all` plus precise predicates when waiters have different conditions.
- When atomics use anything weaker than `seq_cst`, require a written protocol: what is published, which load observes it, and which acquire/release pair creates the edge. Default to `seq_cst` until measurement justifies weakening; `relaxed` is for counters and flags whose readers tolerate stale values.
- When double-checked initialization appears, require `std::call_once`, a magic static (block-scope `static`), or an acquire/release-correct implementation; an unsynchronized fast-path read of a non-atomic pointer is a race.
- When `shared_ptr` is shared across threads, the control block is thread-safe but neither the pointee nor a single `shared_ptr` instance is: concurrent reset/copy of the same instance, or unsynchronized pointee mutation, are findings.
- When an object can be destroyed while another thread might still call into it, require join-before-destroy, `weak_ptr` promotion at the call site, or an unregister-and-drain step proven to complete before destruction.
- When an observer/callback list is dispatched from a different thread than the one that connects or disconnects entries, require two guarantees. (1) The callback container is race-free during dispatch: an unsynchronized list iterated while connect/disconnect mutates it is a `CRITICAL` data race or iterator-invalidation use-after-free. Boost.Signals2 provides this under its default per-signal mutex (it snapshots the slot list under the lock, then unlocks before running slots), but verify the guarantee rather than assume it — a hand-rolled registry usually does not provide it, and a signal instantiated with a non-thread-safe mutex policy (`boost::signals2::dummy_mutex`) loses it. (2) Every object a slot captures by reference or raw pointer outlives the emission: the snapshot is taken before slots run and a plain disconnect does not drain in-flight slots, so a slot can execute during or after its own disconnect. Require an explicit lifetime guard — Boost.Signals2 slot tracking (`slot::track`/`track_foreign` with a `weak_ptr`, which keeps the target alive for the call and skips expired slots) or external join/drain ordering for untracked captures — and treat destruction of a captured object during a possible concurrent emission as `CRITICAL` use-after-destruction.
- When `std::thread` may be destroyed joinable (exceptions between spawn and join), require `std::jthread`, a join-in-destructor wrapper, or scope-exit join; `detach` requires a written lifetime argument for everything the thread touches.
- When hot atomics or mutexes are written by multiple threads, check placement: distinct frequently-written items sharing a cache line (false sharing) is a performance finding, not correctness; report it as `LOW`, or `MEDIUM` when measurements show material impact.

## Checklist

### Shared State And Races

- Every shared mutable object has one named synchronization regime, and all accesses (including reads, including during shutdown) follow it.
- No mixed atomic/non-atomic access to the same memory; no `volatile`-as-synchronization.
- Objects published to other threads are fully constructed before publication, and publication uses a release/acquire edge or a mutex.
- Cross-thread observer/callback dispatch is race-free on the callback container (verified, not assumed: Boost.Signals2's default mutex provides it; a `boost::signals2::dummy_mutex` policy or an unsynchronized hand-rolled list does not), and every slot-captured object outlives the emission via slot tracking or join/drain ordering (a slot can run during or after its own disconnect).

### Locks And Ordering

- Multi-mutex acquisition follows a fixed global order or uses `std::scoped_lock`; no lock is held across calls into unknown code without justification.
- Lock hold times are bounded: no blocking I/O, no unbounded waits, no allocation-heavy work under contended locks unless accepted.
- Recursive locking is absent or explicitly justified with `recursive_mutex` and a documented reason.

### Condition Variables

- Every wait uses a predicate loop under the mutex that protects the predicate state.
- Every state change that can satisfy a predicate is followed by the matching notify; no notify is issued before the state change is visible under the mutex.
- Shutdown sets a stop flag under the mutex and notifies all waiters; no waiter can sleep through shutdown.

### Atomics And Ordering

- Each atomic has a stated role and protocol; memory orderings implement that protocol correctly (release-store paired with acquire-load on the same object).
- No ABA-prone compare-exchange without a counter/tag where reclamation is possible; `compare_exchange_weak` loops handle spurious failure.
- Fences, if any, are paired and documented; no standalone `atomic_thread_fence` without its partner.

### Thread Lifecycle And Shutdown

- Every spawned thread is joined on every path (including exceptions), or detachment carries a written lifetime argument.
- Shutdown order is explicit: stop intake, wake waiters, drain or cancel in-flight work, join, then destroy shared state.
- When teardown uses more than one flag (e.g. hard-close vs graceful-drain), in-flight completions check the one flag that every close path sets; guarding on only the graceful flag lets error-path closes slip through.
- `thread_local` objects with destructors are not relied on after thread exit, and their destruction order across threads is not assumed.

### Tests

- Each fixed race/deadlock class has a regression test that fails without the fix under TSan or deterministic interleaving (barriers, latches, controlled schedules); stress-only tests are recorded as weaker evidence.

## Severity And Verdicts

- `CRITICAL`: a data race on reachable shared state, a deadlock reachable in normal operation, or a use-after-destruction across threads.
- `HIGH`: a race or ordering bug requiring a narrow timing window, specific core count, or shutdown path; a CV protocol that can lose wakeups under load without any data race (a CV bug that includes a data race on predicate state is `CRITICAL`).
- `MEDIUM`: missing documented lock order, unbounded lock hold time, unjustified detach, measured false sharing, or a test gap on previously fixed classes.
- `LOW`: unmeasured false sharing, naming/clarity of synchronization intent, or hardening with no current incorrect execution.

Verdicts:

- `BLOCK`: missing required context, any `CRITICAL`, or any unmitigated `HIGH`.
- `CONCERNS`: any unmitigated `MEDIUM`, or remaining `HIGH`/`MEDIUM` findings that each have a compensating control, accepted tradeoff, or bounded reachability.
- `CLEAN`: every applicable checklist item holds and regression tests cover fixed classes; `LOW`-only findings do not block `CLEAN` and are listed as findings. If no classes were fixed, Tests is n/a and does not block `CLEAN`. For design-stage targets with no code or tests yet, the best achievable verdict is `CONCERNS` with test expectations recorded per finding.

## Output Format

```text
Verdict: BLOCK | CONCERNS | CLEAN
Target: <files, diff, design, or data structure>
Shared state: <items and their claimed regimes>
Thread topology: <threads, spawn/join/detach, shutdown order>

Findings:
1. <short title>
  Severity: CRITICAL | HIGH | MEDIUM | LOW
  Classification: Confirmed issue | Likely risk | Open question | Accepted tradeoff | Test gap
  Evidence: <file:line, diff hunk, or design sentence>
  Rule: <shared-state | locks | condition-variables | atomics | lifecycle | tests>
  Risk: <which interleaving breaks and what it corrupts>
  Required guard: <synchronization or lifecycle change>
  Test expectation: <TSan/deterministic test or N/A>

Checklist status:
- Shared state and races: covered | missing | n/a
- Locks and ordering: covered | missing | n/a
- Condition variables: covered | missing | n/a
- Atomics and ordering: covered | missing | n/a
- Thread lifecycle and shutdown: covered | missing | n/a
- Tests: covered | missing | n/a

Residual risk: <remaining caveats or None>
```

`Rule:` values map to checklist sections as follows: `shared-state` -> Shared State And Races; `locks` -> Locks And Ordering; `condition-variables` -> Condition Variables; `atomics` -> Atomics And Ordering; `lifecycle` -> Thread Lifecycle And Shutdown; `tests` -> Tests.

When no material issues exist, write exactly `Findings: None` (allowed only with `CLEAN`) and list assumptions under Residual risk. For design-stage targets that earn `CONCERNS` solely because tests cannot exist yet, emit one `Test gap` finding with `Rule: tests` listing the required test expectations instead of an empty findings list.

Insufficient-context mode: when the target or shared-state/thread topology cannot be established, emit exactly this reduced template and stop; do not emit shared state, thread topology, or checklist status with guessed values:

```text
Verdict: BLOCK
Target: <files, diff, design, or data structure>

Findings:
1. <missing-context short title>
  Severity: LOW
  Classification: Open question
  Evidence: <which required context is missing>
  Rule: <shared-state | locks | condition-variables | atomics | lifecycle | tests>
  Risk: <why no safe conclusion is possible>
  Required guard: <what context must be supplied>
  Test expectation: N/A
```

## Examples

- Lost wakeup: producer sets `ready = true` without the mutex, then `notify_one()`; consumer checks `ready` under the mutex and waits. The write can land between check and wait — the consumer sleeps forever. Fix: mutate `ready` under the same mutex.
- Lock-order deadlock: `transfer(a, b)` locks `a.mtx` then `b.mtx`; a concurrent `transfer(b, a)` locks in the opposite order. Fix: `std::scoped_lock lk(a.mtx, b.mtx);` or order by address/id.
- Destruction race: a worker thread calls `owner->on_done()` while the owner's destructor runs on another thread. Fix: join the worker in the destructor before members are torn down, or hand the worker a `weak_ptr` it must lock.
- Cross-thread slot lifetime: thread A emits a Boost.Signals2 signal whose slot captures `this` by raw pointer; thread B calls `connection::disconnect()` then destroys the captured object. The slot was already snapshotted, so it runs after disconnect on the now-dead object. Fix: connect with slot tracking (`sig.connect(decltype(sig)::slot_type(...).track_foreign(self_weak_ptr))`, where `slot_type` is the signal's own nested slot type) so emission keeps the target alive and skips it once expired, or order destruction to drain in-flight emissions.

## Definition Of Done

A concurrency change is ready only when:

- Every shared mutable object has a named regime and all accesses follow it (per the Shared State And Races checklist).
- Lock ordering, CV protocols, and atomic protocols satisfy their checklist sections.
- Every thread's join/detach story and the shutdown order are explicit.
- Regression tests or TSan coverage exercise each fixed class; absence of fixed classes makes Tests n/a.
