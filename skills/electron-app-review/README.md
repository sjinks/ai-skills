# Electron App Review

Review Electron desktop app changes that affect window isolation, preload and IPC, local filesystem or process authority, desktop lifecycle, or release behavior. Trace renderer requests to privileged side effects and identify where authorization is enforced.

Use for defensive review of designs, source, and diffs. Renderer-only UI changes without desktop boundary impact are out of scope.

## Files

- [SKILL.md](SKILL.md) — Scope, review workflow, severity, verdicts, and report format.
- [Review checklist](references/review-checklist.md) — Electron-specific checks and scope examples.
