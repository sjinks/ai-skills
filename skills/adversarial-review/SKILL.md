---
name: adversarial-review
description: "Use when: performing adversarial review, red-team analysis, edge-case discovery, failure-mode analysis, misuse review, regression hunting, and risk-focused test planning."
argument-hint: "Describe the spec, design, implementation, workflow, migration, runbook, or test plan to challenge."
user-invocable: true
---

# Adversarial Review

Use this skill to deliberately challenge a concrete artifact before relying on it: a spec, design, implementation, workflow, runbook, migration, security control, or test plan.

The goal is to expose plausible failure modes, separate evidence from speculation, and turn the highest risks into tests, mitigations, or acceptance criteria. Be skeptical, precise, and constructive rather than hostile or cynical.

## When to Use

Use this skill when performing adversarial review, red-team analysis, edge-case discovery, failure-mode analysis, misuse review, regression hunting, risk-focused test planning, or pre-ship challenge of an artifact whose failure would matter.

Use it for specs, designs, implementations, workflows, migrations, operational procedures, and test plans. Do not reduce the review to code-only comments unless the target is only code.

## Invocation Modes

Use the same evidence standard whether invoked directly or after another workflow.

- **Standalone review:** Ask for, read, or infer the concrete target artifact before judging it. If the target is missing or too vague, follow the blocker path in Required Input Context.
- **Paired review:** When invoked after another skill, agent, plan, review, or implementation, treat that prior output as the target artifact. Challenge what it produced, identify what it got right, and avoid re-reporting issues it already raised unless the prior output understated the severity, missed evidence, or left the mitigation ambiguous.

When invoked after a *prior adversarial-review pass on the same target*, two extra cross-pass rules govern deduplication and verdict strength. Read [paired-review](./references/paired-review.md) before reconciling findings or emitting a verdict in that case.

## Boundaries

- Review only artifacts and systems the user is authorized to inspect.
- Keep findings actionable, evidence-based, and tied to the target.
- Do not require a fixed number of issues or persona sections. A `CLEAN` verdict is valid when no actionable findings are found after review.
- Calibrate scrutiny to the target's context: a prototype, local tool, production migration, regulated workflow, and security control do not deserve the same intensity or severity threshold.
- Apply the "so what?" filter before reporting a concern: if ignoring it has no meaningful user, system, data, security, privacy, operational, or maintainability consequence, drop it.
- Do not include exploit instructions, weaponizable payloads, live attack steps, or guidance for abusing real systems.
- Do not exercise the target against live systems, users, or production data; reason from artifacts and non-destructive local inspection only.
- Clearly separate confirmed defects, likely risks, open questions, accepted tradeoffs, and test gaps.

## Required Input Context

Collect or read the narrowest useful context before judging:

- Target artifact and content type: spec, design, implementation, workflow, test plan, prior skill output, or other.
- Intended behavior, success criteria, explicit requirements, and non-goals.
- Actors, users, tenants, permissions, data boundaries, and trust boundaries when relevant.
- Inputs, outputs, dependencies, lifecycle, state transitions, rollback paths, and error paths.
- Release context, blast radius, reversibility, and whether the target is prototype, internal, production, regulated, security-sensitive, or safety-sensitive.
- Existing tests, verification evidence, monitoring, runbooks, or acceptance criteria.

Halt and ask for more context, or report a blocker, when the target is empty, missing, unreadable, or too vague to identify intended behavior. If context is partial but usable, proceed with explicitly listed assumptions and caveats. If the assistant halts to ask for context instead of emitting a verdict, the halt must still include the `Target`, best-effort `Intended behavior`, and the specific missing context; otherwise emit `BLOCK`.

## Optional Review Lenses

Apply the lenses that fit the target. Do not force every lens into the output.

- **Breaker/reliability:** What realistic edge, failure, ordering, timeout, or dependency condition breaks the promise?
- **Maintainer:** What future change, unclear contract, duplicated rule, or hidden coupling makes the artifact easy to misuse or regress?
- **Security/privacy:** What permission, identity, tenancy, data exposure, misuse, or trust-boundary failure is plausible?
- **User/workflow:** Where can a user become stuck, confused, misled, blocked, or lose work?
- **Verification:** What important behavior is unproved, unobservable, or only tested through an unrealistic mock?
- **AI-output:** If the target was produced by an AI system, check for happy-path bias, over-acceptance of the requested scope, confidence without evidence, attraction to familiar patterns, reactive patching, and tests rewritten to match implementation instead of intended behavior.

## Failure-Mode Taxonomy

Classify findings using the closest category:

- `requirements-clarity`: Missing, conflicting, ambiguous, or unverifiable requirements.
- `contract-logic`: Contract or logic failures between caller/callee, spec/implementation, UI/API, or workflow/runtime behavior.
- `input-handling`: Input, boundary, malformed data, default, null, duplicate, stale, or adversarial data handling failures.
- `error-rollback`: Error handling, rollback, retry, idempotency, partial-success, or compensation failures.
- `state-concurrency`: State, ordering, concurrency, cache, clock, race, or lifecycle transition failures.
- `auth-tenancy`: Permission, identity, tenancy, privacy, data-boundary, or secret-handling failures.
- `data-integrity`: Persistence, migration, schema, compatibility, durability, or data-integrity failures.
- `resource-lifecycle`: Resource lifecycle, timeout, cancellation, cleanup, scalability, quota, or backpressure failures.
- `user-workflow`: User workflow confusion, irreversible action, silent failure, misleading feedback, or work-loss failures.
- `verification-gap`: Test or verification gaps tied to specific unverified behavior.

Use the label verbatim as the `Category` value.

