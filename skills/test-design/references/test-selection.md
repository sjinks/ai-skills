When to read: when choosing between plausible test cases, exact assertions, fakes, asynchronous checks, or execution-line syntax.

# Test Selection Guidance

- Inspect repository instructions, interfaces, implementation, and nearby tests to establish test conventions and evidence. Establish expected behavior from the contract; implementation alone cannot define expectations.

- Favor cases for costly, subtle, security-sensitive, destructive, or historically fragile failures. Add absent, empty, invalid, duplicate, threshold-adjacent, retry, partial-failure, cancellation, or concurrency cases when their contract path is reachable and materially distinct.
- For stateful behavior, identify initial state, operation, resulting state, repeated and invalid transitions, and preservation or rollback after failure. Test invariants such as no mutation on rejection or at-most-once effects when promised.
- Assert the strongest stable result. Existence, non-throwing execution, and mock calls are weak oracles unless they are the promised behavior. Exact bytes or call order are appropriate when those are contractually required.
- For asynchronous behavior, synchronize on completion or a bounded condition. Fixed sleeps and test-order dependence are poor evidence. Control clock, randomness, locale, environment, and shared state when they affect assertions.
- Use a narrow fake at a nondeterministic or external boundary. Do not reproduce production logic in a mock or derive expected values with the same algorithm as the code under test.
- Parameterize inputs that express the same behavior; keep distinct behaviors separate so failures are easy to locate. Use snapshots only when the full representation is an intentionally reviewed contract.
- Follow the repository's runner, assertion library, fixtures, naming, and cleanup conventions. Do not add a test dependency when existing tools can express the behavior. Do not alter production behavior solely to make testing convenient.
- A test should fail for an important plausible mutation, such as skipping validation, reversing a boundary, dropping a value, or updating state before a rejected operation. Remove cases that only repeat the same failure signal.
- If a case needs a live service, production data, or an unavailable environment, use a safe local substitute only if it preserves the behavior and observation being tested. If no faithful substitute exists, record the environment limitation and leave the case unrun. For a read-only plan or assessment, record the limit in the second report field and use `Not run; no tests changed.` For changed tests that cannot run, use `Unverified: <reason>`. Never claim the case passed without execution.

## Illustrative Case

For a transfer that rejects insufficient funds without changing either balance, start below the requested amount, assert the specific rejection and both unchanged balances, and catch a debit-before-validation defect. Repeating several arbitrary insufficient amounts adds little evidence unless a boundary changes behavior.

## Execution-Line Examples

These snippets show only the final execution field. The cases and evidence fields must precede it; all three fields remain required. Replace the execution label when the caller requires a different label.

For changed tests that ran, use a complete line such as:

```text
Test execution: Ran: node --test test/clamp.test.js => passed
```

For changed tests that could not run:

```text
Test execution: Unverified: physical sensor unavailable
```

For plans, assessments, or blocked input before any edits:

```text
Test execution: Not run; no tests changed.
```

With caller labels `Case set:`, `Design basis:`, and `Run record:`, the last example becomes `Run record: Not run; no tests changed.` after the caller's cases and evidence fields. Never insert the explanatory text `Final line:` between the execution label and its status.
