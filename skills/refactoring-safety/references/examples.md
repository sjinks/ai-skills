When to read: when constructing a step table or checking common refactoring mistakes. These examples illustrate the core rules; they add no requirements.

# Refactoring Examples

## Example

Target: extract the pricing rules out of `OrderService` into a `PricingPolicy` collaborator; behavior must not change.

Mode: `plan`. Assume the characterization checks have not yet been created or run, so dependent restructuring is blocked.

Preserved behavior row:

| Behavior | Safety net |
|----------|------------|
| order total for mixed-discount carts | characterization step 1 |

Step rows:

| # | Transformation | Check after | Revertible | Notes |
|---|----------------|-------------|------------|-------|
| 1 | characterize: pin totals for the five known cart shapes | new tests green against current code | yes | hand-edit; must not touch: production code |
| 2 | extract: `PricingPolicy` with methods delegating to existing private logic | blocked | yes | hand-edit; must not touch: discount data schema; required after unblocking: full order-service suite green |
| 3 | move: call sites to `PricingPolicy` | blocked | yes | mechanical; must not touch: public `OrderService` API; required after unblocking: full suite + characterization green |
| 4 | delete-dead-code: private pricing methods made redundant by steps 2–3 | blocked | yes | hand-edit; must not touch: public `OrderService` API; required after unblocking: full suite + characterization green; verify no remaining consumers before deletion |

### Blocked

- Step 2: requires step 1 characterization to pass before extraction; implementing agent verifies the results.
- Step 3: requires step 1 characterization to pass before moving callers; implementing agent verifies the results.
- Step 4: requires step 1 characterization to pass and consumer inspection to establish safe deletion; implementing agent verifies the evidence.

These rows and blocker entries are a partial `plan` example. A complete report also includes the heading, Target, Mode, Consumers considered, Consumer inspection, and all required sections. Empty sections contain `None`, except `### Final diff review`, which uses `Outcome: not run` and `Evidence: plan only`. For `execute`, add actual check results with checked-state identifiers and final diff review evidence. Record each pre-step state so rollback preserves unrelated edits.

## Anti-Patterns

- Restructuring first, "adding tests after" — the net goes up before the acrobatics.
- Fixing bugs found mid-refactor instead of recording them as questions.
- A red suite carried across steps to be "stabilized at the end".
- Changing observable-behavior expectations merely to make a step pass.
- One giant revert-resistant step doing extract, rename, and behavior tweak at once.
- Claiming coverage from test files that exist but do not exercise the preserved behavior.
- Treating a passing result from earlier code as validation after its checked inputs change.
- Restoring a whole file during rollback and discarding pre-existing or concurrent edits.
- Treating no consumers found in a searched scope as proof that no consumers exist elsewhere.
- Claiming completion from passing checks without comparing the complete refactor diff against the preserved contract.