## Severity And Verdicts

Use severity for findings:

- `CRITICAL`: exploitable or triggerable now with no compensating control; irreversible or production-impacting; severe security, privacy, data-loss, safety, legal, or business harm.
- `HIGH`: exploitable or triggerable in normal use; mitigations may exist but acceptance must be explicit; major user, tenant, reliability, security, or data-integrity harm.
- `MEDIUM`: plausible but bounded impact; meaningful failure, regression, operational burden, or user harm worth fixing or tracking.
- `LOW`: low likelihood or limited impact; localized ambiguity or minor maintainability risk worth noting.

Use one overall verdict:

- `BLOCK`: one or more `CRITICAL` findings, any `HIGH` without a documented compensating control or explicit owner-accepted tradeoff, or a missing/unreadable target that prevents meaningful review.
- `CONCERNS`: actionable issues, likely risks, open questions, or behavior-specific test gaps remain, but the target may proceed with mitigation or explicit acceptance.
- `CLEAN`: no actionable findings found after reviewing the available target and context. Residual caveats may still be listed.

For every non-`CLEAN` verdict, distinguish blocking mitigations from non-blocking watch items. Blocking mitigations are required before relying on, shipping, or merging the target; watch items are lower-risk follow-up, monitoring, or owner-accepted caveats.

## Evidence Standard

Classify each substantive finding:

- **Confirmed issue:** Direct evidence shows the artifact violates stated or clearly implied intended behavior, or a widely shared correctness, security, privacy, or safety norm.
- **Likely risk:** A plausible trigger could cause harm, but confirmation would require more execution, domain input, or data.
- **Open question:** A decision or requirement is missing and changes the risk assessment.
- **Accepted tradeoff:** The risk is real, documented, and intentionally accepted by the artifact or user.
- **Test gap:** A specific important behavior is not verified by the available tests or evidence.

Every substantive finding must name a concrete trigger or scenario. Do not present speculation as fact; state what evidence supports the claim and what remains unknown.

## Procedure

1. Identify the target artifact and content type.
2. Read the available artifact and nearby context needed to understand it.
3. State the intended behavior in one or two sentences.
4. Steel-man the target before challenging it: briefly state what the current approach gets right, why it is reasonable, or what constraints it appears to satisfy. State this regardless of how many findings follow; if nothing works, write `What works: None identified` rather than inventing strengths to balance the review.
5. List assumptions the review depends on, including missing context.
6. Challenge those assumptions using the relevant lenses and taxonomy.
7. Deduplicate overlapping findings so the same risk is not reported multiple ways; in paired review, apply the dedup criterion in `references/paired-review.md` against every prior adversarial-review pass on the same target, not only the most recent one.
8. Apply the "so what?" filter and drop findings whose ignored consequence is immaterial for the target's context.
9. Rank findings by severity, impact, likelihood, and confidence.
10. Convert the top risks into concrete adversarial tests, mitigations, or acceptance criteria.
11. Mark each mitigation or acceptance criterion as blocking or non-blocking when the distinction matters.
12. Assign the overall verdict. In paired review, hold the verdict monotonicity rule in `references/paired-review.md`: do not emit a verdict weaker than the strongest prior verdict across all prior adversarial-review passes on the same target.

## Output Format

Return a compact review in this shape. Replace each `A | B | C` placeholder with exactly one of the listed values. `What works` is the brief steel-man of the target. `Suggested fix` is local to one finding; `Mitigations / acceptance criteria` is the cross-cutting or gating set agreed for the target and must separate blocking items from non-blocking watch items when both exist. Per-finding `Test gap` names the unverified behavior; the footer `Adversarial tests` aggregates the concrete tests proposed for top risks and may reference finding numbers.

```text
Verdict: BLOCK | CONCERNS | CLEAN
Target: <artifact and content type>
Intended behavior: <one or two sentences>
Evidence basis: <files, sections, tests, logs, or context reviewed>
What works: <brief steel-man of the current approach, or "None identified">
Assumptions: <explicit assumptions or "None beyond reviewed material">

Findings:
1. <short title>
  Artifact: <file, section, component, workflow step, or test>
  Category: <taxonomy label>
  Severity: CRITICAL | HIGH | MEDIUM | LOW
  Confidence: high | medium | low
  Classification: Confirmed issue | Likely risk | Open question | Accepted tradeoff | Test gap
  Trigger: <concrete scenario or condition>
  Risk: <user, system, data, security, privacy, or operational impact>
  Evidence: <specific observation from the reviewed material>
  Suggested fix: <focused mitigation, test, decision, or acceptance criterion>

Adversarial tests: <behavior-specific tests or checks for top risks, may reference finding numbers>
Mitigations / acceptance criteria: <blocking items before reliance, shipping, or merge; non-blocking watch items or "None">
Residual risk: <remaining caveats after suggested mitigations, or "No material residual risk identified">
```

For `CLEAN`, replace each empty section with `None`; `What works` should still name the strongest evidence supporting the clean verdict when available; `Residual risk` must list caveats or `No material residual risk identified`. For `BLOCK` on a missing, unreadable, or insufficient target, emit a single `Open question` finding describing the blocker and use `Pending - target unavailable` for `What works`, `Adversarial tests`, and `Mitigations / acceptance criteria`.

## Anti-Patterns

- Do not report cosmetic-only issues unless they create ambiguity, user harm, operational risk, or verification risk.
- Do not restate the target or intended behavior as if it were a finding.
- Do not provide exploit steps, weaponizable payloads, or instructions for attacking real systems.
- Do not say only "needs tests"; name the unverified behavior and the failure it should catch.
- Do not force every taxonomy category into the output when it does not apply.
