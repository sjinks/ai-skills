Read this reference when assessing static compatibility across supported target models and runtime portability risks.

# Target-Model Portability

These profiles are static-review heuristics. Runtime instructions, effort settings, tools, consumed context, and model snapshots can change behavior.

Evaluate both:

1. **compatibility floor**: can the smaller supported models execute the normal path without guessing essential rules?
2. **capability ceiling**: do the same instructions preserve useful freedom for stronger models?

Use these verdicts per model:

- `Suitable`
- `Suitable with limitations`
- `Unsuitable`
- `Not assessed`

## GPT-5.4 mini

Check for:

- explicit deliverable and completion state;
- short, shallow normal path;
- defaults and catch-all branches;
- limited unrelated workstreams;
- concrete validation requirements;
- simple output grammar;
- no need to infer material tool parameters.

Flag tasks whose intrinsic breadth should be routed to a stronger model rather than compensated for with a much longer prompt.

## GPT-5.4

Check for:

- clear outcomes, invariants, evidence, and completion;
- adaptable workflow;
- explicit side-effect boundaries;
- freedom to choose efficient tools and ordering;
- no assumptions about unavailable runtime capabilities.

## GPT-5.5

Check for:

- outcome-first instructions;
- no legacy process scaffolding without a real correctness purpose;
- no fixed planning, reasoning, tool-call, or progress-update sequence;
- explicit scope and evidence requirements;
- concise but complete final reporting.

## Claude Haiku 4.5

Check for:

- concrete steps when order matters;
- explicit material parameters;
- a defined unavailable-tool or missing-input default;
- shallow decision rules;
- no expectation that broad requirements will be inferred from one example;
- output format simple enough to reproduce reliably.

## Claude Sonnet 5

Check for:

- literal, explicit scope for rules that apply to every item or file;
- explicit tool-use triggers when evidence is required;
- no fixed progress cadence;
- multi-step requirements sufficiently explicit at lower effort settings;
- examples that do not narrow a broader written rule accidentally.

## Claude Opus 4.8

Check for:

- explicit distinction between reasoning and verification;
- tool triggers for claims about current state;
- useful delegation guidance for genuinely independent workstreams;
- broad scope stated literally;
- no assumption that tool availability alone guarantees tool use.

## Claude Fable 5

Check for:

- mission, boundaries, completion, and evidence-based checkpoints;
- explicit pause conditions;
- prohibition of unrequested refactoring, defensive work, and scope expansion;
- progress and completion claims grounded in tool results;
- no micromanagement of ordinary execution;
- optional delegation policy rather than a fixed subagent count.

## Cross-Provider Checks

For every model, check:

- no hard-coded provider tool names in the portable core;
- no provider-specific variables or invocation controls without an adapter;
- skill remains functional without delegation unless delegation is mandatory and guaranteed;
- missing optional capabilities produce an explicit fallback;
- static compatibility claims are not presented as execution proof.
