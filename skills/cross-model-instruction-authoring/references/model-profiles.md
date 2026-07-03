# Model Profiles

Use these profiles as authoring heuristics, not as guarantees. Runtime system instructions, effort settings, tools, context usage, and model snapshots can change behavior. Resolve uncertainty with evaluations.

## Compatibility Strategy

Use two simultaneous tests:

1. **Compatibility floor:** Can GPT-5.4 mini and Claude Haiku 4.5 execute the normal path without guessing essential requirements?
2. **Capability ceiling:** Do the same instructions leave GPT-5.5, Claude Sonnet 5, Claude Opus 4.8, and Claude Fable 5 enough freedom to use better strategies?

GPT-5.4 is the middle reference point.

## GPT-5.4 mini

Treat as a capable cost-efficient model for well-bounded coding, tool use, and subagent tasks.

Authoring implications:

- state the deliverable explicitly;
- keep the normal path short and linear;
- define catch-all behavior;
- avoid several independent goals in one invocation;
- reduce nested exceptions and overlapping priorities;
- provide exact validation expectations;
- provide one concise example for subtle classification or output boundaries;
- route genuinely broad architectural work to a stronger model rather than compensating with a very long prompt.

Failure patterns to test:

- stopping after analysis when implementation was requested;
- omitting a secondary requirement;
- following one branch while missing a sibling branch;
- producing approximately correct but non-conforming output;
- attempting validation without interpreting failure output.

## GPT-5.4

Treat as the balanced general target.

Authoring implications:

- define outcomes, invariants, evidence, and completion;
- provide an adaptable default workflow;
- allow the model to choose tools and ordering;
- make side-effect boundaries explicit;
- avoid provider-specific tool syntax in portable artifacts;
- require verification where current state matters.

Failure patterns to test:

- broadening repository scope;
- unnecessary exploration;
- treating a proposed plan as completion;
- assuming unavailable capabilities.

## GPT-5.5

Treat as a strong outcome-oriented model.

Authoring implications:

- prefer shorter, outcome-first instructions;
- remove legacy process scaffolding unless it protects a real invariant;
- specify what success looks like, constraints, evidence, and final output;
- avoid fixed reasoning, planning, and tool sequences;
- keep validation and scope boundaries explicit;
- configure reasoning effort in the runtime rather than adding generic "think deeply" language.

Failure patterns to test:

- mechanically following an obsolete procedure instead of a better path;
- performing extra work because scope is not bounded;
- compressed final reporting that omits required evidence.

## Claude Haiku 4.5

Treat as the smallest Claude target and prefer straightforward, bounded tasks.

Authoring implications:

- use concrete steps when order matters;
- define required parameters and prohibit guessing material values;
- define the default when a tool or input is unavailable;
- avoid deeply nested decision rules;
- keep tools simple and descriptions precise;
- split broad analysis, implementation, and review into separate stages when necessary;
- use exact output schemas only when the schema is simple or externally validated.

Failure patterns to test:

- inferring a missing tool argument;
- under-exploring related files;
- treating an attempted command as successful validation;
- missing a global rule that was demonstrated only for one example.

## Claude Sonnet 5

Treat as the default balanced Claude target.

Authoring implications:

- state broad scope literally; do not rely on implicit generalization;
- define tool-use triggers when tools are necessary;
- avoid fixed progress-update cadence;
- use positive examples for tone and concision where style matters;
- keep reasoning effort in runtime configuration;
- at lower effort, make multi-step requirements especially explicit.

Failure patterns to test:

- applying a rule only to the first item;
- under-thinking at low or medium effort;
- omitting tool use when thinking is disabled;
- literal compliance with an accidentally narrow instruction.

## Claude Opus 4.8

Treat as a strong complex-work model that may favor reasoning over tool calls.

Authoring implications:

- explicitly require tools when claims depend on current evidence;
- distinguish reasoning from verification;
- state when delegation is useful and when direct work is better;
- state broad scope literally;
- remove forced update cadence;
- define output length and tone when product behavior depends on them.

Failure patterns to test:

- reasoning from memory instead of checking current state;
- spawning too few subagents for clearly independent investigations;
- over-literal application of a locally worded rule;
- producing a persuasive conclusion with insufficient tool evidence.

## Claude Fable 5

Treat as the highest-autonomy, long-horizon target.

Authoring implications:

- use a mission, hard boundaries, completion criteria, and evidence-based checkpoints;
- do not micromanage normal execution;
- define exactly when to pause for the user;
- prohibit unrequested refactoring, backup branches, defensive work, and scope expansion;
- ground progress and completion claims in tool results;
- allow delegation of independent workstreams when available;
- never request reproduction of private reasoning;
- for long work, define memory or verification mechanisms in the runtime, not as mandatory overhead for every small task.

Failure patterns to test:

- taking sensible-looking but unrequested actions;
- overplanning an ambiguous but actionable task;
- reporting progress not supported by tool results;
- pausing for permission despite having authority to proceed;
- following old procedural scaffolding that reduces performance.

## Cross-Model Wording Patterns

Prefer:

> Deliver the requested outcome and verify it against the acceptance criteria.

> Use the following workflow as a default. Adapt it when an equivalent approach is safer or more efficient, but do not omit required outcomes.

> Use available tools when a conclusion depends on current repository state, external state, generated output, or runtime behavior.

> Pause only for a destructive or irreversible action, a real scope change, or information only the user can supply.

Avoid:

> Think step by step and show all reasoning.

> Always call Tool X, then Tool Y, then Tool Z.

> After every three calls, report progress.

> Ask before every edit.

> Use your judgment.

> Make the smallest possible diff.
