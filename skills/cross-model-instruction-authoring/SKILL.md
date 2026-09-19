---
name: cross-model-instruction-authoring
description: >-
  Use when creating, revising, or adapting Agent Skills, custom agent
  prompts, subagent instructions, or instruction packages that should work
  across multiple models or runtimes, especially smaller/faster and frontier
  GPT/Claude models. Produces a model-neutral core, separates runtime-specific
  adapters, and checks both small-model executability and frontier-model
  overconstraint. Do not use for a review-only audit when no authored or
  revised artifact is requested.
argument-hint: "Instruction artifact(s) to create/revise, target runtimes, target model set (or subset), hard constraints/side-effect policy, and required output/return contract."
user-invocable: true
---

# Cross-Model Instruction Authoring

> **A model-specific adaptation MUST NOT be added merely because the target model is known.**

Use four layers: **portable core**, **capability profile**, **behavioral patches**, and **runtime adapter**.

## USE FOR:

- authoring or revising a portable skill, agent prompt, or instruction package
- adapting one artifact across multiple models or runtimes
- replacing model-family folklore with evidence-backed behavioral patches

## DO NOT USE FOR:

- review-only instruction audits with no requested rewrite
- intentionally single-model prompt tuning with no portability goal
- generic model-selection advice with no instruction artifact

**UTILITY SKILL.** Produces or revises an instruction artifact and its
portability rationale. **FOR SINGLE OPERATIONS:** use a review skill for a
read-only audit and keep runtime-only configuration out of the portable core.

## Evidence Classes

Every non-universal adaptation needs a basis: `TASK_REQUIREMENT`, `USER_REQUIREMENT`, `PROVIDER_GUIDANCE`, `HARNESS_REQUIREMENT`, `EVAL_EVIDENCE`, or `OBSERVED_BEHAVIOR`.

Prefer `EVAL_EVIDENCE` for model-specific behavioral claims. Treat `OBSERVED_BEHAVIOR` as provisional. Hearsay such as "model X likes Y" is not evidence.

## Workflow

1. **Extract the behavioral contract.** Identify outcome, authoritative inputs, hard constraints, permissions, output contract, blocked behavior, verification, and definition of done. Separate what must be true from how an agent might achieve it.
2. **Build the portable core.** Prefer outcome-first instructions, material defaults, concise decision rules, evidence requirements, permission boundaries, and observable completion criteria. Avoid chain-of-thought requests, unnecessary provider vocabulary, fixed tool sequences, duplicated tool schemas, and mandatory narration without a runtime reason.
3. **Choose the compatibility floor.** Read `references/capability-profiles.md`. Select the weakest intended capability profile. Add only enough scaffolding for reliable execution; route upward if prompt complexity is compensating for capability.
4. **Protect the capability ceiling.** Do not unnecessarily force stronger models into fixed reasoning, predetermined search/edit order, unnecessary confirmation, redundant exploration, or work beyond done.
5. **Identify an actual failure risk.** Examples: premature local conclusion, redundant exploration, repeated equivalent retries, criterion omission, premature stopping, reasoning substituted for verification, needless serialization.
6. **Apply the smallest patch.** Read `references/behavioral-patches.md`. Record patch, symptom, evidence class, scope, confidence, and optionally a retest/removal condition.
7. **Separate runtime adapters.** Exact model IDs, tool schemas, output envelopes, progress protocol, context injection, permissions, and orchestration belong here. A harness requirement is not automatically model behavior.
8. **Validate.** Use `references/authoring-checklist.md` and the separate eval suite under `evals/cross-model-instruction-authoring/`.

## Acceptance

**Compatibility floor:** the weakest intended profile can identify the deliverable, follow the normal path without guessing material requirements, resolve branches, satisfy output/blocked contracts, and distinguish attempted verification from successful verification.

**Capability ceiling:** stronger targets retain strategy freedom and are not forced into redundant context gathering, unnecessary narration, serialized independent work, or needless confirmation.

**Adaptation discipline:** every non-universal rule has an evidence class; model name alone caused no patch; provider guidance is not a capability guarantee; harness quirks are not mislabeled as model quirks.

## Output Modes

- **Author:** complete artifact.
- **Adapt:** portable core, profile, justified patches, runtime adapter, complete artifact.
- **Review-and-Rewrite:** material portability issues, folklore, changes, complete artifact.
- **Profile Recommendation:** profile, justified patches, evidence still needed.

## Output

Unless the caller supplies a required schema, **Author**, **Adapt**, and
**Review-and-Rewrite** use these labels exactly once and in this order:

`Finished artifact:` — the complete authored or revised artifact.

`Material assumptions:` — assumptions, selected capability profile, evidence
classes, and remaining uncertainty; write `None.` when there are none.

`Runtime adapter:` — runtime-only mechanics, or `None.`.

`Compatibility note:` — floor/ceiling limitations, applied behavioral patches,
and required evaluation; write `None known; evaluation is still required.`
when appropriate.

Each label starts at column zero and has a nonempty body. Do not put content
before `Finished artifact:` or repeat a label. `Compatibility note:` is one
nonempty line and ends the response.

**Profile Recommendation** uses `Profile recommendation:`, `Justified
behavioral patches:`, and `Evidence still needed:` instead. `Profile
recommendation:` contains exactly one capability-profile identifier;
`Justified behavioral patches:` contains bullets or `- None.`; and `Evidence
still needed:` contains one or more bullets. Do not present a model-specific
patch as established without an evidence class.

The Profile Recommendation labels start at column zero, occur exactly once in
that order, and begin the response; the final evidence bullet ends it.

## Stop

Stop when the behavioral contract is complete, compatibility floor passes, capability ceiling remains open, every non-universal adaptation is justified, runtime mechanics are separated, and completion/verification are unambiguous.

## References

- Read [capability profiles](references/capability-profiles.md) to select the
  least-prescriptive profile from task and observed behavior.
- Read [behavioral patches](references/behavioral-patches.md) after identifying
  a concrete failure risk and before recording a narrow correction.
- Read [model profiles](references/model-profiles.md) only for conservative,
  non-binding target-family defaults and candidate patches.
- Read the [authoring checklist](references/authoring-checklist.md) before
  finalizing a complex or production-bound artifact.
- Read the [evidence policy](references/evidence.md) when classifying an
  adaptation basis or a model-specific claim.
