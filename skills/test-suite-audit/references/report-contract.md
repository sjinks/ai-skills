When to read: before recording findings/evidence rows and before producing any final audit report.

# Report Contract

The core owns severity, status precedence, and checklist gates. This reference defines exact report fields and evidence classification. Do not replace labels. Replace all angle-bracket placeholders and enum alternatives with actual values.

## Shape and cardinality

Emit one report for the declared audit scope. Use the five headings shown in the template once, in that order. Finish with one Audit status line; do not append prose after it.

Audit scope identifies revision/workspace state, requested/inspected/excluded/unreviewed files, diagnostic dimensions, profiles, requested/resolved runtime versions, actual commands, and unavailable evidence. Include or link a per-file inventory. Exclusions must not silently discard requested work; unresolved requested scope remains unreviewed.

Under Findings, repeat the complete finding record once per supported material finding, unless the caller explicitly limits the output. Disclose that limit in Audit scope; it does not reduce declared inspection scope. Order findings by severity, then first evidence location. Use no invented file paths or IDs. Reference the corresponding Evidence table row by its Contract and Plausible fault values. Escape Markdown pipes inside cells.

For exhaustive requests, identify unfinished file groups, diagnostic dimensions, implicated sibling checks, or unresolved candidates in Audit scope and apply the core's status rules. A prioritized first batch is not Complete while declared work remains.

Create at least one evidence row per important contract; repeat the contract for distinct faults or profiles. If meaningful inspection identifies no important contract, use `None — <reason>` instead of a table and explain the scope limit. Findings and evidence rows need not have matching counts.

Use these fields in order for each finding:

```text
Title: <concrete finding title>
Severity: Critical | High | Medium | Low
Category: Weak Test | Low-Value Test | Redundant Test | Missing Test | Isolation | Determinism | Misleading Coverage | Other
Finding kind: Test gap | Current defect
Behavior: <contract, invariant, or property>
Evidence: <exact files/symbols, what tests establish, associated evidence row>
Gap: <missing or duplicated behavioral evidence>
Surviving fault: <plausible incorrect implementation, or Not applicable — reason>
Impact: <consequence and evidence limits>
Recommendation: <smallest useful correction>
```

Test gap includes adequacy, redundancy, isolation, and reliability findings. Current defect requires source evidence or a direct probe that unmodified implementation violates an independently established contract. A mutation alone cannot establish it. Record unresolved contracts as uncertainty, not findings of a defect. An incidental Current defect does not authorize implementation fixes or establish deployment exposure.

For source-only findings, label the prediction as inference. For execution, identify baseline/control/probe/mutant commands, profiles, and outcomes. For redundancy, identify subsuming tests and the evidence removal would lose.

## Technical literal formatting

In Markdown report prose and table cells, use inline code for file/directory paths (including line anchors), function/method/class/module names, variables, environment variables, configuration keys, flags, commands, and code literals. Preserve their exact spelling. Choose a backtick delimiter longer than any backtick run in the literal.

For example: `__tests__/lib/upload.js:42` calls `uploadParts()` with `fileMeta` and `DO_NOT_TRACK=1`.

For linked paths, escape Markdown metacharacters in plain-text link labels and leave link destinations unchanged. Inside fenced code blocks, preserve the code without adding inline-code delimiters. Keep the required report headings, field labels, and enum values unchanged.

## Evidence status

Choose exactly one per row, applying these branches:

