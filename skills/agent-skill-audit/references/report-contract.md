Read this reference when producing or validating an Agent/Skill Readiness Audit report.

# Readiness Report Contract

Produce one report per distinct target package or standalone artifact.

Use these top-level markers exactly once and in this order.

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

| Model | Verdict | Main risk | Required adaptation |
|---|---|---|---|
| MODEL | Suitable | None | None |

## Priority Changes

1. HIGHEST_IMPACT_CHANGE

Verdict: Ready | Ready with limitations | Needs revision | Major redesign | Blocked
```

## Empty Sections

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

Separate complete reports with `---`.

Do not append any text after each report's `Verdict:` line.
