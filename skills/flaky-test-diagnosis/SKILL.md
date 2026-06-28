---
name: flaky-test-diagnosis
description: "Use when: a test passes and fails non-deterministically (flaky), fails only under load/parallelism/sanitizers, fails in CI but not locally, or fails depending on run order - diagnosing timing races, order dependence, shared global state, unseeded RNG, real-clock/timezone/locale reliance, real network/filesystem dependence, and hash/iteration-order assumptions, then making it deterministic."
argument-hint: "The flaky test (name/file) and any signal: how often it fails, under what conditions (parallel, sanitizer, CI, specific order), and the failure output."
user-invocable: true
---

# Flaky Test Diagnosis

Use this skill to turn a non-deterministic test into a deterministic one by finding *why* it sometimes fails, not by retrying it until it passes. The recurring failure mode it prevents is "fix" by `sleep` increase, retry annotation, or disabling — all of which hide the defect (which is sometimes in the *code*, not the test) and erode trust in the suite.

The governing rule: **a flaky test is a bug report — either the test races/leaks, or the code does. Find which, then remove the non-determinism at its source.**

**WORKFLOW SKILL.** INVOKES: build/run tooling to reproduce (repeat runs, shuffled order, parallel, sanitizers), read-only inspection of the test and code under test. Apply the deterministic-wait patterns of the project's test framework to express the fix, and hand a confirmed data race or lifetime bug to a concurrency/object-lifetime review rather than masking it. FOR SINGLE OPERATIONS: classify one observed flake against the source table and name the fix.

## Scope

- Use this skill for: reproducing and root-causing an intermittently failing test and making it deterministic, or escalating to a real code defect when the test correctly caught a race/leak.
- Out of scope: authoring a new test from scratch (a test-framework authoring concern), judging whether a consistently-passing test is a *good* test (a separate test-quality-judgement concern), and fixing the underlying concurrency/lifetime bug itself once identified (a concurrency / object-lifetime review concern). Name the boundary when a finding depends on it; route the work accordingly.

## First: reproduce deterministically

Do not trust a single green run. Increase the failure rate until you can observe it:

- Repeat: run the single test many times (`ctest -R <name> --repeat until-fail:N`, or a loop). A flake that needs 100 runs is still a flake.
- Shuffle order: run the suite shuffled (`--gtest_shuffle`, vary `--gtest_random_seed`) to expose order dependence.
- Parallelize: run with high `ctest -j` to expose shared-resource races (ports, temp files, globals). Parallel/sanitizer load also starves event loops: a bounded `for (i<N) yield()` poll that passes solo can exhaust its budget under `-j` before the awaited event fires.
- Sanitize: the project's `sanitizer` preset is **ASan + UBSan + LSan** (it does *not* include TSan; ASan and TSan are mutually exclusive). ThreadSanitizer is a **separate** build via the `tsan` (GCC) or `tsan-clang` (Clang) preset. A flake that only appears under ASan/LSan/TSan is usually a *real* code bug, not a test bug.
  - GCC's TSan can abort with `FATAL: ThreadSanitizer: unexpected memory mapping` under high-entropy ASLR; prefix the binary (and `gtest_discover_tests`) with `setarch -R`. Clang's TSan runs without that workaround and, in practice here, surfaced a race on its first full pass that GCC's full pass missed (GCC needed a targeted `--gtest_repeat`). When a race is suspected, run **both** compilers' TSan.
- Capture the failing seed/order/output. A flake you cannot reproduce, you cannot prove fixed.

## Source classification

Map the observed behavior to a cause and a source-level fix (not a sleep/retry):

| Symptom | Likely cause | Deterministic fix |
|---|---|---|
| Fails depending on test order | Shared global/static state, leaked singleton, unreset fixture | Reset state in fixture setup/teardown; remove the global; isolate per test |
| Fails under `-j` / parallel only | Shared external resource (fixed port, temp path, file) | Ephemeral resource per test (`port 0`, unique temp dir); no fixed ports |
| Async assertion sometimes too early | `sleep`/fixed-delay wait, or a **bounded** `for (i<N) yield()` poll, racing real completion | Wait on the event itself: a latch/promise/future signalled by the callback, with a generous timeout. A bounded yield/poll loop is itself a flake source under parallel/sanitizer load — it is not a fix |
| Fails by time of day / machine / CI region | Real clock, timezone, or locale dependence | Inject a fixed clock; pin timezone/locale; assert on relative not absolute time |
| Fails ~rarely with different values | Unseeded RNG / random inputs | Seed the RNG with a fixed value (and log it); or enumerate inputs |
| Order of results differs run to run | Hash-map / unordered iteration-order assumption | Sort before comparing, or assert set-equality, not sequence |
| Only under ASan/TSan, or rare crash/hang | **Real** data race, use-after-free, or deadlock in the code | Escalate to a concurrency / object-lifetime review; fix the code, keep the test |

The last row is the important one: a flake under the sanitizers is the test doing its job. Do not "stabilize" it away — fix the code.

## Procedure

1. Reproduce with elevated failure rate (repeat / shuffle / parallel / sanitizer) and record the trigger condition and seed/order.
2. Classify against the table from the *condition that triggers it* (order, parallelism, time, sanitizer), not from a guess.
3. Decide test-bug vs code-bug. Sanitizer-only or crash/hang flakes are real defects by default (usually in the code under test, occasionally in the test/fixture itself — a leaked fixture, a test-only overrun); fix at the source either way, never retry-mask. Escalate a code-under-test race/leak to a concurrency / object-lifetime review.
4. Remove the non-determinism at the source (deterministic wait, isolated resource, injected clock, seeded RNG, reset state) — never by lengthening a sleep, adding a retry wrapper, or disabling the test.
5. Prove it: re-run the original reproduction (same repeat count / shuffle seed / parallelism / sanitizer) and show it now passes consistently.

## Output

Return: the reproduction (how the flake was forced and how often it failed), the classified root cause (test-bug or code-bug, with the table row), the source-level fix, and the post-fix verification under the same reproduction conditions. If the cause is a real code defect, say so explicitly and hand it off to a concurrency/lifetime review rather than masking it.

## Anti-Patterns

- "Fixing" a flake by increasing a `sleep`, adding a retry/`--repeat` band-aid, or marking it disabled/known-flaky.
- Declaring it fixed after one green run instead of re-running the original reproduction.
- Treating a sanitizer-only failure as a test problem when it is a real race/leak in the code.
- Asserting on unordered-container iteration order or absolute wall-clock time.
