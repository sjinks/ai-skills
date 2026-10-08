# commit-message-quality

> Draft, rewrite, or validate one commit message with clear rationale, consistent grammar, real trailers, and safe reporting.

This read-only skill reads existing commitlint/hook/check definitions before fallback grammar and applies a default whole-subject 72-character limit, conventional-by-default grammar, a why-focused body, and breaking-change/footer rules. It recommends splits for mixed changes without rewriting history or creating commits.

Validation preserves the message except required removal or redaction of forbidden content and records failed parts as `noncompliant`. Drafted nonempty parts and repairs use `rewritten`; permitted absent trivial Body or absent Footers use `compliant` in every mode; unresolved facts or required message rules use `needs-author-input`. The distinctive report keeps Subject/Body/Footers statuses and checks separate from finding severity. Missing required input produces a reduced `BLOCK` report.

Caller rules take precedence over readable repository rules, consistent history, and generic message defaults for all convention/style rules, including case, punctuation and footer formatting. Safety, evidence, breaking-change disclosure and report/status/severity/verdict requirements remain mandatory. Every declared required rule that cannot be determined requires clarification; when affected parts are unknown, all three checks fail with `needs-author-input`, including absent Body or Footers. Configuration and hooks are never executed by the skill.

The core contains all normal-path decisions, output labels and failure rules. References hold type-selection illustrations and sourced Git cleanup details. Repository prose is unwrapped; commit-body wrapping remains a caller-overridable default.

## Files

- [`SKILL.md`](SKILL.md) — triggers, workflow, grammar, statuses, verdicts, report contract, and completion checklist.
- [`references/types-and-examples.md`](references/types-and-examples.md) — conventional type policy, removal choices, and non-normative message/split examples.
- [`references/git-cleanup.md`](references/git-cleanup.md) — when comment-like headings survive Git cleanup and how to preserve them.
