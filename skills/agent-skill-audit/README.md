# agent-skill-audit

> Use when assessing whether an agent instruction or Agent Skill package is
> ready for its intended task, target models, and runtime.

This skill performs a holistic readiness audit across discovery/delegation,
instruction architecture, operational completeness, model/runtime portability,
and maintainability/evaluability, returning ratings, material findings,
target-model compatibility, priority changes, and a readiness verdict.

It does not replace `instruction-quality-audit`, which is the line-level
diagnostic skill for exact contradictions, ambiguity, authority conflicts,
closure gaps, harmful duplication, and output-contract defects.

The default compatibility floor is GPT-6 Luna and Claude Haiku 5.5. Caller-supplied target models replace the default assessment roster; static profiles do not establish measured model behavior.

The default roster also includes Sonnet 5.5, Opus 5.5, Fable 5.1 and restricted-access Mythos 5.1 alongside the existing profiles. Haiku 5.5 checks use current prompting guidance; API and harness checks are conditional and do not establish runtime access.

## Files

- [`SKILL.md`](SKILL.md) — the full readiness-audit skill definition.
- [`references/model-portability.md`](references/model-portability.md) — static model-profile checks for the supported target models.
- [`references/package-analysis.md`](references/package-analysis.md) — package/path load-graph rules, duplicate handling, and verification-artifact assessment.
- [`references/readiness-rubric.md`](references/readiness-rubric.md) — the five readiness rating areas and calibration guidance.
- [`references/report-contract.md`](references/report-contract.md) — the required readiness report markers, placeholder replacement rules, target-model verdict values, multiple-report numbering, blocked behavior, and no-findings contract.
- [`references/haiku-5-5-runtime.md`](references/haiku-5-5-runtime.md) — conditional Haiku API/harness checks for thinking, tool use, input delivery and failure handling.
