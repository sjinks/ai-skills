---
name: cpp-server-hardening-review
description: "Use when: reviewing, designing, or hardening a C++ network server (HTTP/TLS/socket) against connection-holding DoS, resource exhaustion, weak crypto defaults, and per-connection state leaks; deciding safe defaults for timeouts, connection caps, TLS minimums; or ensuring guaranteed teardown and bounded caches under untrusted load."
argument-hint: "Describe the server component, the option/default to review, or the DoS/resource concern to assess."
user-invocable: true
---

# C++ Server Hardening Review

Use this skill to review or design a network server (or its options surface) for **safe-by-default** behavior against untrusted clients: every connection must be time-bounded, count-bounded, and reclaimed deterministically, and crypto/protocol defaults must fail closed. The recurring failure mode it prevents is a server that is correct on the happy path but exhausts file descriptors, memory, or CPU under a trivial connection flood, or silently negotiates weak TLS because a default was left to the linked library.

The governing rule: **a default-configured server must survive a hostile client that opens connections and does nothing.** Unbounded time, unbounded count, and unreclaimed per-connection state are defects, not tuning knobs.

**WORKFLOW SKILL.** INVOKES: read-only inspection of the server's accept loop, session lifetime, option defaults, and TLS context setup. This skill judges *whether* the server is safe-by-default; defer the underlying mechanics (async-I/O event loop, HTTP parser behavior, TLS library calls) and the lifetime/threading correctness of any proposed fix to the appropriate stack/correctness review. FOR SINGLE OPERATIONS: assess one default or one teardown path directly against the checklist.

## Scope

- Use this skill for: choosing/auditing request-phase and idle timeouts, connection caps and accept backpressure, TLS minimum-version and verification defaults, guaranteed per-connection teardown notifications, and bounded per-connection/per-id caches.
- Out of scope: the protocol parsing rules themselves (an HTTP-parser concern), the async/lifetime mechanics of a fix (an async-I/O and object-lifetime concern), and application authn/authz logic. Name these when a finding depends on them, but route the mechanics elsewhere.

## The Hardening Checklist

### 1. Every connection is time-bounded by default

- The **first** request must be time-bounded, not only keep-alive follow-ups. A header-read timer that arms only after `requests_seen > 0` leaves the initial slowloris read unbounded.
- Ship **non-zero default** request-phase timeouts (e.g. headers 60 s, body 300 s). Zero may still mean "disabled", but the shipped default must bound the phase; document zero as a slowloris risk.
- Verify the timer is actually armed on the path you claim: trace `arm_*_timer` and confirm the first-request branch fires when the default is non-zero.
- Idle keep-alive also needs a finite default (e.g. 5 s).

### 2. Every connection is count-bounded (cap + backpressure)

- The hard `max_connections` cap is **defense-in-depth, not optional**: even with the Section 1 time bounds reaping stalled connections, a flood of fast-handshaking clients can still pin every fd at once. A server with no cap at all is `at-risk`; ship a cap (it may be generous, and stays overridable).
- When the live count reaches the cap, **shed at accept** — do not construct a full session. Two shed mechanisms, with different reclaim requirements: (a) **accept-then-close** keeps the acceptor armed naturally; prefer it. (b) **pause accepting** (stop calling `async_accept`) requires an explicit resume: re-arm accepting when the live count drops, wired to the disconnect notification — otherwise capacity is never reclaimed.
- Expose the live count through a real accessor (not a test-only seam) so the accept loop can consult it.

### 3. Per-connection state is reclaimed deterministically

- Identify the **single guaranteed teardown path** — the socket-close action (e.g. `close_lowest_layer`) — and confirm *every* termination route reaches it: normal completion, client FIN/RST, parser/protocol error, timeout, **TLS handshake failure**, and server shutdown.
- Fire a guaranteed once-per-connection **`disconnect` notification** (distinct from the close action above) so consumers reclaim per-id state without relying on a request ever arriving. Three obligations:
  - Latch it so it fires **exactly once**.
  - Add a **destructor backstop** that fires it if it has not fired — this covers a session dropped before it ever enters a termination route (never-started/aborted-early), which the per-route plumbing does not see.
  - **Contain a throwing observer** so one consumer's exception cannot abort teardown or skip other consumers.
