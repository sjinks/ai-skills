When to read: when illustrating comparisons, conditional lessons, or decision-resolving next checks.

# Worked Examples

These fictional inputs and complete reports illustrate the normative report rules. Evidence names are supplied example artifacts, not claims about this repository. Fences delimit examples; actual reports have no fence. Each example supplies a goal and success condition. Proposed prevention is not claimed to have been validated.

## Failure followed by success

Input: The same fixture must pass. A1 fails because a required field is absent; A2 adds only that field and passes. Fixture logs and the one-field diff isolate the cause. Existing scripts show that a fixture check can run automatically in the current runner with no new dependency or operator action; the supplied local procedure establishes that guidance requires no new dependency and adds one recurring manual invocation. No other mechanism addresses this pattern under the supplied evidence.

```text
Retrospective: Make the supplied fixture pass; compare A1 and A2.
Retrospective Assessment: A1 failed and A2 worked. Only the required field changed; fixture logs and the diff isolate that difference. Repeat checking required fields against the fixture. Baseline: current runner; scenario: next fixture change. Deterministic check has 0 new dependencies and 0 new steps; repository guidance has 0 and 1, supported by supplied scripts and procedure. The check detects the missing field before the full run; guidance prompts a manual check. Other mechanisms lack an evidenced connection. Select the automated check.
Retrospective Attempts:
- A1 | Status: failed | Action: Run the fixture without the required field | Result: Rejected | Evidence: fixture-log-1
- A2 | Status: worked | Action: Add the required field and rerun the same fixture | Result: Passed | Evidence: fixture-log-2 and one-field-diff
Retrospective Learnings:
- L1 | Attempts: A1, A2 | Cause: confirmed | Lesson: When changing this input, check required fields against the fixture before the full run | Evidence: fixture logs and one-field-diff isolate the missing field
Retrospective Prevention:
- P1 | Learnings: L1 | Mechanism: deterministic check | Decision: Add the required-field fixture check to the existing runner to detect omission before the full run; effectiveness remains proposed
Retrospective Next Checks:
None.
Retrospective Skill Candidate: no new skill
Retrospective Verdict: CLEAN
```

No validation gap remains that could change the recommendation under these supplied facts; implementation and execution of the proposed check are outside the retrospective.

## Abandoned approach with unknown cause

Input: The approach must complete within 60 seconds. A1 exceeds that limit and is abandoned. A summary establishes failure but does not identify where time was spent. No trace is supplied, and no prevention mechanism has an evidence-supported connection to a specific failure step.

```text
Retrospective: Review the abandoned approach against the 60-second completion condition.
Retrospective Assessment: A1 failed before abandonment. There is no related attempt to compare and no evidenced success to preserve. The summary establishes a missed deadline, not its cause; prevention is unsupported.
Retrospective Attempts:
- A1 | Status: failed | Action: Run the abandoned approach | Result: Exceeded 60 seconds | Evidence: supplied-run-summary
Retrospective Learnings:
- L1 | Attempts: A1 | Cause: unknown | Lesson: The approach missed the deadline; time spent waiting versus computing remains unknown, so no causal decision rule is supported | Evidence: supplied-run-summary lacks a timing breakdown
Retrospective Prevention:
None.
Retrospective Next Checks:
- N1: Resolve L1 by requesting the timing trace for A1; dominant waiting supports investigating the wait step, while dominant computation supports investigating the computation step; an unavailable or inconclusive trace leaves the cause and prevention unresolved and requires a timing breakdown.
Retrospective Skill Candidate: no new skill
Retrospective Verdict: CONCERNS
```

Abandonment does not erase an established failure. Unknown cause does not require inventing a conditional lesson or blocking all analysis.

## Selected prevention plus an unresolved comparison

Input: The same authenticated fixture must pass. A1 lacks a required field; A2 changes only that field and reaches authentication but fails with an expired credential; A3 refreshes only the credential and passes. Logs, diffs, and credential metadata isolate both failures. For missing-field recurrence, the current runner supports an automatic check with 0 new dependencies/steps; guidance needs 0/1. For credential-expiry recurrence, local guidance needs 0/1, but the directly required dependencies of a refresh helper are unknown. Both expiry candidates address refresh before authentication; other mechanisms have no supported connection in these inputs.

```text
Retrospective: Make the authenticated fixture pass; compare A1 through A3.
Retrospective Assessment: A1 failed; A2 fixed the field but still failed authentication; A3 worked after credential refresh. Each transition changes one factor, isolated by logs and diffs. Preserve checking credential expiry before authenticated runs. Baseline: current runner and local procedure; scenarios: next missing-field recurrence and next credential-expiry recurrence. For L1, deterministic check costs 0 dependencies/0 steps and guidance costs 0/1 per supplied scripts; the check detects omission before execution and guidance prompts manual inspection. For L2, guidance costs 0/1 per procedure and prompts refresh before authentication; a helper would refresh before authentication but its dependency count is unknown. Other mechanisms have no evidenced connection. Select L1 prevention; leave L2 unselected.
Retrospective Attempts:
- A1 | Status: failed | Action: Run without the required field | Result: Rejected before authentication | Evidence: log-1
- A2 | Status: partly-worked | Action: Add only the required field and rerun | Result: Field accepted; expired credential rejected | Evidence: log-2 and field-diff
- A3 | Status: worked | Action: Refresh only the credential and rerun | Result: Passed | Evidence: log-3, refresh-diff, and credential-metadata
Retrospective Learnings:
- L1 | Attempts: A1, A2 | Cause: confirmed | Lesson: When changing fixture inputs, check required fields before execution | Evidence: log-1, log-2, and field-diff
- L2 | Attempts: A2, A3 | Cause: confirmed | Lesson: When a credential has expired, refresh it before the next authenticated run | Evidence: log-2, log-3, refresh-diff, and credential-metadata
Retrospective Prevention:
- P1 | Learnings: L1 | Mechanism: deterministic check | Decision: Add the automatic required-field check to detect omission before execution; effectiveness remains proposed
Retrospective Next Checks:
- N1: Resolve L2's prevention comparison by obtaining the refresh helper's dependency manifest and recurring procedure; if it adds dependencies, choose 0-dependency guidance; if it adds none, compare its recurring steps with guidance's 1 and use mechanism order only on a full tie; unavailable counts keep L2 unselected and require the missing manifest or procedure.
Retrospective Skill Candidate: no new skill
Retrospective Verdict: CONCERNS
```

Uncertainty for L2 does not discard the supported L1 selection. Success learning L2 does not independently authorize creating a skill or implementing a helper.
