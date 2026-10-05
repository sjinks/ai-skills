# test-quality-review

> Audit test code or write one caller-preselected test for assertion quality, determinism, isolation, and behavioral focus.

This skill judges whether a test is a *good* test — one that fails when the behavior breaks and passes only when it works. The governing rule: a test must be able to fail for exactly one behavioral reason, and that reason must be the thing it claims to verify. It is the test-code counterpart to auditing acceptance criteria (that judges the plan; this judges the test code), and is standalone: it routes what-to-test, framework mechanics, and CI-flake diagnosis elsewhere.

It owns writing one test whose behavior and expected result the caller already selected. Feature case selection and implementation of that selected set belong to the feature testing workflow, including sets of one. Available dedicated framework workflows take precedence for writing.

It helps an assistant:

- apply the killer question to every test — *would it fail if the behavior regressed?* — and treat a no as the top, blocking finding
- check the six quality dimensions: it asserts and can fail (no tautologies/no-ops); it targets observable behavior not incidental detail (no over-mocking on call counts/logs/private fields); it is deterministic (no sleep-based or clock/network/RNG/iteration-order dependence); it is isolated (no order dependence or shared-state leakage, ephemeral resources, synthetic fixtures); it covers the negative/boundary paths it claims; and it reads as a spec (name states the behavior, one behavior per test)
- mark each dimension `ok` / `weak` / `missing` with line evidence and give the concrete rewrite (a real assertion, a latch instead of a sleep, an effect-based assertion instead of a mock call count, the missing error-path case)
- return a per-test verdict (`solid` / `weak` / `cannot-fail`) leading with cannot-fail and non-determinism findings as blocking

## Files

- [`SKILL.md`](SKILL.md) — the operational skill definition.
- [`references/report-contract.md`](references/report-contract.md) — conditional report grammar and honest locations.
- [`references/quality-checklist.md`](references/quality-checklist.md) — six gating quality dimensions and failure patterns.

Authoring reports put generated code under `Authored test:` after the verdict
and findings. Findings cite real reviewed files or supplied/generated snippet
lines; authoring does not require an existing file. The suite-local deterministic
validator checks both review and authoring branches plus a missing-context eval that requests the absent expected behavior and emits no invented code.
Live model behavior remains unmeasured.

Writing accepts an existing draft or no test body. The authoring eval rewrites
a supplied no-op draft while constructing the required setup and assertion.
Bulk reviews emit one report per test in input order; the validator checks
report count and individual verdicts. A separate negative case covers an
available framework-authoring workflow.

All initially empty positive read-only workspaces remain empty under the shared
final-state guard `evals/_helpers/check-empty-workspace.py`. This includes
blocked/missing context and returned-snippet authoring where applicable. It
rejects all entries, including hidden files, empty directories and symlinks.
It does not observe transient changes, changes outside the workspace, or
changes restored before grading.

The suite projection check binds text verdict assertions to the program-selected verdict for review, authoring, and missing-context reports. Static checks do not establish model behavior.
