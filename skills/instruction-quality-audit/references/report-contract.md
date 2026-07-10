Read this reference when producing or validating an Instruction Quality Audit report.

# Instruction Quality Report Contract

Produce one report per distinct target package or standalone artifact.

Within each report, use these top-level markers exactly once and in this order.

The canonical template uses these uppercase placeholders. Replace them with actual values; do not emit the placeholder names literally.

- `TARGET_NAME_OR_PATH` - audited target name or path.
- `AUDIT_MODE` - one of `core`, `package`, `path`.
- `AUDIT_STATUS` - one of `completed`, `partial`, `blocked`.
- `FILE_OR_ITEM` - one effective instruction file or item.
- `PATH_OR_NONE` - mutually exclusive path or `None.`.
- `RULE_OR_NONE` - trusted custom diagnostic rule or `None.`.
- `NONE_OR_DESCRIPTION` - `None.` or a concrete limitation description.
- `FINDING_TITLE` - concise finding title.
- `FINDING_SEVERITY` - one of `error`, `warning`, `information`.
- `FINDING_CONFIDENCE` - one of `high`, `medium`.
- `FINDING_TYPE` - one of `contradiction`, `precedence`, `ambiguity`, `terminology`, `authority`, `side-effect`, `closure`, `failure-handling`, `cognitive-load`, `duplication`, `output-contract`, `custom`.
- `FILE_AND_SECTION_OR_LINE` - grounding location.
- `EXACT_RELEVANT_INSTRUCTION` - exact supporting quote.
- `SECOND_EXCERPT_WHEN_NEEDED` - second exact supporting quote when needed.
- `CONCRETE_MODEL_OR_EVAL_FAILURE` - concrete behavioral risk.
- `EXACT_REWRITE_OR_SPECIFIC_STRUCTURAL_CHANGE` - exact rewrite or specific corrective action.
- `UNRESOLVED_QUESTION_OR_NONE` - unresolved question text or `None.`.
- `ERROR_COUNT` - non-negative integer count of error findings.
- `WARNING_COUNT` - non-negative integer count of warning findings.
- `INFORMATIONAL_FINDING_COUNT` - non-negative integer count of informational findings.
- `CORRECTION` - highest-priority correction.
- `VERDICT_VALUE` - one of `No material defects`, `Needs revision`, `Blocked`.

````markdown
# Instruction Quality Audit

Audit: TARGET_NAME_OR_PATH

## Audit Scope

- Mode: AUDIT_MODE
- Status: AUDIT_STATUS
- Effective instruction files:
  - FILE_OR_ITEM
- Mutually exclusive paths:
  - PATH_OR_NONE
- Trusted custom diagnostics:
  - RULE_OR_NONE
- Limitations: NONE_OR_DESCRIPTION

## Findings

### IQA-001 — FINDING_TITLE

Severity: FINDING_SEVERITY
Confidence: FINDING_CONFIDENCE
Type: FINDING_TYPE
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

UNRESOLVED_QUESTION_OR_NONE

## Summary

Errors: ERROR_COUNT
Warnings: WARNING_COUNT
Informational findings: INFORMATIONAL_FINDING_COUNT
Highest-priority corrections:
1. CORRECTION

Verdict: VERDICT_VALUE
````

## Optional Finding Fields

Omit `Related evidence:` when one excerpt is sufficient.

For cross-file findings, include the co-loaded path in `Locations` or `Behavioral risk`.

## Verdict Selection

Use:

- `Verdict: No material defects` only when `Status: completed` and `## Findings` is `None.`;
- `Verdict: Needs revision` when one or more findings are reported, whether `Status` is `completed` or `partial`;
- `Verdict: Blocked` when `Status: blocked`;
- `Verdict: Blocked` when `Status: partial` and no findings were established.

Do not use `No material defects` for a partial audit.

## Partial No-Finding Snippet

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

For one report, `Verdict: VERDICT_VALUE` must be the final content line of the response.

For multiple reports, `Verdict: VERDICT_VALUE` must be the final content line of each report. Blank lines may appear after that content line. The next nonblank line must be `---` or the end of the response.

Number findings sequentially within each report, beginning at `IQA-001`. Restart numbering at `IQA-001` in each subsequent report.

Do not add commentary before, between, or after the reports.
