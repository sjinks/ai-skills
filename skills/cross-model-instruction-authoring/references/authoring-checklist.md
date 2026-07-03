# Authoring Checklist

Use this checklist after drafting. Correct material failures before delivering the artifact.

## A. Purpose and Routing

- [ ] The artifact has one primary purpose.
- [ ] The artifact type is correct: skill, custom agent, or persistent project instruction.
- [ ] A skill description says when to use it and when not to use it.
- [ ] An agent description says when to delegate, what it returns, and what it excludes.
- [ ] Trigger or delegation wording uses recognizable user intent and domain terms.
- [ ] The artifact does not depend on self-identification of the model.

## B. Outcomes and Boundaries

- [ ] The deliverable is explicit.
- [ ] Analysis-only and implementation tasks are distinguished.
- [ ] Required outcomes are separate from default strategy.
- [ ] Scope limits are explicit.
- [ ] Permitted side effects are explicit.
- [ ] Destructive and irreversible actions have an approval rule.
- [ ] "Smallest complete change" is defined where implementation is involved.
- [ ] The artifact prohibits fabricated validation and progress claims.

## C. Decision Quality

- [ ] Terms with special meaning are defined.
- [ ] Quantifiers and scope words are explicit where material.
- [ ] Every reachable decision branch has an action or default.
- [ ] Overlapping rules have a precedence rule.
- [ ] The ask-versus-assume policy is explicit.
- [ ] Exceptional paths do not obscure the normal path.
- [ ] There are no contradictory output or stopping rules.

## D. Tool and Runtime Portability

- [ ] The portable core describes capabilities rather than provider tool names.
- [ ] Required tools or environment dependencies are declared.
- [ ] Optional capability absence has a fallback.
- [ ] Tool use is tied to evidence requirements.
- [ ] Exact tool names, permissions, hooks, and model settings are isolated in runtime adapters.
- [ ] Runtime policy, not prompt text alone, enforces dangerous-action boundaries.
- [ ] Delegation is optional unless guaranteed by the runtime.

## E. Small-Model Executability

- [ ] The normal path is short and shallow.
- [ ] Essential behavior is not implicit.
- [ ] Material tool parameters are not guessed.
- [ ] The artifact does not combine unrelated workstreams.
- [ ] The output grammar is proportionate to the task.
- [ ] Subtle boundaries have a concise example.
- [ ] Long background material is moved to references.
- [ ] Deterministic checks are scripts or validators where appropriate.

## F. Frontier-Model Freedom

- [ ] The workflow is marked as adaptable unless sequence is mandatory.
- [ ] The artifact does not force a plan for trivial work.
- [ ] The artifact does not force progress updates at a fixed cadence.
- [ ] The artifact does not require permission for safe reversible actions already authorized by the request.
- [ ] It does not prescribe internal reasoning.
- [ ] It does not duplicate capable runtime defaults.
- [ ] It prohibits unrequested cleanup and speculative abstraction.

## G. Evidence, Validation, and Completion

- [ ] Claims dependent on current state require tools or supplied evidence.
- [ ] Passed, failed, blocked, and not-run checks are distinguished.
- [ ] An attempted command is not treated as a passing check.
- [ ] Completion criteria are observable.
- [ ] The final output or parent-agent return contract is explicit.
- [ ] Assumptions and unresolved risks are reported.
- [ ] Long-run progress claims are grounded in tool results.

## H. Skill Packaging

Apply only to Agent Skills.

- [ ] `name` is lowercase, hyphenated, and matches the directory.
- [ ] `description` is concise and front-loads the primary trigger.
- [ ] The portable core uses standard frontmatter fields.
- [ ] Execution rules are in the body, not only in metadata.
- [ ] References and scripts are linked with clear conditions for use.
- [ ] The main file contains the normal path.
- [ ] Rare cases and large examples are progressively disclosed.

## I. Agent Prompt Quality

Apply only to custom agents or subagents.

- [ ] The role is narrow and task ownership is clear.
- [ ] Read, edit, execute, browse, and delegation authority are defined.
- [ ] Evidence standards are defined.
- [ ] Autonomy and escalation boundaries are defined.
- [ ] Stopping conditions are defined.
- [ ] The parent-agent or user return contract is defined.
- [ ] Long reusable procedures are delegated to skills rather than duplicated.

## J. Cross-Model Review

- [ ] GPT-5.4 mini can execute the normal path without guessing.
- [ ] GPT-5.4 can choose an efficient approach.
- [ ] GPT-5.5 is not burdened by process-heavy legacy scaffolding.
- [ ] Claude Haiku 4.5 has explicit defaults and parameters.
- [ ] Claude Sonnet 5 receives explicit broad scope.
- [ ] Claude Opus 4.8 has tool and evidence triggers where needed.
- [ ] Claude Fable 5 has boundaries and grounded long-run progress rules.
- [ ] A real evaluation plan covers the actual runtime and model settings.

## Severity Guidance

Treat a failure as **blocking** when it can cause:

- unsafe or unauthorized actions;
- the wrong deliverable;
- silent scope expansion;
- contradictory behavior;
- fabricated validation;
- unusable activation or delegation;
- failure on the compatibility-floor models.

Treat a failure as **material** when it can cause:

- inconsistent execution;
- unnecessary clarification;
- excessive tool use;
- avoidable model-specific degradation;
- output that cannot be consumed reliably.

Treat purely stylistic preferences as optional polish.
