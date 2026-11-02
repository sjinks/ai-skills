When to read: during every audit, after scope selection and before drawing conclusions about test adequacy.

# Diagnostic Checks

Apply every dimension; record assessed evidence, inapplicability with a reason, or unreviewed scope. The core owns severity, completion, and checklist gates. The report contract owns fields and Evidence status; descriptive strength terms here are not report enums.

## Environment and harness

Inspect relevant production code, tests, helpers, fixtures/factories, setup, runner/coverage configuration, dependency substitution, lifecycle scripts, parallelism, and CI commands. Infer language/framework conventions.

Record revision/workspace state, requested/resolved runtime and dependency versions, commands, profiles, skips, and exclusions. Separate bootstrap failures from demonstrated product defects. Trace requested version, target, and options into the executed runtime. Reduced-profile success cannot validate the default profile.

Trace environment forwarding through wrappers/containers, option precedence, cached-image versions, test selection, and disabled groups. A requested setting or successful smoke test does not establish that the intended configuration or broader suite ran.

Inventory every declared test file and affecting helper/harness/configuration as reviewed, unreviewed, or excluded with a reason. Identify omitted neighbors in scoped work. Risk determines depth, not silent omission.

For exhaustive requests, assess every applicable dimension for each inventoried file. Shared helper/harness evidence may cover multiple files only when that relationship is established. Track remaining files and unresolved candidates between file groups. For each candidate, inspect the relevant implementation, challenge alternative explanations, and check implicated sibling tests/paths for the same cause; retain only supported material findings.

Trace local/external lifecycle modes, resource ownership, unique run identifiers, and cleanup on success/failure. A hook name does not establish that cleanup runs after failure. Never destroy an existing test site to verify cleanup.

## Contracts, composition, and coverage

Establish expected behavior from requirements, documented interfaces, user decisions, or independently justified invariants. Code alone cannot define correctness; unresolved product decisions remain uncertainty.

Prioritize authorization/privilege boundaries, validation, command/query dispatch, filesystem/network effects, parsing/deserialization, secrets/cryptography, financial state, persistence, destructive operations, retries/idempotency, concurrency, and partial-failure recovery.

Map each important contract:

```text
must happen / must not happen
→ real entry point and registration/dispatch
→ actual test arguments and subject
→ observable boundary effect
→ assertion
→ plausible fault the assertion rejects
```

Identify substitutions: test-installed hooks, direct callbacks, mocked subject methods, manufactured queue/checkpoint state, bypassed transport. Isolated helper tests cannot establish missing production wiring. Check public defaults, omitted options, and supported nulls; always-overridden fixtures leave defaults unprotected.

Trace producer output into the real consumer: generated challenge to validation, scheduled payload to handler, persisted checkpoint to a fresh reader. Independently seeded consumer fixtures do not establish compatibility. For signatures/tokens, check independent expectations, key dependence, freshness, and scope where contractual; self-generated roundtrips alone can hide a shared defect.

Keep line/statement/branch/function coverage separate from behavioral protection and fault detection. Use coverage to navigate, not to infer assurance. Describe behavioral evidence as strong, partial, weak, or absent with a reason.

## Guards, providers, and boundaries

For rejection fixtures, begin with a valid positive control and vary only the intended guard's input. Trace evaluation order to detect unrelated denial/type errors. Check competing grant/deny conditions, disabled features with environment grants, and blocked parents with enabled children.

Prove fixture prerequisites: duplicate-path rows actually collide, a resource exists before deletion, an initially active object can deactivate, and an early-return fixture would otherwise do observable work. Nonempty output alone cannot establish a fail-closed or unpredictable fallback contract.

Distinguish wrong identity, permission, nonempty credential, expiry, and scope; empty-input rejection does not establish them all. If removing a guard leaves an equivalent layered defense, state which guard is established. Defense-in-depth is not itself defective.

Trace provider row → bound arguments → subject input → independent expectation. Check arity, positional/named binding, nesting, ignored arguments, and unused expected values. Do not credit advertised cases that never reach the subject. Split multiple pairs when only one is consumed.

Check meaningful partitions: below/at/above; absent/empty/single/multiple; unauthorized/minimally/fully authorized; initial/valid/invalid/repeated transition. Many rows are not automatically independent evidence; value differences may encode important boundaries. Do not demand cases without a contractual distinction.

## Assertions, helpers, and failure effects

Trace operands to their origins. Actual values come from the subject/boundary; expectations are independent of actual output and the production algorithm under test. Detect fixture-to-itself comparisons, result-derived expectations, copied algorithms, and omitted contractual fields/types.

Check comparison-helper semantics: keys, types, multiplicity, and contractual ordering must survive normalization. Assert complete call tuples rather than truthy expected values or counts alone. Use raw persisted state when actor-filtered getters could conceal a write.

Choose inputs that distinguish required transformations: benign text alone may not reveal missing escaping or sanitization. Preserve permitted output while checking prohibited content.

An assertion may be strong (observable invariant), moderate (meaningful but partial constraint), weak (existence/non-null/no exception), or tautological (setup/mock/algorithm compared with itself). These are reasoning descriptions. Simple assertions and invariant-based oracles can be sufficient; exact equality is not always required.

Observe “after” after the action. Prove callbacks ran; capture actual generated paths/identifiers rather than sentinels. Seed disposable resources before asserting deletion. Use a fresh reader where same-instance state could hide missing persistence.

Find conditional assertions, empty loops, early returns, swallowed exceptions, dynamic skips, and catch blocks that convert failure into success. Verify missing required preconditions fail tests. Await asynchronous assertions and check terminal failure paths.

For relevant negative guarantees, assert both rejection and absence of prohibited effects: no dispatch, mutation, partial writes/output, secret disclosure, or duplicate irreversible operations. A failure signal alone may miss an earlier effect.