- **Not applicable:** no fault experiment applies. Use for direct unmodified-code defect probes or inspection without a fault prediction; state the reason and actual evidence in Real observation.
- **Blocked:** a planned mutation cannot be attempted because a prerequisite is unavailable. Record any source-backed prediction separately in Real observation; do not replace the blocked execution result with Inferred.
- **Inferred:** source-backed fault prediction when no mutation execution was attempted or blocked.
- For an attempted mutation, use the first matching rule:
  1. **Blocked:** required setup, baseline, or control is unavailable/invalid; zero selected or only-skipped tests provide no usable run; syntax/load failure or an unrelated crash invalidates the experiment; or restoration/resource cleanup is unverified.
  2. **Not exercised:** a valid applied fault is skipped, unloaded, or unreached.
  3. **Observed survivor:** verified runtime-visible fault and relevant path activation, matching passing baseline, working control, and tests that pass.
  4. **Killed:** the same validity requirements, but a new behavior-relevant assertion fails.
  5. **Blocked:** outcome is inconclusive or cannot establish either survival or detection.

Preserve raw outcomes when a control is invalid or cleanup is unverified; do not label a green mutant as Observed survivor. Distinguish this row-level status from overall Audit status.

A component survivor is qualified by that test selection. A suite-wide claim requires the broader suite and matching baseline under the same profile. Count experiment runs separately from distinct edits; selected suspected gaps are not a random mutation score.

## Report template

```markdown
## Audit scope
<revision/workspace, scope inventory and diagnostic coverage, profiles, commands, limits>

## Findings
<complete finding records, or No material findings in the inspected scope>

## Evidence table
| Contract | Test/input actually exercised | Real observation | Plausible fault | Evidence status | Remaining limitation |
|---|---|---|---|---|---|
| <contract> | <fixture/input; explicitly not run when source-only> | <observation and source or run evidence> | <fault or Not applicable — reason> | <one permitted value> | <boundary/profile/inspection limit or None> |

## Final assessment
Code coverage: <instrumentation evidence, or unavailable>
Behavioral coverage: <meaningfully protected contracts>
Fault-detection evidence: <faults known or inferred to be rejected>
Key adequacy gaps: <important faults likely to survive, or None with scope reason>
Test-suite signal-to-noise: <distinct versus weak/redundant evidence>
Isolation and reliability: <restoration, independence, determinism, and limits>

## Audit status
<completed scope and remaining work; limitations do not imply a passing suite>
Audit status: <Blocked, Partial, or Complete under core precedence>
```

No findings after meaningful inspection uses the exact sentence in the template and retains every other section. An empty evidence table uses the explicit reason described in Shape and cardinality. Every Final assessment field appears once even when its value is unavailable or Not assessed.

## Insufficient-context template

If artifacts cannot support meaningful inspection, use this complete report. Name the exact missing input without rating unavailable tests.

```markdown
## Audit scope
<requested scope, exact missing/unreadable input, and what is needed>

## Findings
Not assessed

## Evidence table
Not assessed

## Final assessment
Code coverage: Not assessed
Behavioral coverage: Not assessed
Fault-detection evidence: Not assessed
Key adequacy gaps: Not assessed
Test-suite signal-to-noise: Not assessed
Isolation and reliability: Not assessed

## Audit status
<exact input needed to permit meaningful inspection>
Audit status: Blocked
```

If meaningful inspection succeeded but requested execution or required references are unavailable, retain useful findings/evidence in the normal template and use Partial. If this report reference itself is unreadable, use the core's heading/field fallback with available evidence and its status precedence.

## Discriminating examples

- Completed static inspection, source-backed gap, no requested execution: Inferred row; Audit status Complete; explicitly runtime-unverified.
- Passing mutant without a working control: Blocked row. Requested mutation execution remains invalid, so overall Partial after meaningful inspection.
- Valid mutation not reaching its target: Not exercised row; it cannot satisfy requested proof of fault sensitivity. Report remaining requested work as Partial.
- Mutation survives component tests only: Observed survivor for that component/profile; broader suite protection remains unverified.
- Direct unmodified-code probe violates a documented contract: Current defect finding, Not applicable row; do not call it a mutation survivor.
- Optional mutation unavailable after complete requested static inspection, with cleanup verified: Blocked row and explicit limitation; Complete remains possible.
- Cleanup unverified after any experiment: stop further experiments, disclose residual state, and use Partial after meaningful inspection.
