# commit-message-quality

> Draft, rewrite, or validate one commit message with clear rationale, consistent grammar, real trailers, and safe reporting.

This read-only skill reads existing commitlint/hook/check definitions before fallback grammar and applies a default whole-subject 72-character limit, conventional-by-default grammar, a why-focused body, and breaking-change/footer rules with default blank-line separation before footers. It recommends splits for mixed changes without rewriting history or creating commits.

Validation preserves the message except required removal or redaction of forbidden content and records failed parts as `noncompliant`. Ordered statuses prioritize missing required facts/rules, remaining violations, then drafting/correction. Repairs use `rewritten` even when they delete an invalid part; a permitted absent Body (trivial or nontrivial under selected rules) or optional absent Footers use `compliant` when already absent or intentionally omitted while drafting. Unresolved facts or required message rules use `needs-author-input`. The distinctive report keeps Subject/Body/Footers statuses and checks separate from finding severity. Findings use `Subject`, `Body`, `Footers`, `Input`, or `Convention` anchors with severity and a detail payload appropriate to the finding; mandatory `Convention: information` records convention evidence or assumptions even in CLEAN reports. In a non-BLOCK report, excluded sensitive source content uses an `Input: error` finding and `CONCERNS`, without adding a fourth check or fabricating a message-part failure. Missing required input produces a reduced `BLOCK` report with concrete missing-input and requested-addition values.

Caller rules take precedence over readable repository rules, consistent history, and generic message defaults for all convention/style rules, including case, punctuation and footer formatting. Safety, evidence, breaking-change disclosure and report/status/severity/verdict requirements remain mandatory. Every declared required rule that cannot be determined requires clarification; when affected parts are unknown, all three checks fail with `needs-author-input`, including absent Body or Footers. Configuration and hooks are never executed by the skill.

The core contains all normal-path decisions, output labels and failure rules. References hold type-selection illustrations and sourced Git cleanup details. Validation preserves safe supplied headings with preservation advice. Non-violating cleanup advice appears as a `Body: information` finding, states `unverified` when cleanup is unknown, and alone neither fails checks nor requires author input nor prevents `CLEAN`. Draft/repair retain caller- or repository-required headings with preservation advice; optional headings are omitted when their preservation is unknown. Repository prose is unwrapped; commit-body wrapping remains a caller-overridable default.

## Files

- [`SKILL.md`](SKILL.md) — triggers, workflow, grammar, statuses, verdicts, report contract, and completion checklist.
- [`references/types-and-examples.md`](references/types-and-examples.md) — conventional type policy, removal choices, and non-normative message/split examples.
- [`references/git-cleanup.md`](references/git-cleanup.md) — when comment-like headings survive Git cleanup and how to preserve them.