Inspect helpers that build expectations/commands, hide assertions, normalize output, generate fixtures, configure permissions, or seed/compare state. Challenge validators with absent/stale content, no-op actions, mixed class lists, exhausted retries, and unsuccessful saves. Distinguish browser-repaired DOM from raw/persisted content where contractual.

For browser success, check the expected status and application state; accepting every non-server-error status may admit missing pages. Check cancellation at the request/persistence boundary after work settles, rather than relying on an initially absent UI element.

## Mocks, external boundaries, and concurrency

Mocks at genuine boundaries are useful. Report only substitutions that materially weaken claimed evidence: mocked subjects, impossible states, duplicated production logic, success-only fixtures, or hidden integration/protocol errors.

Validate boundary fixture fields/types, IDs, canonical shapes, and status distinctions against interfaces/current implementation. Distinguish transport failure from application rejection. Trace retention, acknowledgement, retries, and duplicate processing.

Observe destructive targets at the actual external call; metadata/counts cannot establish the correct file, index, or tenant. Check relevant upload/stream bytes and destinations. Intercept boundary requests locally; live vendor calls are unnecessary for contract checks.

For fan-out, verify per-destination multiplicity and relevant method/body/credentials; an allowed URL set and total count can hide duplicate primary writes. Before queue removal/acknowledgement, establish the required downstream effect or defined rejection/retention policy.

Check lifetime and reuse at a capable boundary: immediate cache values or filtered interval metadata do not establish applied TTL/expiry. Equal repeat results do not prove avoided queries or computation; observe relevant work counters without replacing the subject.

For concurrency, identify the contested read/claim/write interleaving. Serial/nested calls and pre-mutated rows cannot establish atomicity. Authorized experiments use independent actors/connections, deterministic barriers, and an owned disposable backend shared by those actors. Assert exclusivity/ownership or admission bounds, not just final counts. Otherwise report concurrency unverified without inferring a race.

## Isolation, independence, and determinism

Check mutations of environment, working directory, globals/statics/singletons, registries/containers/module caches, clocks/timezones/locales, randomness, logging/signal handlers, files/databases/queues, networking, flags, mocks, and fake timers.

Verify original-state capture/restoration, cleanup after failure, concurrent visibility, and retained cache effects. Deleting an originally populated value or restoring an assumed default does not restore prior state.

Inspect framework-provided teardown before declaring a leak. Resetting a global does not remove an irreversible function/class definition; isolate such cases when needed rather than prescribing process isolation for the whole suite.

Inspect dependencies on previous tests, shared fixtures/caches, assumed rows, sequence IDs, leaked files/ports/mocks, and ordering. When requested and authorized, discriminate with isolated, repeated, reordered, or supported parallel execution; label unrun checks honestly.

Assess uncontrolled time/sleeps, thresholds, scheduling, randomness, services, shared databases, locale/timezone, machine speed, filesystem order, process IDs, temporary path formats, and environment settings. Separate intentional integration behavior from accidental nondeterminism. Prefer deterministic synchronization. Flakiness risk is not observed flakiness.

## Value, redundancy, snapshots, and cost

Identify the distinct plausible fault each test rejects. Detect tests that merely execute code, assert trivial existence, validate configured mocks, copy logic, or duplicate stronger evidence.

Redundancy is semantic: identify subsuming tests, equivalent inputs/observations, shared fault classes, and evidence removal would lose. A subset of assertions is a lead, not proof across different boundaries. Preserve distinct historical regressions, diagnostic purposes, and useful integration evidence.

Search neighboring test layers before broad inadequacy claims. Browser/integration tests may protect a unit-test gap; qualify findings by layer/profile and retain that protection.

Similar setup/code, shared paths, or many parameter rows alone do not justify deletion. Recommend removal only after inspected evidence shows required protection remains; incomplete inability to identify value is insufficient. Consolidation must retain partitions and diagnostics. Fault-set overlap is a reasoning aid; executed mutations are not mandatory.

Inspect snapshot contract relevance, reviewability, automatic updates, incidental detail, and meaningful changes hidden in oversized captures. Structure alone need not prove semantics. Balance useful evidence against execution/maintenance cost; do not optimize for minimum test count or arbitrary coverage percentages.

Support cost findings with observed timings or clearly labeled source estimates. Separate aggregate matrix process time from elapsed CI time; do not recommend dropping compatibility/integration coverage without identifying protection retained elsewhere.

Use the report's categories precisely: Weak Test needs stronger observations; Low-Value Test needs a justified target or evidenced removal; Redundant Test needs subsuming evidence; Missing Test needs an uncovered guarantee. Isolation concerns interference; Determinism concerns uncontrolled variability; Misleading Coverage concerns execution mistaken for protection; Other requires explaining why no specific category fits.

## Semantic faults and coverage record

Reason about realistic faults: reversed/removed guards, boundary shifts, wrong identity/permission, fail-open errors, skipped validation, wrong records, premature/omitted/duplicate writes, swallowed errors, unsafe retries, dropped/reordered data, or omitted escaping. Name which assertion should fail. Source-backed predictions are Inferred, not observed survival. Follow the experiment protocol before execution.

In Audit scope, record these dimensions as assessed, inapplicable with reason, or unreviewed with reason:

- environment, harness, profiles, and inventory;
- contracts, composition, defaults, coverage types, guards, and providers;
- assertion provenance/timing, negative effects, and helper validators;
- mocks, targets/payloads, persistence, and concurrency;
- isolation, independence, cleanup, and determinism;
- snapshots, partitions, redundancy, and cost.

Unreviewed applicable dimensions leave inspection incomplete. Missing optional runtime evidence alone does not prevent Complete after finished static inspection.
