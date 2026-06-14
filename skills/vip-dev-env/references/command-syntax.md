Read this when a `vip dev-env` command fails before doing any real work, especially around `--slug`, `@app.env`, or `--` separator handling.

# Command syntax and targeting

Risk level
- Level: Low
- Why: These are command-shape fixes, not data-changing operations by themselves.
- Controls: Apply controls from `references/security.md`.

Core rules
- Local-only LDE commands should target the environment with `--slug=<slug>`.
- Remote-backed flows can combine `@<app>.<env>` with a local target `--slug=<slug>` when the command seeds local configuration from VIP Platform or syncs remote data into an existing LDE.
- `vip dev-env exec` and `vip dev-env shell` require a literal `--` before the inner command.

Use `--slug` for local-only commands
- `vip dev-env start --slug=<slug>`
- `vip dev-env stop --slug=<slug>`
- `vip dev-env logs --slug=<slug>`
- `vip dev-env info --slug=<slug>`
- `vip dev-env exec --slug=<slug> -- wp option get home`
- `vip dev-env shell --slug=<slug> -- ls -lha`
- `vip dev-env envvar list --slug=<slug>`

Use `@<app>.<env>` only for remote-backed flows that support it
- `vip @<app>.<env> dev-env create --slug=<slug>`
- `vip @<app>.<env> dev-env sync sql --slug=<slug>`
- `vip @<app>.<env> dev-env sync sql --slug=<slug> --table=wp_posts`

Exact syntax errors and fixes
1) `This command does not support @app.env notation. Use '--slug=...' to target the local environment.`
- Remove `@<app>.<env>` from local-only commands.
- Re-run with `vip dev-env <command> --slug=<slug>`.

2) `A double dash ("--") must separate the arguments of "vip" from those of the "wp" command.`
- Fix `exec` syntax to:
  - `vip dev-env exec --slug=<slug> -- wp option get home`

3) `A double dash ("--") must separate the arguments of "vip" from those of the command to be executed.`
- Fix `shell` syntax to:
  - `vip dev-env shell --slug=<slug> -- ls -lha`

4) `More than one environment found:`
- Add `--slug=<slug>` to every follow-up command.

Copy-paste recovery commands
- Confirm local envs:
  - `vip dev-env list`
- Confirm the selected env:
  - `vip dev-env info --slug=<slug>`
- Correct `exec` form:
  - `vip dev-env exec --slug=<slug> -- wp option get home`
- Correct `shell` form:
  - `vip dev-env shell --slug=<slug> -- env | sort`
- Correct remote-to-local SQL sync form:
  - `vip @<app>.<env> dev-env sync sql --slug=<slug>`