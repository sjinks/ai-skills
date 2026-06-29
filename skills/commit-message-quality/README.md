# commit-message-quality

> Use when: writing, rewriting, validating, or auditing a single git commit message for quality: a conventional subject (type, scope, breaking marker, imperative ≤72-char description), a body that explains why rather than restating the diff, valid footers, and no leaked secrets — so history stays reviewable and bisectable.

This skill is aimed at one commit message at a time — drafting it from a staged diff, rewriting a weak draft, or validating a message against the contract before it is committed.

It helps an assistant:

- detect the applicable convention — Conventional Commits by default (including empty or mixed-history repos), plain mode only when the repo clearly rejects it — and state the mode used
- enforce a subject contract: smallest accurate type, optional lowercase scope, `!` plus `BREAKING CHANGE:` footer for contract breaks, imperative ≤72-char description with no trailing period
- enforce a body contract: explain why over restating the diff, allow a trivial one-line body, keep test-run evidence in the pull request, and warn about `#`-line cleanup when optional headers are used
- enforce a footer contract: issue trailers, `BREAKING CHANGE:`, and other real trailers only
- recommend a commit split instead of a vague subject when the diff mixes unrelated concerns, and flag secrets or PII rather than committing them
- mark each part `compliant`, `rewritten`, or `needs-author-input`, and return the commit message quality report with a verdict, the detected mode, the full message, and per-part checks, or `BLOCK` when neither a message nor a change description is supplied

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
