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

## Classification and disposition

Classification describes the evidenced kind of finding. General risk reports use `Confirmed issue`, `Likely risk`, `Open question`, `Accepted tradeoff`, `Test gap`, and, where supported, `Defense-in-depth`. Use `Open question` for unavailable context or an unresolved decision; the legacy `Needs more evidence` label does not establish a defect. Preserve explicit domain classifications such as sanitizer outcomes and CERT exceptions.

Disposition describes the action or routing. It is independent of classification, impact, and finding state. Packages declare their allowed dispositions and precedence. For SSRF reports, `fix-now` selects an evidenced correction, `add-verification` selects a missing check for known behavior, `clarify` requests evidence or a decision before selecting a correction, `defer-with-owner` records an agreed owned plan, and `retain-accepted` records existing accountable-owner acceptance. These last two values require their stated metadata; an agent cannot invent acceptance. Former SSRF labels `blocker` and `follow-up` alone cannot determine evidentiary classification. Inapplicability belongs to checklist coverage, not a finding.

## Missing information and empty results

| Value | Meaning |
|---|---|
| `None` | The assessed collection or section has no entries. |
| `unknown` | A value is undetermined; this does not imply an assessment ran. |
| `not-assessed` | The requested assessment was not performed or required evidence was unavailable. |
| `n/a` | The check is structurally or explicitly out of scope; give the reason. Missing input is not inapplicability. |

Keep collection emptiness, value uncertainty, assessment coverage, and inapplicability separate. Use `Findings: None` for the shared literal no-findings marker. Preserve package-specific sentence punctuation, external literals, and explicitly defined schema sentinels. Existing `Not assessed` prose and `UNASSESSED` impact sentinels retain their locally defined representation of unavailable assessment; neither means no defect exists. Artifact states such as `needs-author-input` remain distinct from finding lifecycle.

## Coverage

For checklist/requirement coverage, use the first matching state: justified `n/a` for an inapplicable check, `gap` for an evidenced unmet applicable requirement, `not-assessed` for unavailable requested assessment/evidence, otherwise `covered` when inspected evidence satisfies every applicable part. Disclose unassessed subparts even when a known gap determines the item state. A missing control and missing evidence are different results. A waiver or deferral does not convert an unmet requirement to covered. Missing requested coverage prevents a clean whole-scope assessment; preserve stronger local blocking rules and explicitly limited part-only verdicts.

For review progress, use `reviewed` for inspected scope, `not-assessed` for required scope not inspected, and justified `n/a`. Reviewed scope can contain findings. Preserve explicit domain progress outcomes such as `swept` and `skipped`, but state their scope: a skipped requested assessment is not evidence that its requirement holds. Criteria-only reviews may report criterion quality as clean while feature coverage remains explicitly outside the assessment.

## Finding lifecycle

| State | Required meaning |
|---|---|
| `open` | The finding remains unresolved or its correction lacks required verification. |
| `fixed` | The underlying defect is removed and the resolution criterion is verified. |
| `deferred` | The defect remains under an agreed plan with owner, target, remediation steps and tracking reference. |
| `waived` | The defect remains with explicit accountable-owner risk acceptance, scope, rationale and follow-up reference or wontfix rationale. |

A package may emit a subset. Code-quality reports emit `open`/`fixed`; the merge gate emits all four. Normalize legacy `Open`/`Resolved`, `owned-with-remediation-plan`, and `waived-with-rationale` only through the package's declared mappings and destination-state evidence requirements. Thread closure, ownership, and proposals do not prove a fix. Fix evidence is not interchangeable with waiver evidence. These states do not themselves grant merge permission; high-impact deferrals still fail the gate under its local rules. Stable acceptance-condition labels such as `Resolved when` are not lifecycle enum values.

## Decisions and domain vocabulary

Use `BLOCK`, `CONCERNS`, and `CLEAN` for general review decisions where those values are already canonical. Keep domain decisions such as readiness (`Ready`), requirement decidability (`SHARP`), test quality (`solid`), construction (`VALID`), execution (`VERIFIED`), and completion (`Complete`) distinct. Their meanings do not collapse into a universal pass/fail enum. Keep package-specific marker names, ordering, acceptance conditions, and verdict precedence.

For general risk classification, prefer `Confirmed issue`, `Likely risk`, `Open question`, `Accepted tradeoff`, and `Test gap`. Preserve domain classifications when they carry additional meaning: sanitizer outcomes, CERT exceptions, layout safety, measurement gaps, and defense in depth. Preserve external/tool literals, log levels, code identifiers, quotations, source-confidence metadata, and explicitly defined domain scales such as cause determination or numeric escalation scores.

## Input compatibility and migration

New finding outputs use canonical uppercase severity. Do not infer impact from legacy action labels (`blocker`, `should-fix`, `suggestion`) or diagnostic kinds (`error`, `warning`, `information`); reassess supported impact when the skill owns assessment, otherwise request the missing impact evidence.

Consumers keep only their explicitly declared, case-sensitive compatibility mappings. The merge gate accepts `High`/`Medium`/`Low` as input aliases and preserves `CRITICAL` separately from `HIGH`. The test planner also accepts its legacy `Critical`/`Warning`/`Suggestion` input rubric; that legacy `Critical` maps to must-have priority, not automatically to canonical `CRITICAL` severity. Unrecognized labels remain unmapped or block the gate as locally defined. Preserve original labels where the consumer requires provenance.

This is an output-contract migration for consumers parsing old severity names. Instruction-audit summary counts now use `Critical:`, `High:`, `Medium:`, and `Low:`. PR/commit informational entries now use `note`; the PR reduced disclosure signal uses `present`/`none` independently of severity. Existing verdict and acceptance rules continue to govern decisions.

The shared-state migration also separates SSRF `Classification` from `Disposition`, replaces generic coverage `missing` with `gap` or `not-assessed`, emits lowercase finding lifecycle states, and uses exact `None` empty markers (including compliant acceptance-criterion contract-gap cells). Update parsers for these emitted contracts; only the explicit input aliases remain compatible.

## Maintenance check

Run `python3 scripts/check-skill-vocabulary.py` from the repository root. Shared-state checks also reject obsolete generic coverage enums, action labels in Classification fields, legacy emitted finding states in the declared code-quality/gate report profiles, and lowercase no-findings markers. Unrelated domain artifact statuses retain their own values. It inventories every canonical package, validates each literal severity enum and rubric locally, and flags obsolete report projections. Every enum with multiple impact alternatives and every detected rubric must declare all four levels; unrelated README text, examples, or another declaration cannot supply missing levels. Referenced rubric files are checked in their own declaration scope. Code and bold formatting are removed before every literal member is checked, including alternatives inside angle-bracket templates. Scalar samples, exact schema placeholders, descriptive slots, explanatory prose, and declared legacy-input tables retain their distinct treatment. This static check does not prove rubric equivalence or model behavior. Review related rules, templates, examples, README files, and consumers whenever a contract changes. Do not edit generated or experimental copies as canonical packages.
