---
name: cpp-correctness-review
description: "Use when: reviewing, debugging, or designing bounded C or C++ operation correctness, including wrong conditions, invalid state transitions, off-by-one errors, signed/unsigned mistakes, truncation, size calculations, iterator misuse in single-threaded flows, partial operation handling, stale cached state, overload mistakes, boundary cases, or tests that contradict implementation. Do not use for lifetime, concurrency, security, performance, sanitizer triage, or broad architecture review."
argument-hint: "Describe the C/C++ operation, state transition, boundary case, failing input, or diff whose functional correctness is in question."
user-invocable: true
---

# C++ Correctness Review

Use this skill when a bounded C or C++ operation, state transition, parser step, container update, numeric calculation, or API behavior may return the wrong result or leave the wrong state for a concrete input or edge case.

The goal is to compare the visible contract with the reachable behavior: name the expected state or result, trace the control flow that actually occurs, and report only defects with a concrete failing scenario or a clearly violated contract.

**UTILITY SKILL.** INVOKES: read-only file access for supplied targets; no other tools or skills. FOR SINGLE OPERATIONS: use for focused functional-correctness review, edge-case review, failing-input analysis, or test/implementation consistency checks.

## Scope

- Use this skill for wrong branch conditions, invalid state transitions, off-by-one and boundary handling, signed/unsigned conversion, integer truncation, overflow in non-security size calculations, incorrect size or index calculations, invalid iterator use in single-threaded control flow, container invalidation that does not depend on object lifetime escaping, partial read/write or partial update handling where the issue is the wrong final result, stale cached state, wrong overload or template selection, incorrect standard-library assumptions, missing empty-input behavior, and tests that contradict the implementation contract.
- Apply it to one function, class operation, parser transition, algorithm step, state-machine transition, or small diff where the expected behavior can be stated.
- Keep the review centered on functional behavior. Route dangling owners/borrowers, data races, attacker-controlled exploit paths, performance-only costs, and sanitizer report interpretation to a more specific review instead of stretching this skill.

## DO NOT USE FOR:

- Object lifetime, ownership, dangling references, callback lifetime, or use-after-move review where the core failure is invalid storage.
- Multithreaded synchronization, data races, deadlocks, atomics, condition variables, or shutdown ordering.
- Security review where the claim depends on attacker control, trust boundaries, command/path/deserialization risk, cryptography, authorization, or resource-exhaustion impact.
- Performance tuning, ABI/API compatibility classification, CMake/build review, or sanitizer-report triage.
- Broad architecture review or speculative redesign when no bounded operation or state transition is in scope.

## Required Context

Collect or infer before judging:

- Target: files, diff, function, class operation, test, trace, or design step under review.
- Expected contract: documented behavior, test expectation, caller expectation, invariant, or explicit user-stated intended result.
- Concrete inputs or states in scope, including empty, minimum, maximum, one-past-boundary, duplicate, malformed, and partial-operation cases when relevant.
- State affected by the operation before and after it runs, including caches, counters, iterators, indices, status flags, and ownership-neutral container contents.
- Existing tests that define or contradict expected behavior.

If the target or expected contract cannot be established, return `Verdict: BLOCK` with one open question. Do not invent the expected behavior. Insufficient-context mode takes precedence over pattern-level decision rules: general rules may be cited as context, but no verdict other than `BLOCK` may rest on an unseen target or unstated contract.

## Output Depth

Default to `standard`. `quick` still reports missing required context, blockers, unmitigated HIGH/CRITICAL findings, and target-specific concerns; it only omits non-applicable checklist expansion. `standard` covers the applicable checklist with concise evidence. `exhaustive` enumerates the full checklist only when asked or when the change surface warrants it. Name the selected depth when the user asks for `quick` or `exhaustive`.

## Workflow

1. Establish the operation and the expected contract: result, state transition, invariant, or test expectation.
2. Trace the normal path for a representative valid input.
3. Trace the relevant edge paths: empty, boundary, duplicate, malformed, partial, overflow/truncation, and state-transition cases that the target can receive.
4. Compare each reachable result or state mutation with the contract and adjacent tests.
5. Check whether any related cached state, counters, indexes, iterators, or status flags are updated consistently on success, failure, and early-return paths.
6. Classify only defects with a concrete failing input/state or a visible contract violation, map severity to a verdict, and state the regression test each fix needs.

