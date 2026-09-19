# cross-model-instruction-authoring

> Use when: creating, revising, or adapting Agent Skills, custom agent prompts, subagent instructions, or instruction packages that should work across multiple models or runtimes, especially smaller/faster and frontier GPT/Claude models.

This skill authors instruction artifacts from a portable core, a
least-prescriptive capability profile, narrow evidence-backed behavioral
patches, and separate runtime adapters. It does not turn model-family folklore
or harness quirks into model behavior.

It helps an assistant:

- extract a behavioral contract before selecting an implementation strategy
- protect the compatibility floor without compensating for a capability mismatch with a larger prompt
- preserve capability-ceiling strategy freedom
- classify adaptations by evidence and remove stale patches
- separate runtime mechanics from portable task behavior

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- [`references/capability-profiles.md`](references/capability-profiles.md) — task-derived capability profiles and selection rule.
- [`references/behavioral-patches.md`](references/behavioral-patches.md) — narrow failure-mode corrections and their lifecycle.
- [`references/model-profiles.md`](references/model-profiles.md) — conservative target-family defaults, never a source of automatic patches.
- [`references/evidence.md`](references/evidence.md) — adaptation evidence classes and anti-folklore policy.
- [`references/authoring-checklist.md`](references/authoring-checklist.md) — finalization and evaluation checks.
- [Canonical Waza suite](https://github.com/sjinks/ai-skills/tree/master/evals/cross-model-instruction-authoring) — trigger and behavior suite.
