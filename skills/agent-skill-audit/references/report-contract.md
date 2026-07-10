Read this reference when producing or validating an Agent/Skill Readiness Audit report.

# Readiness Report Contract

Produce one report per distinct target package or standalone artifact.

Within each report, use these top-level markers exactly once and in this order.

Uppercase tokens such as `TARGET_NAME_OR_PATH`, `MODEL_LIST`, and `RISK_OR_NONE`, plus angle-bracket tokens such as `<value>`, are placeholders. Replace them with actual values; do not emit the placeholder names literally.

Allowed target-model verdicts are:

- `Suitable`
- `Suitable with limitations`
- `Unsuitable`
- `Not assessed`

```markdown
# Agent/Skill Readiness Audit

Audit: TARGET_NAME_OR_PATH

## Audit Scope

- Artifact type: Agent Skill | Custom agent | Persistent instructions | Other
- Mode: core | package | path
- Status: completed | partial | blocked
- Target models: MODEL_LIST
- Target runtimes: RUNTIME_LIST_OR_NOT_SUPPLIED
- Files included:
  - FILE_OR_ITEM
- Files excluded:
  - FILE_OR_ITEM — REASON
- Limitations: NONE_OR_DESCRIPTION

## Readiness Ratings

| Area | Rating | Main risk |
|---|---:|---|
| Discovery and delegation | 1-5 | RISK_OR_NONE |
| Instruction architecture | 1-5 | RISK_OR_NONE |
| Operational completeness | 1-5 | RISK_OR_NONE |
| Model and runtime portability | 1-5 | RISK_OR_NONE |
| Maintainability and evaluability | 1-5 | RISK_OR_NONE |

## Material Findings

### ASR-001 — TITLE

Severity: CRITICAL | HIGH | MEDIUM | LOW
Area: AREA_NAME
Locations:
- FILE_AND_SECTION_OR_LINE
Evidence:
> SHORT_EXACT_EXCERPT
Risk: OBSERVABLE_FAILURE_OR_MAINTENANCE_RISK
Correction: SPECIFIC_CORRECTIVE_TASK

## Target-Model Compatibility

Use one target-model verdict from the allowed list above for each `MODEL_VERDICT` value.

Uppercase tokens such as `MODEL`, `MODEL_VERDICT`, `MAIN_RISK_OR_NONE`, and `REQUIRED_ADAPTATION_OR_NONE` are placeholders. Replace them with actual values; do not emit the placeholder names literally.

| Model | Verdict       | Main risk         | Required adaptation         |
| ----- | ------------- | ----------------- | --------------------------- |
| MODEL | MODEL_VERDICT | MAIN_RISK_OR_NONE | REQUIRED_ADAPTATION_OR_NONE |

## Priority Changes

1. HIGHEST_IMPACT_CHANGE

Verdict: Ready | Ready with limitations | Needs revision | Major redesign | Blocked
```

## Empty Sections

The following snippets replace only the named section and its content. They do not permit omission of the other required report markers.

When no material finding exists, write:

```markdown
## Material Findings

None.
```

When no priority change exists, write:

```markdown
## Priority Changes

None.
```

## Blocked Report

Preserve every top-level marker.

Use:

- `Status: blocked`;
- `Not assessed.` under `## Readiness Ratings`;
- `Not assessed.` under `## Material Findings`;
- `Not assessed.` under `## Target-Model Compatibility`;
- the exact input needed under `## Priority Changes`;
- `Verdict: Blocked`.

Do not assign rating `1` merely because input is unavailable.

## Multiple Reports

For one report, `Verdict: <value>` must be the final content line of the response.

For multiple reports, separate reports with a line containing only `---`. Within each report, `Verdict: <value>` must be the final content line before the separator or the end of the response.

Number material findings sequentially within each report as `ASR-001`, `ASR-002`, and so on. Restart numbering at `ASR-001` in each subsequent report.

Do not add commentary before, between, or after the reports.
