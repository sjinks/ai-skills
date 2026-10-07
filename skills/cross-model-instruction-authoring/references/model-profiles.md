When to read: when comparing a target family with conservative, non-binding profile candidates.

# Model Profiles

Conservative authoring defaults, not capability guarantees. Prefer current provider guidance and concrete behavioral evidence.

**Do not add a behavioral patch simply because a model appears below.**

These are profile candidates, not a selection rule. The task- and
evidence-derived selection rule in `capability-profiles.md` takes precedence;
a target name may narrow the compatibility floor but cannot itself justify a
behavioral patch.

| Target | Default profile | Default model-specific patches |
|---|---|---|
| GPT-6 Luna | `fast-general` | none |
| GPT-6 Sol | `strong-general` | none |
| GPT-6.1 Sol | `strong-general` | none |
| GPT-6 Astra | `deep-reasoning` | none |
| GPT-5.3 Codex / Codex Spark | `coding-agent` | none |
| Claude Haiku-class | `fast-general` | none |
| Claude Sonnet-class | `strong-general` | none |
| Claude Opus-class | `deep-reasoning` | none |
| Gemini general-purpose | `strong-general` | none |
| Grok general-purpose | choose by task requirements | none |
| Grok code-specialized | `coding-agent` when appropriate | none |

Candidate, not default, patches:
- Haiku-class: `context-before-conclusion` only when concrete evidence shows a recurring local-only conclusion problem.
- Sonnet-class: `bounded-exploration` only when guidance, harness constraints, or observed behavior demonstrate redundant exploration.
- Opus-class: `bounded-exploration` or `verification-over-reasoning` only with evidence.
- Gemini/Grok: remain provider-neutral until a reproducible failure justifies a patch.

For unknown/new models: author the portable core, choose a profile from task/runtime constraints, and apply no model-specific patch without concrete evidence.

Exact availability and fallback order belong to runtime routing.
