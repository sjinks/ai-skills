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

## Boundaries

- Review only artifacts and systems the user is authorized to inspect.
- Keep findings actionable, evidence-based, and tied to the target.
- Do not require a fixed number of issues or persona sections. A `CLEAN` verdict is valid when no actionable findings are found after review.
- Do not include exploit instructions, weaponizable payloads, live attack steps, or guidance for abusing real systems.
- Do not exercise the target against live systems, users, or production data; reason from artifacts and non-destructive local inspection only.
- Clearly separate confirmed defects, likely risks, open questions, accepted tradeoffs, and test gaps.

## Required Input Context

Collect or read the narrowest useful context before judging:

- Target artifact and content type: spec, design, implementation, workflow, test plan, or other.
- Intended behavior, success criteria, explicit requirements, and non-goals.
- Actors, users, tenants, permissions, data boundaries, and trust boundaries when relevant.
- Inputs, outputs, dependencies, lifecycle, state transitions, rollback paths, and error paths.
- Existing tests, verification evidence, monitoring, runbooks, or acceptance criteria.

Halt and ask for more context, or report a blocker, when the target is empty, missing, unreadable, or too vague to identify intended behavior. If context is partial but usable, proceed with explicitly listed assumptions and caveats. If the assistant halts to ask for context instead of emitting a verdict, the halt must still include the `Target`, best-effort `Intended behavior`, and the specific missing context; otherwise emit `BLOCK`.

## Optional Review Lenses

Apply the lenses that fit the target. Do not force every lens into the output.

- **Breaker/reliability:** What realistic edge, failure, ordering, timeout, or dependency condition breaks the promise?
- **Maintainer:** What future change, unclear contract, duplicated rule, or hidden coupling makes the artifact easy to misuse or regress?
- **Security/privacy:** What permission, identity, tenancy, data exposure, misuse, or trust-boundary failure is plausible?
- **User/workflow:** Where can a user become stuck, confused, misled, blocked, or lose work?
- **Verification:** What important behavior is unproved, unobservable, or only tested through an unrealistic mock?

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
4. List assumptions the review depends on, including missing context.
5. Challenge those assumptions using the relevant lenses and taxonomy.
6. Deduplicate overlapping findings so the same risk is not reported multiple ways.
7. Rank findings by severity, impact, likelihood, and confidence.
8. Convert the top risks into concrete adversarial tests, mitigations, or acceptance criteria.
9. Assign the overall verdict.

## Output Format

Return a compact review in this shape. Replace each `A | B | C` placeholder with exactly one of the listed values. `Suggested fix` is local to one finding; `Mitigations / acceptance criteria` is the cross-cutting or gating set agreed for the target. Per-finding `Test gap` names the unverified behavior; the footer `Adversarial tests` aggregates the concrete tests proposed for top risks and may reference finding numbers.

```text
Verdict: BLOCK | CONCERNS | CLEAN
Target: <artifact and content type>
Intended behavior: <one or two sentences>
Evidence basis: <files, sections, tests, logs, or context reviewed>
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
Mitigations / acceptance criteria: <cross-cutting changes or explicit decisions needed>
Residual risk: <remaining caveats after suggested mitigations, or "No material residual risk identified">
```

For `CLEAN`, replace each empty section with `None`; `Residual risk` must list caveats or `No material residual risk identified`. For `BLOCK` on a missing, unreadable, or insufficient target, emit a single `Open question` finding describing the blocker and use `Pending - target unavailable` for `Adversarial tests` and `Mitigations / acceptance criteria`.

## Anti-Patterns

- Do not invent findings to satisfy a quota.
- Do not report cosmetic-only issues unless they create ambiguity, user harm, operational risk, or verification risk.
- Do not restate the target or intended behavior as if it were a finding.
- Do not provide exploit steps, weaponizable payloads, or instructions for attacking real systems.
- Do not say only "needs tests"; name the unverified behavior and the failure it should catch.
- Do not force every taxonomy category into the output when it does not apply.
