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

Assess each selected target independently. For a target with a profile in this package, use its checks below. For an unprofiled target, apply Cross-Provider Checks without inferring model-specific behavior, emit `Not assessed` in its compatibility row, and record the missing profile under `Limitations` in `## Audit Scope`. Assess the readable artifact normally; this missing profile alone does not require `Blocked`. If all other readiness conditions pass, use `Ready with limitations`; otherwise retain the core's applicable revision or blocking verdict. Keep the default roster order in reports, but do not treat it as a benchmark ranking or infer compatibility from another model's result.

The Claude roster is a selected audit set, not a catalog of all released models. See Anthropic's [models overview](https://platform.claude.com/docs/en/models/overview) for the current lineup.

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

## GPT-6.2 Sol and GPT-6.2 Astra

Assess each model separately using the shared checks below. Use [OpenAI's model-selection guide](https://developers.openai.com/api/docs/guides/model-selection) to calibrate workload expectations: Sol for general coding and agent workflows, Astra for demanding engineering and analysis.

- Check for clear scope, explicit evidence requirements, and observable completion criteria.
- When a runtime is supplied, check its configured reasoning effort and available tools against the task. Record unknown settings as limitations when they affect the assessment. Do not assume API defaults or tool availability apply to the supplied runtime.

The following older GPT profiles apply only when explicitly requested.

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

## Claude Opus 5.5

Check for clear completion criteria in unattended work; progress reports distinguished from completed tasks; scope and consequential-action boundaries; and effort calibration for the supplied workload. When a harness is supplied, check pending-work handling, bounded continuations and response-block handling rather than treating every text-only turn as completion.

Use [Anthropic's Opus 5.5 guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5). Keep runtime mechanics out of portable instructions.

## Claude Fable 5.1

Check for completion and scope boundaries; explicit search triggers at low effort; compaction preserving constraints and decisions; targeted edits; and clear deliverable formatting. Permit batching of independent calls when supported, without requiring parallel execution. With a harness, check append-only history and whether progress updates reach the user.

Use [Anthropic's Fable 5.1 guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1).

## Claude Fable 5.2

Use [Anthropic's Fable 5.2 prompting guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2) to check for observable completion criteria, explicit approval boundaries, and delegation limited to work that benefits from separate context. For long-running tasks, check that progress updates do not substitute for completion. When a runtime is supplied, assess its effort settings against the workload rather than assuming settings from an earlier profile apply.

## Claude Mythos 5.1

Apply the Fable 5.1 checks above; [Anthropic's shared guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1) covers both models. Assess Mythos separately rather than copying Fable's verdict. [Mythos access requires organizational verification](https://platform.claude.com/docs/en/models/mythos-5-1/overview). For a supplied runtime, record unverified or unavailable access as a limitation; do not claim runtime readiness from a static profile or seek access during this audit.

## Cross-Provider Checks

For every model, check:

- no hard-coded provider tool names in the portable core;
- no provider-specific variables or invocation controls without an adapter;
- skill remains functional without delegation unless delegation is mandatory and guaranteed;
- missing optional capabilities produce an explicit fallback;
- static compatibility claims are not presented as execution proof.
