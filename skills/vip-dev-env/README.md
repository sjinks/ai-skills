# vip-dev-env

> WordPress VIP Local Development Environment guidance using VIP-CLI (`vip dev-env`). Use when creating or updating local VIP dev environments, loading app code, inspecting stack services/logs, troubleshooting startup or 500 errors, or explaining VIP WordPress skeleton repo structure and local-vs-container code boundaries.

This skill is aimed at WordPress VIP Local Development Environment (LDE) workflows driven by `vip dev-env` across macOS, Linux, and Windows (WSL2), where guidance must stay grounded in real CLI commands and the local-repo-vs-container code split.

It helps an assistant:

- ask for the environment `--slug` before single-environment commands that modify state, and confirm scope for global commands (`purge`, `stop --all`) that take no `--slug`; collect the primary symptom and exact CLI error text before remediation
- explain the core mental model: the app repo is local (WordPress skeleton directories), while WordPress core and VIP MU plugins live inside the container image
- route each task through a decision tree to the right reference (create, load app code, stack services, envvars, networking, HTTPS, Enterprise Search, database/media import, command syntax, and troubleshooting)
- recognize high-value error messages (missing or ambiguous slug, rejected `@app.env` notation, Docker connectivity, double-dash separator, unsupported versions, invalid paths, envvar validation) and map each to a first-fix command
- run message-driven Docker triage with quick-checks, false-positive elimination, a stop-and-escalate gate, and sanitized escalation bundles instead of generic checklists
- call out destructive commands (`destroy`, `purge`, sync/import overwrites) and sensitive-data exposure in logs and SQL dumps before suggesting them

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- [`references/`](references/) — extended workflow and reference material.
