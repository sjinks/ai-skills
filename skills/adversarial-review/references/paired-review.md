When to read: when prior review passes are supplied, before deciding revision identity, finding reconciliation, or verdict.

# Paired Review: Cross-Pass Rules

Apply this reference when this skill runs *after a prior adversarial-review pass on the same target revision* and you must decide which findings are new and what verdict to emit. For a first pass, a revised target, or prior output from a different skill or review, these rules do not apply as monotonic constraints. When a revised target is supplied, verify whether prior findings were resolved and review the revised artifact on its current evidence.

Classify revised-target evidence first. Changed artifact content or target-defining context, an explicitly new or changed revision, differing revision identifiers, or missing or ambiguous identity means a revised target and overrides matching identifiers or unchanged claims. Target-defining context includes intended behavior, requirements, constraints, controls, and evidence about the artifact; a new observation produced by the later review alone does not change the revision. Otherwise, an uncontradicted unchanged claim or matching explicit immutable identifiers establishes the same revision. For a revised target, use prior findings as context without suppressing current findings or retaining the prior verdict, and record the assumption.

Recognize a prior pass by the `## Adversarial Review Report` heading and report markers, or by the legacy `Verdict:`, `Target:`, `Evidence basis:`, `Findings:`, and `Residual risk:` envelope. A partial legacy pass is also recognizable when it contains `Verdict:` plus per-finding `Artifact:`, `Category:`, and `Trigger:`. A no-findings report is still a prior pass; do not require per-finding fields when `Findings: None`. Other prior outputs are targets to challenge under the core workflow, not monotonic prior passes.

## Dedup criterion

Treat a candidate finding as already covered only when a prior finding matches all three of:

1. the same artifact,
2. the same `Category` value, and
3. the same concrete trigger.

If any of the three differ, the candidate survives: keep it and note the related prior finding in its `Evidence:` line rather than suppressing it.

## Verdict monotonicity

Verdict strength order: `BLOCK` > `CONCERNS` > `CLEAN`.

Reassess unresolved prior findings using the core severity/control/acceptance mapping even when they are not re-emitted. For example, an unresolved HIGH without a documented control or owner acceptance requires BLOCK even if the prior pass incorrectly used CONCERNS. Combine that result with current findings and the still-supported prior verdict; select the strongest applicable verdict.

Do not emit a verdict weaker than the strongest prior verdict whose supporting findings remain unresolved on the same target revision. Before retaining that verdict, check the available evidence for resolution or explicit owner acceptance of each supporting finding. A verdict may weaken only when the supplied evidence confirms that every finding responsible for the stronger prior verdict is resolved or validly accepted. For a same-revision CRITICAL finding, acceptance alone is not resolution and cannot remove its blocker; apply the core verdict precedence to current findings.

When retaining a prior verdict, reference the prior finding titles or identifiers in `Evidence basis`; do not add unchanged prior findings as fresh entries under `Findings`. List only net-new findings or prior findings whose category, trigger, evidence, severity, or mitigation status materially changed.

When retaining a non-`CLEAN` verdict with no net-new or materially changed findings, emit `Findings: None`. Name the unresolved prior finding titles or identifiers in `Evidence basis`; do not repeat them as fresh findings.

When multiple prior passes exist, apply both rules against *every* prior pass on the same target revision, not only the most recent one.

When retaining a non-CLEAN verdict, carry unresolved blocking mitigations and watch items into `Mitigations / acceptance criteria`, even with `Findings: None`. An unavailable or incomplete prior pass without usable verdict-support evidence is not evidence that the current target is clean; state the limitation and assess current evidence without inventing prior findings.
