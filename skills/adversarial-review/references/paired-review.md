# Paired Review: Cross-Pass Rules

Read this when this skill runs *after a prior adversarial-review pass on the same target* and you must decide which findings are new and what verdict to emit. For a first pass, or when the prior output came from a different skill or review, these rules do not apply — treat that output as the target under review.

These rules apply only against a prior pass that emitted this skill's Output Format markers (`Artifact:`, `Category:`, `Trigger:`, `Verdict:`). A prior output lacking those fields is the target under review, not a prior pass; the Paired-review "avoid re-reporting" guidance in `SKILL.md` still applies to it.

## Dedup criterion

Treat a candidate finding as already covered only when a prior finding matches all three of:

1. the same artifact,
2. the same `Failure-Mode Taxonomy` category, and
3. the same concrete trigger.

If any of the three differ, the candidate survives: keep it and note the related prior finding in its `Evidence:` line rather than suppressing it.

## Verdict monotonicity

Verdict strength order: `BLOCK` > `CONCERNS` > `CLEAN`.

Do not emit a verdict weaker than the strongest prior verdict on the same target. If your net-new findings alone would justify a weaker verdict, emit the prior verdict instead, restate the prior finding(s) that justify it, and note in `Evidence basis` that the verdict is retained from a prior pass.

When multiple prior passes exist, apply both rules against *every* prior pass on the same target, not only the most recent one.
