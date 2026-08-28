# Paired Review: Cross-Pass Rules

Read this when this skill runs *after a prior adversarial-review pass on the same target revision* and you must decide which findings are new and what verdict to emit. For a first pass, a revised target, or prior output from a different skill or review, these rules do not apply as monotonic constraints. When a revised target is supplied, verify whether prior findings were resolved and review the revised artifact on its current evidence.

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

When multiple prior passes exist, apply both rules against *every* prior pass on the same target revision, not only the most recent one.
