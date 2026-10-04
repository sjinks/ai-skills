Read before judging or writing a test; this reference defines all six gating dimensions and common failure patterns.

## The Quality Checklist

Audit each test against these. Any failure is a finding.

### 1. It asserts, and it can fail
- There is at least one assertion that depends on the behavior under test. A test that only constructs objects and never asserts is a no-op.
- The assertion can actually fail: not a tautology (`EXPECT_EQ(x, x)`), not comparing a value to itself, not asserting a constant the code never influences. Sanity check: would this test fail if the implementation were deleted/inverted? If not, it is worthless.

### 2. It targets behavior, not incidental detail
- Assert on observable contract (return value, wire output, emitted error, state transition), not on private internals, call counts, log strings, or formatting that the contract does not promise.
- Over-mocking smell: if the test mostly asserts "method X was called", it tests the implementation's shape, not its behavior, and will break on harmless refactors. Prefer asserting the *effect*.
- Byte/structure-exact assertions are good when the contract *is* exact (e.g. a differential oracle for serialized output); they are bad when they pin an unpromised detail.

### 3. It is deterministic
- No `sleep`/fixed-delay waits for async work. Wait on the actual condition: a latch/promise/future signalled by the callback, or a **time-bounded** poll on the condition with a generous timeout (`wait_for_*`). The timeout itself should run off a monotonic/steady clock, not the wall clock / real time of day. A loop bounded by an *iteration count* (`for (i<N) yield()`) is **not** deterministic — its budget can be exhausted before the event fires under parallel/sanitizer load, so it is itself a flake source, not an acceptable wait.
- No dependence on real time of day, timezone, locale, RNG without a fixed seed, network availability, filesystem ordering, or hash-map iteration order.
- Timeouts used as *probes* (deliberately short to force a deadline) are fine; timeouts used as *hopes* (sleep long enough and assume it finished) are not.

### 4. It is isolated
- No order dependence: the test passes run alone and in any order. No reliance on state a sibling test left behind.
- Shared/global/static state touched by the test is reset (fixture setup/teardown), and external resources (ports, temp files) are unique per test (e.g. ephemeral `port 0`, a temp dir) and cleaned up.
- Fixtures are deterministic and synthetic; no production data, real certs, secrets, or live endpoints.

### 5. It covers the negative and boundary paths it claims
- For a behavior with error/edge cases, there is a test that exercises the failure path and asserts the *specific* error/classification, not just "it didn't crash".
- Boundary values (empty, zero, max, off-by-one) for the behavior under test are present or explicitly out of scope.

### 6. It is legible as a spec
- The test name states the behavior and expected outcome; a reader learns the contract from the name + assertions without reading the implementation.
- One behavior per test (or clearly enumerated cases via parameterization), so a failure points at one cause.

## Anti-Patterns

- Approving a test because it is green, without checking it can fail.
- Asserting on mock call counts / log text / private fields instead of the observable effect.
- `sleep`-then-assert for async work instead of a latch or a time-bounded poll on the condition (and an iteration-count spin like `for (i<N) yield()` is no better — it flakes under load).
- Order-dependent tests or shared global state without reset.
- A "happy path only" test for a behavior whose error path is the actual risk.

## Severity and Scope

Treat inability to detect the promised regression and non-determinism as high
priority; behavior or claimed-coverage gaps as medium priority; readability
alone as low priority. These priorities order findings; the core checklist
controls the verdict. For writing one preselected test, keep other behaviors
explicitly outside the requested case instead of selecting additional cases.
