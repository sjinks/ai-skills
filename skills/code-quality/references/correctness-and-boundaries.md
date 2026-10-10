When to read: when the target or relevant inspected context involves validation, errors, I/O, numeric or temporal values, encoding, shared state, tests, potentially costly work, or public evolution; also before every proposed edit.

# Correctness, verification, and change safety

Use these checks to expose concrete risks in the inspected code. They do not constitute a comprehensive security audit. Follow `SKILL.md` before editing; adding safeguards or changing failure semantics can change behavior.

## Validation and errors

- Trace untrusted data to its interpretation point. Check shape, domain constraints, and transformations at each trust boundary, including re-entry through persistence or external services.
- Before treating validation as redundant, establish all entry points, prior enforcement, mutation, and conversions. Keep assertions for internal invariants when they remain necessary. An assertion or non-null annotation alone does not prove the invariant.
- Check whether parsing results become a trusted representation, or whether callers continue handling a mixture of validated and raw values. Keep shared validators cohesive; split a sub-validator when it is reused or independently owns a boundary.
- Check whether callers can distinguish error categories needed for recovery, retry, reporting, or authorization. Retain structured details and original causes when wrapping errors. Do not require a particular exception or result type.
- Inspect broad catch blocks, silent fallback values, and log-only handlers for failures reported as success. Keep deliberate recovery and boundary logging when the contract supports them. Avoid exposing sensitive diagnostic details to unintended consumers.
- Look for real boundary safeguards required by the workload, such as deadlines, cancellation, access checks, and bounded request rates. Inspect shared clients, middleware, and infrastructure before concluding a safeguard is absent. Do not remove safeguards to reduce apparent defensive code.

## Values and representations

- For monetary or other precision-sensitive calculations, check units, numeric range, rounding policy, precision requirements, and conversion/display boundaries. Check currency compatibility when amounts carry currencies. Choose an adequate representation for the stated contract rather than prescribing one numeric type.
- For approximate numeric comparisons, check the intended equality and tolerance against scale and domain requirements. Exact comparison can be valid for exact quantities; a fixed epsilon is not a universal correction.
- Distinguish instants, calendar dates, local scheduled times, and durations. Check timezone and daylight-saving behavior where conversions or calendar arithmetic matter. Do not convert a date-only value into an instant without a contract.
- Check identifiers for domain confusion, precision loss, and unsupported ordering assumptions. Select identifier formats from interoperability and threat requirements; neither sequential nor random identifiers alone establish authorization.
- Check encoding at each interpreting boundary. Use the interpreter's safe construction mechanism and prevent missing or duplicate encoding. Confirm the applicable character-set contract rather than assuming every input is already normalized or escaped.

## Effects, lifetime, and concurrency

- For retryable operations, inspect delivery guarantees, deduplication scope, atomicity, and partial completion. Verify that a retry does not duplicate irreversible effects or incorrectly suppress a distinct request. Do not assume a method name, HTTP verb, or upsert alone makes a compound operation safe.
- For resources, trace acquisition, ownership, transfer, and release through success, failure, early return, and cancellation. Check rollback, listener/timer removal, subscriptions, and abandoned streams where those resources exist.
- Inspect operations sharing state for interleavings that violate invariants. Check synchronization or atomic operations against the invariant; do not infer safety from low expected frequency.
- Choose serial or concurrent work using dependencies, ordering guarantees, rate limits, and resource budgets. Bound concurrency when work can exceed those budgets. Sequential I/O is not automatically a defect.
- Check whether cancellation reaches active operations and whether abandoned work can still commit effects. Distinguish a timeout reported to the caller from actual cancellation of the underlying work.
- For optimistic updates, autosave, cache synchronization, or offline queues, check stale-result handling, rollback, pending/error states, conflicts, retry identity, and multiple writers. Require durable recovery only when the user-facing contract promises survival across restart or disconnection. Do not import a framework-specific queue or persistence mechanism.
- Check remote-state/cache identity against all inputs that distinguish results, including ownership or tenancy where applicable. Inspect mutation invalidation or reconciliation across affected views. Bound retry/replay work and preserve dependency ordering when required by the contract.
- During save completion or recovery, delete a retained draft or queued write only after confirmation that the same value or operation was committed. Settle request-in-flight indicators on success, failure, or cancellation without discarding unsaved data. This retention rule does not forbid explicit user-authorized discard. Check that stale completions and optimistic rollback preserve newer edits. For version-based conflict control, check atomic comparison and update rather than a separate check followed by an unprotected write.


Apply these checks within the requested code scope. Findings still require evidence and consequences under `SKILL.md`. This reference does not authorize new behavior, commits, PRs, or a repository-wide audit.

## Behavioral evidence

- Check whether an assertion fails for a plausible violation of the stated behavior. Use independently derived expectations rather than repeating the production algorithm. A no-throw assertion is useful only when absence of an exception is the behavior it claims to verify.
- Check outputs, state transitions, error outcomes, and externally visible interactions. Keep interaction assertions when those interactions are the contract; avoid pinning private helper names or incidental call order.
- Evaluate mocks and snapshots by what they establish. Do not count them as defects. Pair broad snapshots with discriminating assertions when the snapshot can pass while important behavior is wrong.
- Before accepting a changed snapshot or expected value, compare it with the intended contract. Do not regenerate an oracle merely to match changed output or discard a meaningful regression signal.
- Inspect shared fixtures, clocks, randomness, environment access, and execution order for isolation and determinism. Introduce controllable dependencies when needed; keep integration tests that intentionally exercise real boundaries.
- For user interfaces, check whether tests can identify controls by stable semantics and distinguish repeated elements. Missing accessible names can be a concrete usability/testability concern. Dedicated test identifiers remain valid when semantic identification is insufficient. Do not promise full accessibility certification.
- Preserve useful coverage when proposing replacement of a weak or outdated test. Distinguish static inspection from observed test results. Coverage percentages and complexity scores are signals, not proof of fault detection or quality.

