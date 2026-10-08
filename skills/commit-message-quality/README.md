# commit-message-quality

> Draft, rewrite, or validate one commit message with clear rationale, consistent grammar, real trailers, and safe reporting.

This read-only skill applies a whole-subject 72-character limit, conventional-by-default grammar, a why-focused body, and breaking-change/footer rules. It recommends splits for mixed changes without rewriting history or creating commits.

Validation preserves the message except sensitive-value redaction and records failed parts as `noncompliant`. Drafting and repair use `rewritten`; unresolved facts use `needs-author-input`. The distinctive report keeps Subject/Body/Footers statuses and checks separate from finding severity. Missing required input produces a reduced `BLOCK` report.

The core contains all normal-path decisions, output labels and failure rules. References hold type-selection illustrations and sourced Git cleanup details. Repository prose is unwrapped; commit-body wrapping remains a caller-overridable default.

## Files

- [`SKILL.md`](SKILL.md) — triggers, workflow, grammar, statuses, verdicts, report contract, and completion checklist.
- [`references/types-and-examples.md`](references/types-and-examples.md) — conventional type policy, removal choices, and non-normative message/split examples.
- [`references/git-cleanup.md`](references/git-cleanup.md) — when comment-like headings survive Git cleanup and how to preserve them.
