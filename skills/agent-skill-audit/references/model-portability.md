Read this reference when assessing static compatibility across supported target models and runtime portability risks.

# Target-Model Portability

These profiles are static-review heuristics. Runtime instructions, effort settings, tools, consumed context, and model snapshots can change behavior.

The default compatibility floor is GPT-6 Luna and Claude Haiku 5.5. Treat these as the weaker-model targets for instruction design, not as a measured cross-provider capability ranking. If the user supplies target models, assess that list instead.

Evaluate both:

1. **compatibility floor**: can the smaller supported models execute the normal path without guessing essential rules?
2. **capability ceiling**: do the same instructions preserve useful freedom for stronger models?

Use these verdicts per model:

- `Suitable`
- `Suitable with limitations`
- `Unsuitable`
- `Not assessed`

Assess each listed target independently with the checks below. Keep the default roster order in reports, but do not treat it as a benchmark ranking or infer compatibility from another model's result.

Current Anthropic additions were checked against the [models overview](https://platform.claude.com/docs/en/models/overview) on 2026-10-09; earlier supported profiles remain in the roster.

Do not infer one total capability order across Claude Opus and Fable profiles. Opus targets complex reasoning and synthesis; Fable targets long-horizon autonomy.

## GPT-6 Luna

Check for:

- explicit deliverable and completion state;
- short, shallow normal path;
- defaults and catch-all branches;
- limited unrelated workstreams;
- concrete validation requirements;
- simple output grammar;
- no need to infer material tool parameters.

Flag tasks whose intrinsic breadth should be routed to a stronger model rather than compensated for with a much longer prompt.

## GPT-6 Sol

Check for:

- clear outcomes, invariants, evidence, and completion;
- adaptable workflow;
- explicit side-effect boundaries;
- freedom to choose efficient tools and ordering;
- no assumptions about unavailable runtime capabilities.

## GPT-6.1 Sol

Check for:

- outcome-first instructions;
- no legacy process scaffolding without a real correctness purpose;
- no fixed planning, reasoning, tool-call, or progress-update sequence;
- explicit scope and evidence requirements;
- concise but complete final reporting.
- literal scope across files, components, or workstreams;
- explicit invariants and completion criteria for broad synthesis;
- optional delegation guidance only for independent workstreams;
- preservation of evidence and unresolved disagreements;
- no fixed planning, tool, or progress-update cadence.

## GPT-6 Astra

Check for:

- a concise mission, hard boundaries, and observable completion state;
- freedom to choose and revise an efficient execution strategy;
- explicit pause conditions for consequential ambiguity or side effects;
- progress and completion claims grounded in tool results;
- protection against unrequested scope expansion without micromanaging normal work.

## Claude Haiku 5.5

Check for:

- concrete ordered steps, explicit parameters, shallow branches and missing-input/tool defaults;
- explicit completion boundaries that prevent early hand-back without expanding scope;
- checks that exercise runnable changes before reporting success, or an honest reason no check ran;
- current-date context and retrieval triggers for changeable facts when search is available;
- simple output grammar and broad rules stated explicitly rather than inferred from one example;
- assessment tied to the intended effort/thinking settings, with unknown settings recorded as a limitation.

[Anthropic's prompting guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-haiku-5-5) reports effort-dependent search, completion and verification risks. Treat these as audit prompts, not guaranteed failures. For a supplied API integration or harness, read [runtime checks](haiku-5-5-runtime.md); do not require an adapter for a portable instruction-only artifact.

## Claude Sonnet 5

Check for:

- literal, explicit scope for rules that apply to every item or file;
- explicit tool-use triggers when evidence is required;
- no fixed progress cadence;
- multi-step requirements sufficiently explicit at lower effort settings;
- examples that do not narrow a broader written rule accidentally.

## Claude Sonnet 5.5

Check for effort-aware completion and verification rules; boundaries against unrequested additions or extra review cycles; retrieval triggers for mutable facts; and JSON reasoning requirements that fit the supplied thinking configuration. Preserve freedom to choose an efficient workflow.

Use [Anthropic's Sonnet 5.5 guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5). Do not transfer effort settings or observed behavior from Sonnet 5 without evidence.

## Claude Opus 4.8

Check for:

- explicit distinction between reasoning and verification;
- tool triggers for claims about current state;
- useful delegation guidance for genuinely independent workstreams;
- broad scope stated literally;
- no assumption that tool availability alone guarantees tool use.

## Claude Opus 5

Check for:

- outcome-first instructions for complex analysis and synthesis;
- explicit tool and evidence triggers for claims about current state;
- hard scope, safety, and stopping boundaries without procedural micromanagement;
- optional delegation guidance for genuinely independent investigations;
- preservation of uncertainty, disagreement, and verification status in final conclusions.

## Claude Opus 5.5

Check for clear completion criteria in unattended work; progress reports distinguished from completed tasks; scope and consequential-action boundaries; and effort calibration that does not inherit Opus 5 assumptions. When a harness is supplied, check pending-work handling, bounded continuations and response-block handling rather than treating every text-only turn as completion.

Use [Anthropic's Opus 5.5 guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5). Keep runtime mechanics out of portable instructions.

## Claude Fable 5

Check for:

- mission, boundaries, completion, and evidence-based checkpoints;
- explicit pause conditions;
- prohibition of unrequested refactoring, defensive work, and scope expansion;
- progress and completion claims grounded in tool results;
- no micromanagement of ordinary execution;
- optional delegation policy rather than a fixed subagent count.

## Claude Fable 5.1

Check for completion and scope boundaries; explicit search triggers at low effort; compaction preserving constraints and decisions; targeted edits; and clear deliverable formatting. Permit batching of independent calls when supported, without requiring parallel execution. With a harness, check append-only history and whether progress updates reach the user.

Use [Anthropic's Fable 5.1 guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1); calibrate effort independently of Fable 5.

## Claude Mythos 5.1

Apply the Fable 5.1 checks above; [Anthropic's shared guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1) covers both models. Assess Mythos separately rather than copying Fable's verdict. [Mythos access requires organizational verification](https://platform.claude.com/docs/en/models/mythos-5-1/overview). For a supplied runtime, record unverified or unavailable access as a limitation; do not claim runtime readiness from a static profile or seek access during this audit.

## Cross-Provider Checks

For every model, check:

- no hard-coded provider tool names in the portable core;
- no provider-specific variables or invocation controls without an adapter;
- skill remains functional without delegation unless delegation is mandatory and guaranteed;
- missing optional capabilities produce an explicit fallback;
- static compatibility claims are not presented as execution proof.
