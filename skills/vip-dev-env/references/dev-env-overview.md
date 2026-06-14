Read this for high-level explanations and quick orientation.

# VIP Local Development Environment overview

- VIP Local Development Environment (LDE) is built into VIP-CLI (`vip dev-env`).
- It uses Docker containers to mirror VIP Platform environments for local work.
- Good for local development, quick testing, and tutorials.
- Services expose local ports; use `vip dev-env info --slug=<slug>` to see URLs.

Command families
- Create and change envs: `create`, `update`, `start`, `stop`, `destroy`, `purge`
- Inspect envs: `info`, `list`, `logs`
- Run commands inside envs: `exec`, `shell`
- Move data: `import media`, `import sql`, `sync sql`
- Manage local env vars: `envvar` subcommands `set`, `get`, `get-all`, `list`, and `delete`

Lifecycle quick reference
- Stop one env: `vip dev-env stop --slug=<slug>`
- Stop all envs: `vip dev-env stop --all`
- Destroy one env but keep config for rebuild: `vip dev-env destroy --soft --slug=<slug>`
- Destroy one env completely: `vip dev-env destroy --slug=<slug>`
- Purge all envs with confirmation: `vip dev-env purge`
- Purge all envs non-interactively: `vip dev-env purge --force`
- Purge all envs but preserve configs: `vip dev-env purge --soft`

Lifecycle recovery signals
- `Environment not found.` (commonly from stop) or `Environment doesn't exist.` means the target slug is missing.
- `No environments to purge!` means there is nothing to remove.
- Use `vip dev-env list` before destructive lifecycle commands when target scope is unclear.

Useful reminders
- Most local-only commands should use `--slug=<slug>`.
- `vip dev-env exec` and `vip dev-env shell` require `--` before the inner command.
- `vip @<app>.<env> dev-env create` and `vip @<app>.<env> dev-env sync sql` are the main remote-backed patterns.
