When to read: when selecting the least-prescriptive profile for an intended task and compatibility floor.

# Capability Profiles

Profiles describe authoring needs, not fixed model rankings. Snapshot, reasoning effort, tools, context, and harness can materially change behavior.

## `fast-general`
For bounded, cost-efficient work. Make outcomes/defaults explicit, keep the path shallow, enumerate independent required criteria when omission is costly, use concise discriminating examples, and keep output schemas simple. Do not compensate for a capability mismatch with an enormous prompt.

## `strong-general`
Prefer outcome-first instructions, hard constraints, evidence, and completion criteria. Leave tool choice and execution order flexible. Avoid procedural scaffolding that merely restates competent agent behavior.

## `deep-reasoning`
Define the decision/outcome rather than hidden reasoning. Preserve uncertainty and conflicting evidence. Distinguish reasoning from empirical verification. Avoid fixed analysis sequences unless methodology itself is required. Do not request chain-of-thought.

## `coding-agent`
State repository outcome, scope, behavior-preservation constraints, conventions, verification, and definition of done. Keep tool mechanics in the runtime adapter. Avoid prescribing search/edit order unless correctness requires it.

## `specialized-classifier`
Define labels operationally, make boundaries explicit, distinguish positive evidence from absence of evidence, define abstain/unknown behavior, and prefer a few discriminating examples.

## Selection
Choose from task and demonstrated behavior, not branding. Start with the least prescriptive plausible profile, run evals, add scaffolding only for reproduced failures, and route upward if prompt complexity begins compensating for capability.
