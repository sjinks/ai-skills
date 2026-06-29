# pr-description-quality

> Use when: writing, rewriting, updating from the branch's commit history, validating, or auditing one pull request's title and description for quality: a title that names the whole PR, a body that explains what changed and why with honest testing notes, linked issues, risks, and no leaked secrets — honoring the repo's PR template when one exists.

This skill is aimed at one pull request's title and body — drafting them from the branch's commits, rewriting a weak draft, or validating them against the contract before the PR is opened or updated.

It helps an assistant:

- detect and honor the repo's `PULL_REQUEST_TEMPLATE` when present, falling back to a default summary/changes/testing/risks/linked-issues structure, and state which was used
- enforce a title contract: one line describing the whole PR, conventional `type(scope)!:` form when the repo uses it, a length note past 72 characters, issue keys kept out of the title unless convention requires them
- enforce a body contract written for the approving reviewer: what changed and why in reviewer terms over a restated diff, reproducible testing/verification steps a reviewer can rerun (never claiming an unrun check), linked issues, and explicit risks, breaking changes, and rollout notes
- omit genuinely irrelevant sections instead of padding them, synthesize the branch's commit history into reviewer-meaningful points — collapsing fixups, theming related commits, and dropping noise rather than transcribing the log — and flag secrets or PII rather than posting them
- mark each part `compliant`, `rewritten`, `noncompliant` (validate-mode failure left unchanged), or `needs-author-input`, and return the PR description quality report with a verdict, the detected structure, the title and body, and per-part checks, or `BLOCK` when neither a draft nor any change description is supplied

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
