Read this reference when producing or validating an Instruction Quality Audit report.

# Instruction Quality Report Contract

Produce one report per distinct target package or standalone artifact.

Within each report, use these top-level markers exactly once and in this order.

Uppercase tokens such as `TARGET_NAME_OR_PATH`, `FILE_OR_ITEM`, and `NONE_OR_DESCRIPTION`, plus angle-bracket tokens such as `<value>`, are placeholders. Replace them with actual values; do not emit the placeholder names literally.

````markdown
# Instruction Quality Audit

Audit: TARGET_NAME_OR_PATH

## Audit Scope

- Mode: core | package | path
- Status: completed | partial | blocked
- Effective instruction files:
  - FILE_OR_ITEM
- Mutually exclusive paths:
  - PATH_OR_NONE
- Trusted custom diagnostics:
  - RULE_OR_NONE
- Limitations: NONE_OR_DESCRIPTION

## Findings

### IQA-001 — TITLE

Severity: error | warning | information
Confidence: high | medium
Type: contradiction | precedence | ambiguity | terminology | authority | side-effect | closure | failure-handling | cognitive-load | duplication | output-contract | custom
Locations:
- FILE_AND_SECTION_OR_LINE
Evidence:
```text
EXACT_RELEVANT_INSTRUCTION
```
Related evidence:
```text
SECOND_EXCERPT_WHEN_NEEDED
```
Behavioral risk: CONCRETE_MODEL_OR_EVAL_FAILURE
Correction: EXACT_REWRITE_OR_SPECIFIC_STRUCTURAL_CHANGE

## Unresolved Questions

None.

## Summary

Errors: N
Warnings: N
Informational findings: N
Highest-priority corrections:
1. CORRECTION

Verdict: No material defects | Needs revision | Blocked
````

## Optional Finding Fields

Omit `Related evidence:` when one excerpt is sufficient.

For cross-file findings, include the co-loaded path in `Locations` or `Behavioral risk`.

## Verdict Selection

Use:

- `Verdict: No material defects` only when `Status: completed` and `## Findings` is `None.`;
- `Verdict: Needs revision` when one or more findings are reported, whether `Status` is `completed` or `partial`;
- `Verdict: Blocked` when `Status: blocked`;
- `Verdict: Blocked` when `Status: partial`, no findings were established, and the unavailable instruction surface prevents a reliable conclusion.

Do not use `No material defects` for a partial audit.

## No-Finding Report

This snippet begins at `## Findings`. Precede it with the required `# Instruction Quality Audit`, `Audit:`, and `## Audit Scope` sections.

Use:

```markdown
## Findings

None.

## Unresolved Questions

None.

## Summary

Errors: 0
Warnings: 0
Informational findings: 0
Highest-priority corrections:
None.

Verdict: No material defects
```

## Blocked Report

Preserve every top-level marker.

Use:

- `Status: blocked`;
- `Not assessed.` under `## Findings`;
- the blocker or target ambiguity under `## Unresolved Questions`;
- `Errors: Not assessed.`;
- `Warnings: Not assessed.`;
- `Informational findings: Not assessed.`;
- the exact required input under `Highest-priority corrections`;
- `Verdict: Blocked`.

Do not classify unreadable input as target `failure-handling`.

## Multiple Reports

For one report, `Verdict: <value>` must be the final content line of the response.

For multiple reports, separate reports with a line containing only `---`. Within each report, `Verdict: <value>` must be the final content line before the separator or the end of the response.

Number findings sequentially within each report, beginning at `IQA-001`. Restart numbering at `IQA-001` in each subsequent report.

Do not add commentary before, between, or after the reports.
