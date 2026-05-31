---
name: multi-lens-review
description: "Use when: structuring a multi-lens review of a change, spec, design, or implementation; combining intent, design, implementation, security, adversarial, and verification perspectives, then synthesizing them into a single integrated decision."
argument-hint: "Describe the change, artifact, or decision and the lenses worth applying."
user-invocable: true
---

# Multi-Lens Review

Use this skill to walk a single change or decision through several review lenses and synthesize the findings into one decision with required actions and residual risk.

This skill describes lenses a single assistant adopts in turn. It is not a multi-agent panel. The lenses are perspectives, not independent reviewers — apply each honestly and resist consensus when a lens surfaces a genuine concern.

## When to Use

Use this skill when a change is non-trivial enough that one lens alone would miss material risk:

- A spec, design, implementation, or workflow that affects more than one concern (correctness, security, data, UX, ops).
- A change where required fixes and follow-ups must be separated for a merge decision.
- A review that has to reconcile tradeoffs between lenses (e.g. ergonomics vs. security, speed vs. correctness).

Do not use it for single-lens questions that have an obvious owner (e.g. "is this regex correct?", "does this CSS validate?"). Prefer an installed/available focused skill (`adversarial-review`, `review-cycle-gatekeeper`, `ssrf-outbound-fetch-review`, `nestjs-code-review`, `nestjs-development`) when the work is squarely in its scope; reach for `multi-lens-review` when the work spans several of them.

## Boundaries

- Review only artifacts the user is authorized to inspect.
- Apply only lenses that add value for the target. Skipping a lens is valid; pretending to apply one is not.
- A single assistant cannot produce truly independent perspectives. Do not present lens output as if it came from separate reviewers, and do not stage fake disagreement.
- Separate confirmed defects, likely risks, open questions, accepted tradeoffs, and test gaps; do not merge them into a single "issues" bucket.
- Do not invent findings to fill a lens. A lens with no finding is a valid result.

## Required Input Context

Collect the narrowest useful context before judging:

- Target artifact and content type: spec, design, diff, file set, workflow, runbook, or test plan.
- Goal, scope, non-goals, and explicit constraints.
- Acceptance criteria or success conditions, if any.
- Trust boundaries, data sensitivity, and affected actors when relevant.
- Existing tests, prior reviews, related issues, and known tradeoffs.

If the target is missing, unreadable, or too vague to identify intended behavior, emit `BLOCK` with the specific missing context rather than guessing.

## Lenses

Apply only the lenses that add value. Each lens has a narrow question, a non-goal, and an expected output.

A lens may delegate to a focused skill, when installed/available, if the target falls squarely in that skill's scope (for example: `adversarial-review` from the Adversarial lens, `ssrf-outbound-fetch-review` or `nestjs-code-review` from the Security & Privacy or Implementation lens). When delegating, record the focused skill's verdict in the lens summary, identify the delegated report by an explicit identifier the caller can resolve (an inline appendix block, a reproduced report immediately following the multi-lens output, or a link to a prior emitted block), and do not duplicate the delegated findings.

### 1. Intent / Spec

- **Question:** Are the goal, scope, and acceptance criteria clear and consistent with the target?
- **Non-goal:** Critiquing implementation details.
- **Output:** Restated intent, missing or ambiguous requirements, conflicting constraints.

### 2. Design

- **Question:** Does the proposed approach fit the codebase, constraints, and tradeoffs? Are there material alternatives?
- **Non-goal:** Line-level code review.
- **Output:** Design decisions, alternatives considered, integration risks, migration or rollback concerns.

### 3. Implementation

- **Question:** Does the code correctly realize the intent and design? Are there bugs, contract mismatches, or unintended behavior changes?
- **Non-goal:** Re-litigating the design.
- **Output:** Concrete defects or regressions with file/line evidence and a suggested fix.

### 4. Security & Privacy

- **Question:** What auth, injection, secrets, data-exposure, tenancy, or trust-boundary risk does the change introduce or fail to address?
- **Non-goal:** Generic checklists not grounded in the target.
- **Output:** Security findings tied to specific code paths or controls; explicit "no material change" when applicable.

### 5. Adversarial

- **Question:** What realistic edge, ordering, timeout, dependency, or misuse condition breaks the promise?
- **Non-goal:** Hypothetical attacks unmoored from the target.
- **Output (direct):** Failure modes with concrete triggers, recorded under `Findings:` with `Lens: Adversarial`.
- **Output (delegated):** When the target warrants the full taxonomy and `adversarial-review` is installed/available, delegate to it; summarize its verdict, the count of its findings, and the worst severity in the `Lens findings:` line. Treat the delegated report as the canonical finding list — do not restate its entries under `Findings:`. The delegated verdict feeds the overall verdict per `## Severity And Verdict`.

### 6. Verification

- **Question:** Are the behaviors that matter tested or otherwise verified? What is unverified?
- **Non-goal:** Demanding coverage for cosmetic or out-of-scope behavior.
- **Output:** Specific unverified behaviors and the failure each missing test should catch, or "verification adequate" with rationale. A Verification "Suggested fix" may itself be a concrete test specification.

## Synthesis

Synthesis is not a lens — it inspects the other lenses' output rather than the target. Run synthesis when two or more lenses produced findings or when any two lenses conflict. If only one lens produced findings, skip synthesis; that lens's findings feed directly into the required-actions / follow-ups split in step 5 and the overall verdict assigned in step 6 of `## Procedure`. If no lens produced findings, skip synthesis; the overall verdict is `CLEAN` unless the `BLOCK`-on-insufficient-input rule applies.

