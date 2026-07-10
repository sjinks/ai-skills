Read this reference when producing or validating an Agent/Skill Readiness Audit report.

# Readiness Report Contract

Produce one report per distinct target package or standalone artifact.

Within each report, use these top-level markers exactly once and in this order.

The canonical template uses these uppercase placeholders. Replace them with actual values; do not emit the placeholder names literally.

- `TARGET_NAME_OR_PATH` - audited target name or path.
- `ARTIFACT_TYPE` - one of `Agent Skill`, `Custom agent`, `Persistent instructions`, `Other`.
- `AUDIT_MODE` - one of `core`, `package`, `path`.
- `AUDIT_STATUS` - one of `completed`, `partial`, `blocked`.
- `MODEL_LIST` - supplied target models or the evaluated default set.
- `RUNTIME_LIST_OR_NOT_SUPPLIED` - supplied runtimes or `Not supplied`.
- `FILE_OR_ITEM` - one included or excluded file or artifact.
- `REASON` - exclusion reason.
- `NONE_OR_DESCRIPTION` - `None.` or a concrete limitation description.
- `AREA_RATING` - integer `1` through `5`.
- `RISK_OR_NONE` - a concrete main risk for the readiness area or `None.`.
- `FINDING_TITLE` - concise finding title.
- `FINDING_SEVERITY` - one of `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.
- `AREA_NAME` - the affected readiness area.
- `FILE_AND_SECTION_OR_LINE` - grounding location.
- `SHORT_EXACT_EXCERPT` - exact supporting quote.
- `OBSERVABLE_FAILURE_OR_MAINTENANCE_RISK` - concrete risk.
- `SPECIFIC_CORRECTIVE_TASK` - specific corrective action.
- `MODEL` - target model name.
- `MODEL_VERDICT` - one of `Suitable`, `Suitable with limitations`, `Unsuitable`, `Not assessed`.
- `MAIN_RISK_OR_NONE` - model-specific main risk or `None.`.
- `REQUIRED_ADAPTATION_OR_NONE` - required adaptation or `None.`.
- `HIGHEST_IMPACT_CHANGE` - highest-priority recommended change.
- `READINESS_VERDICT` - one of `Ready`, `Ready with limitations`, `Needs revision`, `Major redesign`, `Blocked`.

Allowed readiness verdicts are:

- `Ready`
- `Ready with limitations`
- `Needs revision`
- `Major redesign`
- `Blocked`

Allowed target-model verdicts are:

- `Suitable`
- `Suitable with limitations`
- `Unsuitable`
- `Not assessed`

These values apply only to `MODEL_VERDICT` table cells. Section-content sentences such as `Not assessed.` in blocked reports are not target-model verdict values.

```markdown
# Agent/Skill Readiness Audit

Audit: TARGET_NAME_OR_PATH

## Audit Scope

- Artifact type: ARTIFACT_TYPE
- Mode: AUDIT_MODE
- Status: AUDIT_STATUS
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
| Discovery and delegation | AREA_RATING | RISK_OR_NONE |
| Instruction architecture | AREA_RATING | RISK_OR_NONE |
| Operational completeness | AREA_RATING | RISK_OR_NONE |
| Model and runtime portability | AREA_RATING | RISK_OR_NONE |
| Maintainability and evaluability | AREA_RATING | RISK_OR_NONE |

## Material Findings

### ASR-001 — FINDING_TITLE

Severity: FINDING_SEVERITY
Area: AREA_NAME
Locations:
- FILE_AND_SECTION_OR_LINE
Evidence:
> SHORT_EXACT_EXCERPT
Risk: OBSERVABLE_FAILURE_OR_MAINTENANCE_RISK
Correction: SPECIFIC_CORRECTIVE_TASK

## Target-Model Compatibility

| Model | Verdict       | Main risk         | Required adaptation         |
| ----- | ------------- | ----------------- | --------------------------- |
| MODEL | MODEL_VERDICT | MAIN_RISK_OR_NONE | REQUIRED_ADAPTATION_OR_NONE |

## Priority Changes

1. HIGHEST_IMPACT_CHANGE

Verdict: READINESS_VERDICT
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

For one report, `Verdict: READINESS_VERDICT` must be the final content line of the response.

For multiple reports, `Verdict: READINESS_VERDICT` must be the final content line of each report. Blank lines may appear after that content line. The next nonblank line must be `---` or the end of the response.

Number material findings sequentially within each report as `ASR-001`, `ASR-002`, and so on. Restart numbering at `ASR-001` in each subsequent report.

Do not add commentary before, between, or after the reports.