## Decision Rules

The Checklist below is the gating source of truth when these rules overlap; the rules explain rationale.

- When an operation has a documented precondition, distinguish precondition violations from implementation bugs. A caller that violates a visible precondition is not a correctness finding in the callee unless the callee promises to validate it.
- When a condition uses `<=`, `<`, `>=`, `>`, or an index offset, test the exact boundary values: empty, size 1, last valid index, one past the end, minimum, and maximum. A branch that accepts one-past-end or rejects the last valid element is a finding.
- When signed and unsigned values mix, prove the conversion cannot wrap, widen unexpectedly, or turn a negative value into a huge positive value before comparison, indexing, or allocation. If that conversion affects memory under attacker control, route the security impact separately.
- When a value is narrowed, truncated, multiplied, or added to compute a count, offset, length, or capacity, verify the operation's domain and the type that stores the result. Silent truncation that changes the functional result is a finding.
- When a function can process fewer bytes, elements, records, or operations than requested, check the partial result path. Treat assuming all-or-nothing behavior as a finding when the called API documents partial completion.
- When an operation mutates multiple pieces of state, all derived state must stay consistent: caches, indexes, counts, flags, reverse maps, and sorted/order metadata. Updating one projection but not its sibling is a finding.
- When a container is mutated during iteration in single-threaded code, the loop must use an invalidation-safe idiom for that container. Report the wrong skipped element, duplicated visit, invalid iterator increment, or stale index as the correctness effect; route storage-dangling cases to lifetime review when the invalid reference escapes.
- When overload resolution, implicit conversion, template argument deduction, or ADL selects a different operation than intended, cite the selected operation and the visible behavior change. Do not report theoretical overload ambiguity that the compiler would reject.
- When tests and implementation disagree, first identify the contract source. If neither side defines the intended behavior, report an open question rather than declaring one side wrong.

## Checklist

### Contract And Inputs

- The target operation and expected contract are explicit or inferable from authoritative tests/docs/callers.
- Empty, single-item, duplicate, malformed, minimum, maximum, and one-past-boundary inputs are handled according to the contract where applicable.
- Preconditions are either enforced or documented; findings do not rely on callers violating visible preconditions unless validation is promised.

### Control Flow And State Transitions

- Every branch condition matches the intended state transition, including early returns and error branches.
- State-machine transitions reject invalid prior states and update status flags consistently.
- Success, no-op, partial, and failure paths leave the object in the promised state.

### Numeric And Size Calculations

- Signed/unsigned comparisons, narrowing conversions, and integer arithmetic do not change the functional result.
- Counts, offsets, lengths, and capacities are computed in a type large enough for the stated domain.
- Boundary comparisons accept all valid values and reject invalid ones exactly once.

### Containers, Iterators, And Algorithms

- Iteration remains valid across erase/insert/reallocation for the container used.
- Indexes, iterators, and references are refreshed after mutations that invalidate them within the same operation.
- Standard-library algorithm and container semantics are applied correctly, including sortedness, comparator, iterator-category, and erase-return rules.

### Consistency And Derived State

- Caches, reverse indexes, counters, flags, and summaries update atomically with the source state from the caller's perspective.
- Copy/move/assignment operations preserve invariants and leave source/destination states that match the type's contract.
- Tests, examples, and implementation agree on visible behavior or record the unresolved contract question.

### Tests

- Each fixed correctness bug has a regression test for the failing input or state transition.
- Boundary and partial-operation cases are tested at the layer where the contract is observable.

## Severity And Verdicts

- `CRITICAL`: a reachable correctness defect corrupts persistent state, returns a dangerously wrong result to a caller that will act on it, or violates a core invariant in normal operation.
- `HIGH`: a reachable defect produces wrong output or wrong state for a specific boundary, partial, or state-transition case likely to occur in production.
- `MEDIUM`: a contract ambiguity, missing edge handling, derived-state inconsistency, or test gap is likely to become wrong behavior under plausible callers or future edits.
- `LOW`: clarity or hardening issue with no current incorrect execution.

