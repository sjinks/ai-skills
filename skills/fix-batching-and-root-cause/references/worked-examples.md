When to read: when choosing verification that distinguishes removal of a producing cause from containment of its effects.

# Root-cause removal versus symptom containment

These hypothetical examples illustrate the core rules. File names, findings, constraints and observations are scenario inputs, not claims about this repository. The reports are complete planning examples: checks are proposed, no changes have been applied, and no test results are claimed.

## Shared scenario

Two supplied findings identify negative quantities accepted by a web endpoint and a batch importer. In the supplied source, both entry points call `validateQuantity`, which checks only that the value is an integer. The domain requires nonnegative quantities; zero and positive integers remain valid. The missing lower-bound check in the shared validator produces both findings.

The important distinction is where the producing condition changes. Endpoint tests can establish containment at those endpoints; they cannot alone establish that the shared validator was repaired.

## Example 1: remove the producing cause

Scenario evidence identifies the web endpoint and importer as the validator's only consumers. The caller allows a change to the shared validator. Proposed verification covers the shared decision and both entry points, including valid boundary values.

```markdown
## Fix Batch Plan

### Findings

- F1: WEB-QTY at web/quantity-handler — negative integer quantity is accepted.
- F2: IMPORT-QTY at batch/quantity-importer — negative integer quantity is accepted.

### Clusters

| Cluster | Findings | Shared cause | Fix depth | Planned change | Verification |
|---------|----------|--------------|-----------|----------------|--------------|
| C1 | F1, F2 | Supplied source: shared validateQuantity checks integer shape but omits the required nonnegative bound; both entry points call it | root-cause | Reject negative integers in validateQuantity; preserve acceptance of zero and positive integers | Proposed validator tests: negative integers are rejected, zero/positive integers are accepted, existing noninteger rejection remains. Proposed web/importer tests: both reject negative input and retain valid-input behavior. Source comparison: both still delegate to the repaired shared validator. |

### Symptom-level and no-fix justifications

None.

### Fix order

1. C1 — depends on: none.

### Planning gaps

None.

Verdict: BATCH-READY
```

The direct validator checks distinguish cause removal from endpoint-only filtering. Entry-point checks show that both supplied findings are addressed through the shared fix. Valid and invalid boundary checks constrain unintended behavior changes. `BATCH-READY` describes the complete plan, not successful execution of these checks.

## Example 2: contain the symptoms under a scope constraint

The caller authorizes only a boundary hotfix. Changing the shared validator is excluded until its wider consumer compatibility has been assessed. The supplied source still establishes the missing shared check, but this plan addresses only the two supplied entry points. It does not claim that other consumers are protected.

```markdown
## Fix Batch Plan

### Findings

- F1: WEB-QTY at web/quantity-handler — negative integer quantity is accepted.
- F2: IMPORT-QTY at batch/quantity-importer — negative integer quantity is accepted.

### Clusters

| Cluster | Findings | Shared cause | Fix depth | Planned change | Verification |
|---------|----------|--------------|-----------|----------------|--------------|
| C1 | F1, F2 | Supplied source: shared validateQuantity checks integer shape but omits the required nonnegative bound; both entry points call it | symptom-level | Reject negative integers at the web and importer boundaries before calling the unchanged validator | Proposed web/importer tests: both reject negative input and retain zero/positive acceptance and existing noninteger rejection. Source comparison: guards exist at both boundaries, while validateQuantity remains unchanged and still lacks the lower-bound check; passing endpoint tests alone does not demonstrate cause removal. |

### Symptom-level and no-fix justifications

- C1: symptom-level — caller limits this hotfix to the two entry points pending shared-validator compatibility assessment — follow-up: proposed task QUANTITY-VALIDATION to inventory consumers, repair the shared lower-bound check, and verify consumer compatibility.

### Fix order

1. C1 — depends on: none.

### Planning gaps

None.

Verdict: BATCH-READY
```

Both endpoint effects are contained, but the producing defect remains in the shared validator. The reason and named proposed follow-up make the depth honest; they do not imply that an issue was created or that its work is complete. The deferred compatibility assessment belongs to the documented follow-up, not an unresolved prerequisite for this caller-constrained containment plan. If that assessment were required to establish the containment change's safety, it would instead be a planning gap and the verdict would be `BATCH-PARTIAL`.
