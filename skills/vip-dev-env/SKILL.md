---
name: vip-dev-env
description: WordPress VIP Local Development Environment guidance using VIP-CLI (`vip dev-env`). Use when creating or updating local VIP dev environments, loading app code, inspecting stack services/logs, troubleshooting startup or 500 errors, or explaining VIP WordPress skeleton repo structure and local-vs-container code boundaries.
argument-hint: "Environment slug, primary symptom or task, and exact CLI error text when troubleshooting."
user-invocable: true
---

# VIP Dev Env

## Overview

Provide focused, step-by-step help for WordPress VIP Local Development Environment workflows across macOS, Windows (WSL2), and Linux.
Keep explanations grounded in VIP-CLI commands and the local-vs-container code split.
Ask for the environment slug before any command that targets a single environment; for global commands that do not take `--slug` (such as `vip dev-env purge` and `vip dev-env stop --all`), confirm scope with `vip dev-env list` and get explicit confirmation first. For read-only diagnostics, proceed and resolve an unknown slug with `vip dev-env list` (users may have multiple LDEs).

## Security and safe defaults

- Ask for `--slug` before suggesting single-environment commands that modify state. For global commands that do not take `--slug` (such as `vip dev-env purge` and `vip dev-env stop --all`), confirm scope with `vip dev-env list` and get explicit confirmation before running.
- For troubleshooting, ask for the primary symptom first (for example: start failure, HTTP 500, DNS issue, DB issue).
- Ask for the exact error text before suggesting fixes. Prefer message-driven guidance over generic troubleshooting when the user already has CLI output.
- Prefer loopback-only networking (`127.0.0.1`) unless the user explicitly needs LAN access.
- Treat logs and SQL dumps as sensitive. Avoid sharing tokens, passwords, cookies, or personal data.
- Call out destructive commands before suggesting them (for example: `vip dev-env destroy`, sync/import workflows that overwrite local data, index setup resets).
- Prefer least-privilege guidance: use only the permissions needed for the specific operation.

## Incident intake template

Collect this before remediation commands:

- Slug: `<slug>`
- Primary symptom: startup failure | HTTP 500 | domain/DNS | DB sync/import | code not reflected
- What changed last: CLI/Docker/Node update, repo switch, config change, or unknown
- Scope and urgency: single env or multiple envs, blocking release/testing or not
- Safe artifacts available: sanitized logs, error snippet, recent command and output

## Core mental model

- App repo is local (WordPress skeleton directories only).
- WordPress core and VIP MU plugins live inside the container image.
- Local repo changes are reflected immediately in the running LDE.

## Workflow decision tree

This is the canonical router; the "Common tasks and prompts to handle" section gives example phrasings that defer to these routes.

- Need to run a single-environment command that modifies state (create, update, start, stop one env, destroy, sync, import, envvar set/delete): ask for the `--slug` value first.
- Need to run a global command that does not take `--slug` (`purge`, `stop --all`): confirm scope with `vip dev-env list` and get explicit confirmation before running, since it affects all local environments.
- Need read-only diagnostics (`info`, `logs`, `list`): proceed and resolve the slug with `vip dev-env list` if it is unknown.
- Need to diagnose a failure: ask for the symptom and the exact CLI error text, then use `references/troubleshooting.md` triage flow.
- Need security constraints or risky-operation guidance: use `references/security.md` first.
- Need exact options, defaults, or command shape for a subcommand: run `vip dev-env <command> --help` before proposing syntax.
- Need authoritative command syntax/details beyond local help output: verify against `https://docs.wpvip.com/vip-cli/commands/`.
- Need targeting rules (`@app.env` vs local slug-based commands): verify against `https://docs.wpvip.com/vip-cli/target-environments/`.
- Need help with command syntax, `--`, or local-vs-remote targeting: use `references/command-syntax.md`.
- Need a new local environment: follow the create flow in `references/create.md`.
- Need lifecycle help for start, stop, info, list, destroy, or purge: use `references/dev-env-overview.md` first, then `references/troubleshooting.md` if the command fails.
- Need Docker-specific failures (`Failed to connect to Docker`, permission denied on `/var/run/docker.sock`, daemon not running, disk/log exhaustion): start with the `Docker quick-check (10-second triage)` and `60-second triage macro` in `references/troubleshooting.md`, then continue with the Docker playbook and retry the original `vip dev-env` command. That reference also covers capturing the `COMMAND LOG FILE`, compose-version-split signals, and known false positives.
- Need to escalate a Docker failure that persists after baseline plus one targeted branch: use the `Stop-and-escalate gate`, escalation bundles, and support-ticket template in `references/troubleshooting.md`.
- Need to load app code: follow `references/load-app-code.md`.
- Need service URLs or logs: use `references/stack-services.md`.
- Need to manage local `.env` values for an LDE: use `references/envvars.md`.
- Troubleshooting (env not starting, 500s, flaky services): start with `references/troubleshooting.md`, then drill into service logs.

## Common tasks and prompts to handle