- **Trigger:** Two or more lenses produced findings, or any two lenses conflict (per the paragraph above).
- **Inputs:** All applied lens outputs.
- **Produces:** Deduplicated findings, conflict resolutions with the chosen tradeoff and the winning lens named, identified coverage gaps, required actions vs. follow-ups, residual risk, and the overall verdict. These map to the `Conflicts between lenses:`, `Required actions:`, `Follow-ups:`, and `Residual risk:` lines of the Output Format.

## Severity And Verdict

Use severity for findings:

- `CRITICAL`: exploitable or triggerable now with no compensating control; irreversible or production-impacting; severe security, privacy, data-loss, safety, legal, or business harm.
- `HIGH`: exploitable or triggerable in normal use; mitigations may exist but acceptance must be explicit; major user, tenant, reliability, security, or data-integrity harm.
- `MEDIUM`: credible but bounded impact; meaningful failure, regression, operational burden, or user harm worth fixing or tracking.
- `LOW`: low likelihood or limited impact; localized ambiguity or minor maintainability risk worth noting.

MEDIUM uses `credible` instead of `adversarial-review`'s `plausible` because this skill has a separate confidence axis (`medium` confidence is "plausible from the evidence"); reusing `plausible` on both axes would collapse impact and evidentiary strength into the same word. The two skills' severity remain semantically aligned — only the MEDIUM-impact adjective differs.

Use confidence per finding:

- `high`: direct evidence in the reviewed material.
- `medium`: plausible from the evidence but would benefit from confirmation.
- `low`: suspicion based on partial signals; flag for follow-up rather than treating as fact.

Use one overall verdict:

- `BLOCK`: at least one `CRITICAL`, any `HIGH` without a compensating control or explicit accepted tradeoff, or insufficient input to evaluate the target.
- `CONCERNS`: actionable findings remain, but the target may proceed with mitigation or explicit acceptance.
- `CLEAN`: no actionable findings across applied lenses. Residual caveats may still be listed.

## Procedure

1. Identify the target, intended behavior, and applicable lenses. State which lenses are skipped and why.
2. Collect required input context; emit `BLOCK` if it is too thin to evaluate the target.
3. Walk each selected lens in the order listed above (Intent / Spec → Design → Implementation → Security & Privacy → Adversarial → Verification). For each lens, write findings using its expected output shape. A lens may delegate to a focused skill when installed/available; record the delegated verdict in the lens summary. A lens with no finding records `None` rather than being omitted from the log.
4. Run Synthesis when the conditions in `## Synthesis` apply: deduplicate findings, reconcile conflicts (state the tradeoff explicitly and which lens wins), and identify coverage gaps. The synthesis outputs are recorded in the `Conflicts between lenses:`, `Required actions:`, `Follow-ups:`, and `Residual risk:` lines of the Output Format, and feed the overall verdict.
5. Separate required actions (must clear before merge) from follow-ups (track but do not block).
6. Assign the overall verdict and state residual risk.

## Output Format

The `Lens findings:` block is a one-line summary per applied lens. The `Findings:` block is the numbered detail list; each entry's `Lens:` field cross-references back to the lens that produced it. Do not duplicate detail between the two blocks.

The template below is a partial example: Intent / Spec, Security & Privacy, Adversarial, and Verification are shown as applied; Design and Implementation are assumed under `Lenses skipped:`. Include one `Lens findings:` line per applied lens only — lenses listed under `Lenses skipped:` do not appear in the `Lens findings:` block. The template shows only emitted content; do not copy any explanatory prose from this document into the output.

```text
Verdict: BLOCK | CONCERNS | CLEAN
Target: <artifact and content type>
Intended behavior: <one or two sentences>
Lenses applied: <comma-separated list>
Lenses skipped: <comma-separated list with one-clause reason each, or None>
Synthesis: applied | skipped (<reason>)
Evidence basis: <files, sections, tests, logs, or context reviewed>
Assumptions: <explicit assumptions or "None beyond reviewed material">

Lens findings:
- Intent / Spec: <summary or None>
- Security & Privacy: <summary or None>
- Adversarial: <summary or None>
- Verification: <summary or None>

Findings:
1. <short title>
  Lens: <lens name>
  Artifact: <file, section, component, or step>
  Severity: CRITICAL | HIGH | MEDIUM | LOW
  Confidence: high | medium | low
  Classification: Confirmed issue | Likely risk | Open question | Accepted tradeoff | Test gap
  Trigger: <concrete scenario>
  Risk: <impact>
  Evidence: <observation>
  Suggested fix: <focused mitigation, test, decision, or acceptance criterion>

Conflicts between lenses: <reconciliation or None>
Required actions: <items that must clear before merge, or None>
Follow-ups: <tracked but non-blocking items, or None>
Residual risk: <remaining caveats after required actions, or "No material residual risk identified">
```

If no findings exist, replace the entire `Findings:` block with `Findings: None`. Lenses that were not applied are omitted from `Lens findings:` (they are already listed under `Lenses skipped:`). For `BLOCK` on a missing, unreadable, or insufficient target, emit a single `Open question` entry under `Findings:` describing the blocker and use `Pending - target unavailable` for `Required actions`.

When `Synthesis: skipped`, render `Conflicts between lenses: None` and populate `Required actions:` / `Follow-ups:` / `Residual risk:` directly from the applied lens(es) per Procedure steps 5–6.

## Anti-Patterns

- Role-playing independent reviewers and presenting their "disagreements" as real.
- Applying every lens by default. Choose the smallest useful set and record what was skipped.
- Merging required fixes and follow-ups into one list, hiding the merge gate.
- Stopping at "needs tests"; name the specific unverified behavior and the failure the test should catch.
- Resolving lens conflicts silently. State the tradeoff and the winner.
- Using this skill instead of an installed/available focused one when the work is squarely in the focused skill's scope.