Verdicts:

- `BLOCK`: missing required context, any `CRITICAL`, or any unmitigated `HIGH`.
- `CONCERNS`: any unmitigated `MEDIUM`, or remaining `HIGH`/`MEDIUM` findings that each have a compensating control, accepted tradeoff, or bounded reachability.
- `CLEAN`: every applicable checklist item holds; `LOW`-only findings do not block `CLEAN` and are listed as findings. If no behavior was changed, Tests is n/a and does not block `CLEAN`. For design-stage targets with no tests yet, the best achievable verdict is `CONCERNS` with test expectations recorded per finding.

## Output Format

```text
Verdict: BLOCK | CONCERNS | CLEAN
Target: <files, diff, operation, test, or design step>
Contract: <expected behavior>
Inputs/states reviewed: <concrete cases>

Findings:
1. <short title>
  Severity: CRITICAL | HIGH | MEDIUM | LOW
  Classification: Confirmed issue | Likely risk | Open question | Accepted tradeoff | Test gap
  Evidence: <file:line, diff hunk, test, trace, or design sentence>
  Rule: <contract-inputs | control-flow-state | numeric-size | containers-algorithms | derived-state | tests>
  Expected: <required result or state>
  Actual: <reachable wrong result or state>
  Required guard: <implementation, contract, or test change>
  Test expectation: <regression test or N/A>

Checklist status:
- Contract and inputs: covered | missing | n/a
- Control flow and state transitions: covered | missing | n/a
- Numeric and size calculations: covered | missing | n/a
- Containers, iterators, and algorithms: covered | missing | n/a
- Consistency and derived state: covered | missing | n/a
- Tests: covered | missing | n/a

Residual risk: <remaining caveats or None>
```

`Rule:` values map to checklist sections as follows: `contract-inputs` -> Contract And Inputs; `control-flow-state` -> Control Flow And State Transitions; `numeric-size` -> Numeric And Size Calculations; `containers-algorithms` -> Containers, Iterators, And Algorithms; `derived-state` -> Consistency And Derived State; `tests` -> Tests.

When no material issues exist, write exactly `Findings: None` (allowed only with `CLEAN`) and list assumptions under Residual risk. For design-stage targets that earn `CONCERNS` solely because tests cannot exist yet, emit one `Test gap` finding with `Rule: tests` listing the required test expectations instead of an empty findings list.

Insufficient-context mode: when the target or expected contract cannot be established, emit exactly this reduced template and stop; do not emit contract, inputs/states, checklist status, or residual risk with guessed values:

```text
Verdict: BLOCK
Target: <files, diff, operation, test, or design step>

Findings:
1. <missing-context short title>
  Severity: LOW
  Classification: Open question
  Evidence: <which required context is missing>
  Rule: <contract-inputs | control-flow-state | numeric-size | containers-algorithms | derived-state | tests>
  Expected: <unknown because missing context>
  Actual: <unknown because missing context>
  Required guard: <what context must be supplied>
  Test expectation: N/A
```

## Examples

- Off-by-one: `if (index <= values.size()) return values[index];` accepts `index == values.size()`, which is one past the last valid element. Fix: use `index < values.size()` and add tests for `size() - 1` and `size()`.
- Signed/unsigned conversion: a lookup whose contract rejects negative positions first converts `int pos` to `std::size_t index`, then clamps `index >= vec.size()` to `vec.size() - 1`. For `pos == -1` and a non-empty vector, conversion produces a large unsigned value and the function returns the last element instead of rejecting the input. Fix: reject negative values before converting and test `-1`, `0`, and the last valid position.
- Stale derived state: `remove(id)` erases from `items_` but leaves `by_name_[old_name] = id`, so a later name lookup returns a removed item. Fix: update both projections on every success path and test remove-then-lookup.

## Definition Of Done

A correctness change is ready only when:

- The operation's expected behavior is explicit.
- The normal path and relevant edge paths match that behavior.
- Numeric, container, and state-transition assumptions are checked against the actual types and APIs used.
- Derived state remains consistent across success, no-op, partial, and failure paths.
- Regression tests cover each fixed failing input or state transition; if no bug classes were fixed, Tests is n/a.