## Performance and tradeoffs

- Inspect repeated queries, nested lookups, unnecessary repeated work, large buffers, and retained objects against expected data sizes and resource budgets. Select algorithms and data structures from the operation's actual workload and semantics.
- Check whether caching introduces invalidation, staleness, or ownership costs disproportionate to the observed need. Preserve intentional caching contracts and measured optimizations.
- Before claiming a speed or memory improvement, measure the affected workload with comparable conditions. For performance-critical contracts, retain the applicable benchmark or regression evidence. Do not prescribe micro-optimizations from source heuristics alone.
- When readability conflicts with demonstrated resource requirements, preserve correctness and the required budget, then minimize the resulting comprehension cost. Without such evidence, use the clearer idiomatic solution.
- When reuse conflicts with clarity, distinguish shared meaning from similar text. Reuse compatible existing behavior; do not force a helper that changes semantics or couples independently evolving concepts. Require actual variation or a boundary contract for new generalization, not a fixed caller-count rule.

## Evolution and reviewability

- Inspect callers and persisted/wire contracts before signature, shape, or enum changes. Check whether consumers tolerate new variants. Additive changes are not automatically compatible.
- For breaking evolution, require an explicit migration strategy appropriate to deployment and consumer coordination. Deprecation, coexistence, or an atomic migration can be valid; cleanup alone does not authorize a breaking change.
- Match established naming, organization, diagnostics, and testing conventions unless a concrete defect justifies departure. Do not preserve an unsafe pattern solely for symmetry.
- Keep structural cleanup separate from behavior changes and unrelated formatting. In legacy code, preserve observed behavior and characterize the affected contract before simplifying. Stop at the requested scope.
- Inspect placeholders, debug statements, unreachable code, and unused abstractions for actual consumers and runtime reachability. Keep intentional operational logging, reflective/plugin entry points, and tracked workarounds. Do not add or remove them to make code appear human-written.
- Distinguish an unfinished implementation placeholder from a documented future improvement. Report an unimplemented required path as a correctness issue; do not erase its marker as cosmetic cleanup.

## Proportional verification

Read this section for every proposed edit. The three classes and recovery rules in `SKILL.md` govern editing; these details determine the applicable checks.

- `Documentation` excludes executable examples, doctests, directives, annotations, generated-code markers, and comments consumed by tools. Establish that the text is ordinary prose. Review its accuracy and remaining contract documentation before and after editing; run relevant documentation or lint checks when the project requires them. Record manual inspection as inspection, not a test run.
- `Symbol` requires a closed set of bindings and consumers. Inspect exports, reflection, string-based lookup, serialization, configuration, and external consumers where applicable. A text search alone does not prove that set is closed. Use language-aware references or inspect every binding and use; run applicable compilation, analysis, and focused checks. Unknown consumers or observable names move the edit to `Behavior`.
- `Behavior` is the verification class for behavior-preserving edits to control flow, guards, defaults, data shapes, public contracts, effects, ownership, and algorithms. The baseline and post-change checks must exercise the affected normal and failure paths. Passing unrelated tests is insufficient. If that evidence is unavailable, propose the edit without applying it. Correctness fixes remain proposal-only here, including authorized fixes; implement them in a separate behavior-changing task, not under this cleanup gate.
- Identify required checks before editing from project instructions and the affected contract. Report unavailable or failing required checks as limitations; do not silently substitute inspection for them. Report unrelated baseline failures separately and avoid claiming the whole suite passed.
- For the combined result, rerun the checks affected by interactions among retained edits. If required checks fail or cannot run, or equivalence is uncertain, apply the rollback and recovery-check rules in `SKILL.md`; individually passing edits do not establish a passing combined state. Keep unchanged IDs and resolve a finding only when its observable criterion and applicable verification are satisfied. Describe checks, class, and observed results in `Quality verification:`.

## Contextual simplification recipes

Use the edit and verification gate in `SKILL.md` for every recipe. Treat each recipe as a candidate, not an automatic rewrite:

- Flatten a branch or remove a redundant boolean conversion only after checking evaluation order, truth semantics, cleanup, and effects. Check asynchronous scheduling/error delivery, inferred public declarations, and copy/alias/iterator semantics when the transformation affects them.
- Extract a predicate, named operation, or parameter record when it clarifies responsibility without hiding a simple path.
- Consolidate metadata, constants, or shape definitions when they share meaning and ownership; verify all affected consumers and variant coverage.
- Remove a forwarding wrapper, unused option, or repeated guard only after establishing its contract, callers, and invariant enforcement.
- Isolate effects or initialization when it improves lifecycle control and behavioral evidence; preserve initialization ordering and ownership.
- For state-model, error-model, or algorithm changes, check whether behavior remains equivalent. If equivalence is uncertain, retain the change as a separately identified proposal.
