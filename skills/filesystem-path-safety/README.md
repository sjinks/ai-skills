# filesystem-path-safety

> Use when: auditing code that builds filesystem paths from external input and then reads, creates, mutates, or deletes files under a trusted root. Detects traversal, symlink-follow, TOCTOU, file-type confusion, validator error-contract drift, and resource-ordering issues.

This skill is aimed at code that turns external input into filesystem paths under a trusted root and then reads, creates, mutates, or deletes files.

It helps an assistant:

- establish the target, trusted root, external-input surface, and operation kind before judging
- audit validation, canonicalization, containment, symlink, hardlink, TOCTOU, and mutation-ordering controls
- distinguish static safe paths from externally influenced paths that need a trusted-root contract
- support local output depth (`quick`, `standard`, or `exhaustive`), while `quick` still reports missing context, blockers, high-risk concerns, and target-specific findings
- return anchored findings, insufficient-context blocks, and test expectations without broader web-app review structure

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- [`references/`](references/) — extended workflow and reference material.
