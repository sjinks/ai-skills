# cpp-server-hardening-review

> Use when: reviewing, designing, or hardening a C++ network server (HTTP/TLS/socket) against connection-holding DoS, resource exhaustion, weak crypto defaults, and per-connection state leaks; deciding safe defaults for timeouts, connection caps, TLS minimums; or ensuring guaranteed teardown and bounded caches under untrusted load.

This skill reviews a C++ network server (or its options surface) for **safe-by-default** behavior against untrusted clients. The governing rule: a default-configured server must survive a hostile client that opens connections and does nothing — unbounded time, unbounded count, and unreclaimed per-connection state are defects, not tuning knobs. It is standalone: it judges *whether* the server is safe-by-default and routes the underlying mechanics (event loop, parser, TLS calls, fix lifetime/threading correctness) to the appropriate stack/correctness review.

It helps an assistant:

- confirm every connection is time-bounded by default, including the **first** request (not just keep-alive follow-ups), with non-zero shipped request-phase and idle timeouts
- confirm every connection is count-bounded with a default-on `max_connections` cap (defense-in-depth, not optional) that **sheds at accept** under backpressure, re-arming the acceptor as connections close
- confirm per-connection state is reclaimed on a **single guaranteed teardown path** that every termination route reaches (including TLS handshake failure), with a once-only `disconnect` latch, a destructor backstop, and bounded per-id caches
- catch the install-after-teardown leak class, where an async completion runs after teardown and re-forms a strong-capture cycle the latch never breaks again — guarding every `shared_from_this` re-dispatch site on the **closed** latch, not just the one where a leak was first seen
- confirm crypto/protocol defaults fail closed: pinned minimum TLS version, verification on by default with only a named opt-out, verify-mode re-applied after per-SNI context switches
- confirm bounds are enforced **while reading**, wired to the parser, not validated after buffering
- emit a `Verdict: BLOCK | CONCERNS | CLEAN` hardening report: severity-tagged findings (per-item status `at-risk`/`missing`/`missing-evidence`, the hostile-client failure, the minimal fix, and the verification), a per-section checklist-status block, a `Findings: None` clean path, and a deterministic insufficient-context BLOCK template

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