- Any map/cache keyed by a monotonic connection id is an unbounded leak if entries are removed only on the request/success path. Bound it (LRU/size cap or TTL) **and** remove on the `disconnect` notification.
- **Install-after-teardown leak** — audit every `shared_from_this` completion handler. Sub-points:
  - *Mechanism:* an async completion can run *after* teardown latched the connection closed and released its per-request slots. If it then re-installs per-request state that strong-captures the session (response/commit/stream handlers, a re-dispatched request), it re-forms a `session -> handle -> handler -> session` cycle that the latched teardown never breaks again — leaking the session and everything it owns.
  - *Trap (a):* a cancelled read can still complete **successfully** from already-buffered bytes, so cancellation does not prevent re-dispatch.
  - *Trap (b):* error-path teardown sets the *closed* latch **without** the *draining* flag, so a handler guarding only on "draining" is not protected.
  - *Fix:* every completion that re-dispatches or re-reads must early-return on the **closed** latch (not just draining).
  - *Scope (defect class):* guard the buffered-header completion, the keep-alive/streaming write completions, the handshake completion, and any `100-continue`/expectation re-dispatch — not just the one site a leak was observed at.
  - *Verify:* a connect-write-abort stress loop under LSan; confirm the test fails with the guard removed.

### 4. Crypto and protocol defaults fail closed

- Pin a **minimum TLS version** (1.2) for both client and server when the caller does not set one; do not inherit whatever the linked TLS library build permits. Keep it overridable.
- Client TLS verification (chain + hostname) is on by default; the only disable path is an explicit, named opt-out.
- Per-SNI / per-context cert selection must re-apply the verify mode after switching contexts.

### 5. Bounds are enforced while reading, not after buffering

- Body/header/target limits fire during the read, not after the whole input is in memory. Confirm the limit is wired to the parser, not just validated post-hoc.

## Review Procedure

1. Locate the accept loop, the session constructor/teardown, the options struct with its defaults, and the TLS context setup.
2. Walk each checklist section against the code; for each item, cite the exact symbol/default and mark one of `safe` / `at-risk` / `missing` / `missing-evidence`. Use `missing-evidence` (never `safe`) when a section's code was not supplied, and state what to inspect — do not infer a passing status from absence.
3. For every `at-risk` or `missing` item, state the concrete failure a hostile client triggers (e.g. "1 fd + buffer + SSL state pinned forever per stalled connection") and the minimal fix. For a `missing-evidence` item, state what code to inspect to resolve it.
4. For each proposed fix, name the verification: a focused test (stalled-first-request closes within the bound; over-cap connection is shed; `disconnect` fires once including on handshake failure and on no-request; bounded cache evicts) plus the lifetime/concurrency check to confirm the fix is itself safe.

## Output

Return a hardening report: one row per checklist item with status (`safe` / `at-risk` / `missing` / `missing-evidence`), evidence (symbol/default), the hostile-client failure if not safe, the minimal fix, and the verification. Lead with the blocking items (unbounded time or count, unreclaimed state, weak default that fails open).

## Anti-Patterns

- Treating unbounded timeouts/caps as "operator's responsibility" without shipping a safe default or prominent documentation.
- Arming the request timer only for keep-alive follow-ups, leaving the first request unbounded.
- Removing per-id cache entries only on the success path while the id is monotonic.
- Letting the TLS minimum version default to the linked library's policy.
- Adding a `disconnect` notification that can double-fire, miss the handshake-failure path, or throw out of a completion handler.
- Re-installing strong-capturing per-request state from a completion that runs after the connection is closed (install-after-teardown), re-forming the ownership cycle the latch already broke.
