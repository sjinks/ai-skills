# Skill vocabulary

Use this convention when maintaining canonical `skills/**`. Each package retains its own operational rules and rubric so it works when installed alone. This document governs repository authoring; it is not a runtime dependency.

## Shared concepts

| Term | Meaning |
|---|---|
| Finding | An evidence-backed defect or risk with a concrete consequence and correction. |
| Severity | Impact of the finding; use `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW`, highest applicable first. |
| Assessment confidence | Reliability of the assessment; use lowercase `high`, `medium`, or `low`. A skill may exclude low-confidence findings. |
| Classification | Kind of finding or evidence, independent of impact. |
| Priority | Urgency or planned ordering of work; not a synonym for severity. |
| Status | State of an artifact, finding, operation, or assessment. |
| Verdict | Overall decision for the skill's declared scope, under its local decision rules. |
| Evidence | An inspected source, observed result, or explicitly qualified inference supporting a claim. |
| Limitation | A boundary on coverage, evidence, or capability; not automatically a target defect. |
| Note | Non-defect context, creation metadata, or assumptions; never a severity level. |

## Severity

| Value | Impact anchor |
|---|---|
| `CRITICAL` | Credible severe or irreversible harm to security, privacy, safety, integrity, or the primary operation. |
| `HIGH` | Major correctness, contract, reliability, security, or operational harm on a realistic path. |
| `MEDIUM` | Meaningful bounded regression, ambiguity, change cost, or operational harm. |
| `LOW` | Minor localized correctness, comprehension, or maintenance harm. |

Define domain-specific anchors in each emitting package. Evaluate impact separately from confidence, status, and priority. Do not inflate severity because evidence is unavailable, several files are involved, or a finding uses strong wording. A missing-input diagnostic rates the review obstacle only when a package explicitly requires that diagnostic; it does not rate unseen target behavior.

`NONE` and `UNASSESSED` are report/action sentinels only where a package explicitly defines them; they are not finding severities. `unknown` in an incomplete finding row likewise means missing impact evidence. `note` may appear in PR/commit report entries for non-defect context; it is not a fifth severity. Keep required no-findings and blocked templates exact.

## Decisions and domain vocabulary

Use `BLOCK`, `CONCERNS`, and `CLEAN` for general review decisions where those values are already canonical. Keep domain decisions such as readiness (`Ready`), requirement decidability (`SHARP`), test quality (`solid`), construction (`VALID`), execution (`VERIFIED`), and completion (`Complete`) distinct. Their meanings do not collapse into a universal pass/fail enum. Keep package-specific marker names, ordering, acceptance conditions, and verdict precedence.

For general risk classification, prefer `Confirmed issue`, `Likely risk`, `Open question`, `Accepted tradeoff`, and `Test gap`. Preserve domain classifications when they carry additional meaning: sanitizer outcomes, CERT exceptions, layout safety, measurement gaps, and defense in depth. Preserve external/tool literals, log levels, code identifiers, quotations, source-confidence metadata, and explicitly defined domain scales such as cause determination or numeric escalation scores.

## Input compatibility and migration

New finding outputs use canonical uppercase severity. Do not infer impact from legacy action labels (`blocker`, `should-fix`, `suggestion`) or diagnostic kinds (`error`, `warning`, `information`); reassess supported impact when the skill owns assessment, otherwise request the missing impact evidence.

Consumers keep only their explicitly declared, case-sensitive compatibility mappings. The merge gate accepts `High`/`Medium`/`Low` as input aliases and preserves `CRITICAL` separately from `HIGH`. The test planner also accepts its legacy `Critical`/`Warning`/`Suggestion` input rubric; that legacy `Critical` maps to must-have priority, not automatically to canonical `CRITICAL` severity. Unrecognized labels remain unmapped or block the gate as locally defined. Preserve original labels where the consumer requires provenance.

This is an output-contract migration for consumers parsing old severity names. Instruction-audit summary counts now use `Critical:`, `High:`, `Medium:`, and `Low:`. PR/commit informational entries now use `note`; the PR reduced disclosure signal uses `present`/`none` independently of severity. Existing verdict and acceptance rules continue to govern decisions.

## Maintenance check

Run `python3 scripts/check-skill-vocabulary.py` from the repository root. It inventories every canonical package, checks literal severity fields/rubrics and four-level vocabulary coverage, and flags obsolete report projections. This static check does not prove rubric equivalence or model behavior. Review related rules, templates, examples, README files, and consumers whenever a contract changes. Do not edit generated or experimental copies as canonical packages.
