---
name: test-quality-review
description: "Use when: writing, reviewing, or auditing a test (not a test plan) for quality - tests with no assertion or that cannot fail, assertions on incidental implementation detail instead of behavior, sleep-based or clock/network-dependent non-determinism, shared-state leakage between tests, over-mocking, tautologies, and missing negative/error-path coverage."
argument-hint: "The test (or test file/diff) to audit or write, plus the behavior or AC it is meant to verify."
user-invocable: true
---

# Test Quality Review

Use this skill to judge whether a test is a *good* test — one that fails when the behavior breaks and passes only when it works. The recurring failure mode it prevents is a green suite that proves nothing: assertion-free tests, tests that assert on incidental implementation detail, flaky timing, and tests that can never fail. It is the test-code counterpart to auditing acceptance criteria: that judges the plan, this judges the test code itself.

The governing rule: **a test must be able to fail for exactly one behavioral reason, and that reason must be the thing it claims to verify.**

**WORKFLOW SKILL.** INVOKES: read-only inspection of the test and the code under test. This skill judges test *quality*; defer the choice of what to test to a test-planning concern, and the framework mechanics of expressing a fix to the project's test-framework conventions. FOR SINGLE OPERATIONS: audit one test against the checklist and return a verdict.

## Scope

- Use this skill for: reviewing or writing an individual test or a test file/diff for assertion quality, determinism, isolation, and behavioral (not implementation) focus.
- Out of scope: choosing *what* to test or coverage strategy (a test-planning concern), framework mechanics (a test-framework authoring concern), and root-causing an already-failing intermittent CI test (a separate flake-diagnosis concern). Name the boundary when a finding depends on it.

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

## Review Procedure

1. Identify the behavior/AC the test claims to verify.
2. Walk the six checklist sections; for each, mark `ok` / `weak` / `missing` with the line evidence.
3. Apply the killer question to the whole test: *would it fail if the behavior regressed?* If no, that is the top finding regardless of anything else (a `cannot-fail` verdict).
4. For each `weak`/`missing`, give the concrete rewrite (a real assertion, a latch instead of a sleep, an effect-based assertion instead of a mock call count, the missing error-path case).

## Output

If the caller requests specific section labels, follow them exactly. Otherwise use this default labeled format:

- `Verdict:` one of `solid` / `weak` / `cannot-fail`. Write the third token as `cannot-fail` (hyphenated) everywhere, including in prose.
- `Findings:` a list keyed to the checklist number, each with file/line and the concrete fix. Lead with any `cannot-fail` or non-deterministic finding (these drive a `cannot-fail`/`weak` verdict); behavioral-focus and coverage findings follow.

## Anti-Patterns

- Approving a test because it is green, without checking it can fail.
- Asserting on mock call counts / log text / private fields instead of the observable effect.
- `sleep`-then-assert for async work instead of a latch or a time-bounded poll on the condition (and an iteration-count spin like `for (i<N) yield()` is no better — it flakes under load).
- Order-dependent tests or shared global state without reset.
- A "happy path only" test for a behavior whose error path is the actual risk.
