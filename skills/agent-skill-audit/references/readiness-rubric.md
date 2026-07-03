Read this reference before assigning readiness ratings for an agent, skill, or instruction package audit.

# Readiness Rubric

Apply each area to the actual artifact type and audit mode.

## 1. Discovery and Delegation

### Agent Skill

Check:

- valid, specific `name`;
- description states recognizable triggers and a meaningful exclusion;
- activation scope does not materially overlap neighboring skills;
- critical execution behavior is not hidden only in metadata;
- user-invocable behavior and arguments are coherent when those fields exist.

### Custom Agent or Subagent

Check:

- delegation description identifies the problem class and workflow stage;
- the result returned to the parent or user is explicit;
- exclusions distinguish the agent from neighboring roles;
- read, edit, execute, browse, delegate, and state-change authority are clear;
- the role is narrow enough to route reliably.

## 2. Instruction Architecture

Check:

- one primary purpose;
- correct division among core instructions, references, adapters, scripts, templates, and project-wide guidance;
- normal path remains in the main artifact;
- references have explicit loading conditions;
- important rules are not hidden behind deep reference chains;
- mutually exclusive paths are separated;
- each load-bearing rule has one authoritative source;
- examples do not silently define required behavior;
- the package is not a monolithic prompt when progressive disclosure would reduce instruction competition.

## 3. Operational Completeness

Check:

- inputs and deliverables;
- analysis versus implementation distinction;
- side-effect and approval policy;
- ask-versus-assume policy;
- closed decision branches and precedence;
- capability and tool failure behavior;
- validation semantics;
- completion and stopping conditions;
- final output contract;
- for agents, the parent-agent return contract;
- blocked and partially available input behavior.

Do not require every rare edge case to be in the core. Require every reachable case to have a defined outcome somewhere reachable.

## 4. Model and Runtime Portability

Check:

- explicitness and shallow normal path for the compatibility-floor models;
- freedom from unnecessary process scaffolding for stronger models;
- provider-neutral capability language in portable instructions;
- runtime-specific tool names and metadata isolated in adapters;
- optional tool and delegation fallbacks;
- no reliance on self-identification of the model;
- no model behavior treated as a security boundary;
- output grammar proportionate to the underlying task;
- permissions enforced by runtime policy where possible.

Use `model-portability.md` for model-specific checks.

## 5. Maintainability and Evaluability

Check:

- stable, distinctive output markers where the repository requires them;
- activation and execution can be evaluated separately;
- exact serialization is externally validated when machine parsing matters;
- rules and examples agree;
- duplicated policy is unlikely to drift;
- changes do not require updating many independent copies;
- evals cover positive, negative, close-domain, blocked, package, and model-sensitive cases;
- eval regexes and `not_contains` assertions match canonical labels;
- static audit limitations are stated and execution evals are planned.

## Material Finding Severity

Assign severity according to the most serious credible consequence of leaving the finding unresolved.

Use uppercase severity values exactly as follows:

### `CRITICAL`

Use when the finding can cause:

* unsafe or unauthorized destructive action;
* exposure of credentials, private data, or protected reasoning;
* systematic prompt-injection takeover of the audit or execution process;
* an instruction package that cannot safely perform its stated purpose;
* a fundamental authority conflict likely to produce severe external impact.

A `CRITICAL` finding normally requires `Verdict: Major redesign`.

### `HIGH`

Use when the finding can cause:

* the wrong primary deliverable;
* contradictory mandatory behavior on a normal execution path;
* material scope expansion or unauthorized state changes;
* fabricated validation or unsupported completion claims;
* unusable activation, delegation, stopping, or return behavior;
* failure across one or more explicitly targeted model or runtime profiles.

A `HIGH` finding normally prevents `Verdict: Ready`.

### `MEDIUM`

Use when the finding can cause:

* inconsistent execution across realistic inputs;
* material ambiguity or guessing;
* missed failure handling;
* excessive instruction burden for a target model;
* unnecessary restriction of stronger models;
* cross-file drift or an eval contract that is unreliable but still usable.

A `MEDIUM` finding requires correction but does not by itself imply that the artifact is fundamentally unusable.

### `LOW`

Use when the finding is a confirmed, localized maintainability or clarity problem with limited behavioral impact, such as:

* avoidable duplication that has not yet diverged;
* a minor reference-routing weakness;
* a small eval-coverage gap;
* wording that is awkward but unlikely to change the normal result.

Do not emit a `LOW` finding for optional polish or personal style preference.

## Severity Selection Rules

* Evaluate consequence, not the amount of text involved.
* Use the highest severity supported by concrete evidence.
* Do not raise severity merely because a finding affects several files when those files represent the same underlying defect.
* Do not lower severity because a stronger model may infer the intended behavior.
* When the consequence depends on an unverified assumption, lower confidence in the prose explanation rather than inflating severity.
* Ratings and finding severities are related but not mechanically identical. Determine area ratings from the combined material risk, not by averaging or counting findings.

## Rating Calibration

Use the highest severity of material risk, not issue count.

- `5`: complete and well structured; no material correction;
- `4`: minor localized weakness; behavior remains reliable;
- `3`: one or more material weaknesses can cause inconsistent behavior;
- `2`: broad structural weakness likely to cause repeated failures;
- `1`: purpose, authority, safety, or architecture is fundamentally broken.

Optional polish must not lower a rating below 5.
