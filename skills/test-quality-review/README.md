# test-quality-review

> Use when: writing, reviewing, or auditing a test (not a test plan) for quality - tests with no assertion or that cannot fail, assertions on incidental implementation detail instead of behavior, sleep-based or clock/network-dependent non-determinism, shared-state leakage between tests, over-mocking, tautologies, and missing negative/error-path coverage.

This skill judges whether a test is a *good* test — one that fails when the behavior breaks and passes only when it works. The governing rule: a test must be able to fail for exactly one behavioral reason, and that reason must be the thing it claims to verify. It is the test-code counterpart to auditing acceptance criteria (that judges the plan; this judges the test code), and is standalone: it routes what-to-test, framework mechanics, and CI-flake diagnosis elsewhere.

It helps an assistant:

- apply the killer question to every test — *would it fail if the behavior regressed?* — and treat a no as the top, blocking finding
- check the six quality dimensions: it asserts and can fail (no tautologies/no-ops); it targets observable behavior not incidental detail (no over-mocking on call counts/logs/private fields); it is deterministic (no sleep-based or clock/network/RNG/iteration-order dependence); it is isolated (no order dependence or shared-state leakage, ephemeral resources, synthetic fixtures); it covers the negative/boundary paths it claims; and it reads as a spec (name states the behavior, one behavior per test)
- mark each dimension `ok` / `weak` / `missing` with line evidence and give the concrete rewrite (a real assertion, a latch instead of a sleep, an effect-based assertion instead of a mock call count, the missing error-path case)
- return a per-test verdict (`solid` / `weak` / `cannot-fail`) leading with cannot-fail and non-determinism findings as blocking

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
