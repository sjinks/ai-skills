# Paired Review: Cross-Pass Rules

Read this when this skill runs *after a prior adversarial-review pass on the same target revision* and you must decide which findings are new and what verdict to emit. For a first pass, a revised target, or prior output from a different skill or review, these rules do not apply as monotonic constraints. When a revised target is supplied, verify whether prior findings were resolved and review the revised artifact on its current evidence.

Revision identity follows the precedence rule in `SKILL.md`. Changed artifact content or target-defining context, an explicitly new or changed revision, differing revision identifiers, or missing or ambiguous identity means a revised target and overrides matching identifiers or unchanged claims. Target-defining context includes intended behavior, requirements, constraints, controls, and evidence about the artifact; a new observation produced by the later review alone does not change the revision. Otherwise, an uncontradicted unchanged claim or matching explicit immutable identifiers establishes the same revision. For a revised target, use prior findings as context without suppressing current findings or retaining the prior verdict, and record the assumption.

These rules apply only against a prior pass that emitted this skill's Output Format markers (`Artifact:`, `Category:`, `Trigger:`, `Verdict:`). A prior output lacking those fields is the target under review, not a prior pass; the Paired-review "avoid re-reporting" guidance in `SKILL.md` still applies to it.

## Dedup criterion

Treat a candidate finding as already covered only when a prior finding matches all three of:

1. the same artifact,
2. the same `Failure-Mode Taxonomy` category, and
3. the same concrete trigger.

If any of the three differ, the candidate survives: keep it and note the related prior finding in its `Evidence:` line rather than suppressing it.

## Verdict monotonicity

Verdict strength order: `BLOCK` > `CONCERNS` > `CLEAN`.

Do not emit a verdict weaker than the strongest prior verdict whose supporting findings remain unresolved on the same target revision. Before retaining that verdict, check the available evidence for resolution or explicit owner acceptance of each supporting finding. A verdict may weaken only when the supplied evidence confirms that every finding responsible for the stronger prior verdict is resolved or validly accepted.

When retaining a prior verdict, reference the prior finding titles or identifiers in `Evidence basis`; do not add unchanged prior findings as fresh entries under `Findings`. List only net-new findings or prior findings whose category, trigger, evidence, severity, or mitigation status materially changed.

When retaining a non-`CLEAN` verdict with no net-new or materially changed findings, emit `Findings: None`. Name the unresolved prior finding titles or identifiers in `Evidence basis`; do not repeat them as fresh findings.

When multiple prior passes exist, apply both rules against *every* prior pass on the same target revision, not only the most recent one.