- "Dev env does not start" -> follow the Docker and escalation routes in the Workflow decision tree above (`references/troubleshooting.md`), retrying with `--debug` and `vip dev-env logs` between branches.
- "Site returns 500" -> check PHP logs with `vip dev-env logs --service=php --slug=<slug> --follow`, validate local code changes.
- "DB sync/import failed or produced bad data" -> backup local DB first, run targeted sync/import commands, verify URL rewriting behavior.
- "Domain does not resolve / wrong site opens" -> inspect bind address, domain pattern, and hosts/DNS mapping.
- "Create a local env for <app>" -> `vip dev-env create --slug=<slug>` wizard and prerequisites.
- "Create a local env from remote app settings" -> `vip @<app>.<env> dev-env create --slug=<slug>` and then verify local config before start.
- "Load local app code" -> clone repo, `vip dev-env update --app-code=/absolute/path/to/repo --slug=<slug>`, restart.
- "Set a local env var" -> `vip dev-env envvar set --slug=<slug> <NAME> <VALUE>` and restart after changes; see `references/envvars.md` for `get`, `get-all`, `list`, and `delete`.
- "Import a SQL dump" -> `vip dev-env import sql /absolute/path/file.sql --slug=<slug>` and use `references/add-database-content.md` for search-replace and validation flags.
- "Import local media" -> `vip dev-env import media /absolute/path/uploads --slug=<slug>` and use `references/add-media-content.md`.
- "Start and generate editor workspace" -> `vip dev-env start --editor=<editor> --slug=<slug>`; check the current `--editor` values with `vip dev-env start --help`.
- "Where is WordPress core / MU plugins?" -> explain container code vs local repo.

## High-value error messages to recognize

- `Environment doesn't exist.` -> confirm slug, avoid `@app.env` notation unless the command supports it, create the env if needed.
- `Environment already exists.` -> switch to `vip dev-env start --slug=<slug>` or choose a new unique slug.
- `More than one environment found:` -> require `--slug=<slug>` on all follow-up commands.
- `This command does not support @app.env notation.` -> replace `vip @<app>.<env> dev-env ...` with the local target form using `--slug=<slug>`.
- `docker binary could not be located!` -> install Docker Engine/Desktop first.
- `Failed to connect to Docker.` -> start Docker daemon/Desktop and re-run.
- `A double dash ("--") must separate...` -> correct `vip dev-env exec` or `vip dev-env shell` syntax before deeper debugging.
- `A WP-CLI command can only be executed on a running local environment.` or `Environment needs to be started first` -> run `vip dev-env start --slug=<slug>` first, then retry.
- `Service '<name>' not found.` or `<tool> is not a known lando task` -> inspect `vip dev-env info --slug=<slug>` and use a supported service/task.
- `Configuration file ... could not be loaded` or `invalid configuration-version key` -> fix `vip-dev-env.yml` before retrying create/update.
- `Unknown or unsupported PHP version:` or `Unknown or unsupported WordPress version:` -> select a supported value and rerun.
- `Provided path "..." does not point to a valid or existing directory.` -> fix the absolute path before relying on `--app-code` or `--mu-plugins`.
- `The provided file ... does not exist or it is not valid (see "--help" for examples)` -> fix the local import file path before retrying `import sql`.
- `The provided path does not exist or it is not valid (see "--help" for examples)` -> fix the local directory path before retrying `import media`.
- `Media redirect domain must be a domain name or an URL` -> provide a real hostname or URL, not a boolean-like value.
- `Environment variable name must consist of A-Z, 0-9, or _, and must start with an uppercase letter.` -> rename the variable before retrying `vip dev-env envvar set`.
- `The environment variable "<NAME>" does not exist` -> verify the name with `vip dev-env envvar list --slug=<slug>`.
- `There are no environment variables` -> initialize them with `vip dev-env envvar set --slug=<slug> NAME VALUE`.

## Provenance

Guidance is grounded in VIP-CLI behavior and official WordPress VIP and Docker documentation. See `references/source-map.md` for source confidence and the authoritative links to verify command syntax, defaults, and error strings against.

## References to load as needed

- [references/dev-env-overview.md](references/dev-env-overview.md) for orientation and `vip dev-env info`.
- [references/create.md](references/create.md) for prerequisites and the create wizard.
- [references/load-app-code.md](references/load-app-code.md) for wiring a local repo.
- [references/stack-services.md](references/stack-services.md) for services, logs, cache, and core path.
- [references/add-media-content.md](references/add-media-content.md) for media import and media proxying.
- [references/troubleshooting.md](references/troubleshooting.md) for version checks, `--debug`, and log commands.
- [references/security.md](references/security.md) for safe defaults, redaction, destructive-action controls, and exposure risks.
- [references/command-syntax.md](references/command-syntax.md) for separator rules, `@app.env` vs `--slug`, and common command forms.
- [references/envvars.md](references/envvars.md) for local environment variable workflows and related errors.
- [references/wordpress-skeleton.md](references/wordpress-skeleton.md) for repo layout and deployable paths.
- [references/enable-https.md](references/enable-https.md) for HTTPS and local CA trust.
- [references/enterprise-search.md](references/enterprise-search.md) for Enterprise Search setup.
- [references/add-database-content.md](references/add-database-content.md) for database sync/import.
- [references/networking.md](references/networking.md) for custom domains, DNS, and bind address configuration.
- [references/source-map.md](references/source-map.md) for source confidence and authoritative links to verify against.
- `https://docs.wpvip.com/vip-local-development-environment/` for official LDE docs and requirements links.
- `https://docs.wpvip.com/vip-cli/` for official VIP-CLI command and troubleshooting docs.
- `https://docs.wpvip.com/vip-local-development-environment/troubleshooting-dev-env/` for upstream LDE troubleshooting guidance.
- `https://docs.wpvip.com/vip-cli/troubleshooting/` for upstream VIP-CLI troubleshooting guidance.
- `https://docs.docker.com/engine/daemon/troubleshoot/` for daemon-level diagnostics and recovery.
- `https://docs.docker.com/engine/install/linux-postinstall/` for Linux daemon permissions and non-root usage.
- `https://docs.docker.com/config/containers/logging/configure/` for log-driver and rotation behavior that can affect local disk health.
