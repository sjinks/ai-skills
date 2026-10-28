# test-suite-audit

> Audit whether an existing automated test suite rejects plausible incorrect implementations and provides trustworthy behavioral evidence.

Test Suite Audit inspects a declared suite or group of tests, the relevant production contracts, and its helpers, harness, and runtime profiles. It distinguishes code coverage, behavioral protection, and fault-detection evidence. It is language- and framework-agnostic.

## Use

Supply the suite or test group, relevant requirements or known defect, and any requested execution. Inspection is the default. Whole-suite claims require an inventory of every in-scope test file and affecting helper/configuration; scoped reviews identify omitted neighbors.

An exhaustive request applies all relevant diagnostics across that inventory, follows candidate findings into implementation, and checks sibling tests/paths sharing the cause. The audit can proceed in file groups, but an initial batch or arbitrary finding count does not establish completion. All supported material findings are reported unless the caller limits output; unfinished coverage remains `Partial`. Exhaustive scope does not guarantee discovery of every possible defect.

```text
Audit the checkout tests against the documented ownership and retry contracts.
Inspect the harness, fixtures, assertions, and failure cleanup. Use static
inspection only, identify plausible faults the tests would miss, and report
the limits of the evidence.
```

This skill assesses existing suite adequacy and escaped defects. It excludes isolated single-test review, new-feature test authoring, running tests alone, and implementation fixes. It recommends remediation without applying it.

## Evidence and execution

Inspection traces real entry points, guard reachability, provider binding, independent assertions, boundary effects, persistence, and concurrency. It also assesses isolation, determinism, snapshots, redundancy, and cost.

Checks include producer-consumer compatibility, comparison-helper semantics, fixture prerequisites, actual request targets/payloads, cache lifetime/reuse, cancellation, framework teardown, neighboring test-layer protection, and measured versus estimated execution cost.

Execution is optional unless requested and uses only authorized disposable resources. Mutation claims require a matching passing baseline, a working behavioral control, verified runtime-visible edits and path activation, and cleanup verification. Source-only predictions remain inference. A survivor identifies a test gap rather than an existing deployed defect.

## Report

Every audit returns `Audit scope`, `Findings`, `Evidence table`, `Final assessment`, and `Audit status`. Findings distinguish `Test gap` from `Current defect`. Severity (`Critical`, `High`, `Medium`, `Low`) prioritizes test remediation rather than incident impact.

The terminal status measures completion:

- `Blocked`: artifacts cannot support meaningful inspection.
- `Partial`: meaningful inspection succeeded, but declared scope, candidate assessment, required references, or requested execution remain incomplete/unavailable/invalid, or experiment restoration/resource cleanup is unverified.
- `Complete`: declared inspection and requested execution are complete, with limitations recorded. This does not mean the suite is adequate or that unexercised runtime profiles passed.

Completed static inspection can be `Complete` when execution was not requested. Reports retain no-findings and insufficient-context branches. Row-level evidence statuses are separate from overall completion.

Markdown reports use inline code for paths, symbols, commands, and other technical literals so names such as `__tests__` render correctly. Linked paths use escaped plain-text labels; fenced code and report labels retain their existing form.

## Files

- [`SKILL.md`](SKILL.md) — activation, boundaries, workflow, severity, status precedence, and completion checklist.
- [`references/diagnostic-checks.md`](references/diagnostic-checks.md) — environment, contracts, assertions, boundaries, concurrency, isolation, redundancy, snapshots, and diagnostic coverage record.
- [`references/mutation-and-probe-protocol.md`](references/mutation-and-probe-protocol.md) — baseline/control, mutation activation, probes, claim scope, restoration, and evidence retention.
- [`references/report-contract.md`](references/report-contract.md) — finding fields, evidence enums, report cardinality, complete templates, and discriminating examples.
