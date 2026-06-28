# flaky-test-diagnosis

> Use when: a test passes and fails non-deterministically (flaky), fails only under load/parallelism/sanitizers, fails in CI but not locally, or fails depending on run order - diagnosing timing races, order dependence, shared global state, unseeded RNG, real-clock/timezone/locale reliance, real network/filesystem dependence, and hash/iteration-order assumptions, then making it deterministic.

This skill turns a non-deterministic test into a deterministic one by finding *why* it sometimes fails, not by retrying it until it passes. The governing rule: a flaky test is a bug report — either the test races/leaks, or the code does; find which, then remove the non-determinism at its source. It is standalone: it routes the underlying concurrency/lifetime fix and test-authoring mechanics to the appropriate review rather than masking the flake.

It helps an assistant:

- reproduce deterministically first — elevate the failure rate with repeat runs, shuffled order, high parallelism, and sanitizers — and capture the failing seed/order/output before attempting any fix
- classify the observed flake against a symptom → cause → deterministic-fix table (order dependence, shared external resource, premature async assertion, real-clock/timezone/locale, unseeded RNG, unordered-iteration assumption, real data race)
- distinguish a test bug from a code bug: a sanitizer-only or crash/hang flake is the test doing its job and must be escalated, not stabilized away
- remove the non-determinism at the source (deterministic wait, isolated ephemeral resource, injected clock, seeded RNG, reset state) — never by lengthening a sleep, adding a retry wrapper, or disabling the test
- prove the fix by re-running the original reproduction under the same repeat/shuffle/parallelism/sanitizer conditions
- report the reproduction, the classified root cause, the source-level fix, and the post-fix verification

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
