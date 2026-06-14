Read this for service discovery, logs, and common runtime behavior.

# Stack services and logs

Risk level
- Level: Mixed (Low/High)
- Why: Read-only info/log commands are low risk; destructive lifecycle actions can remove local database state.
- Controls: Apply controls from `references/security.md`.

Discover services and URLs
- `vip dev-env info --slug=<slug>`
- Use `vip dev-env list` for a quick inventory of all local environments.

Service logs
- All services: `vip dev-env logs --slug=<slug>`
- Specific service: `vip dev-env logs --service=<service> --slug=<slug>`
- Follow logs: add `--follow`
- Treat logs as sensitive: redact secrets, tokens, cookies, and personal data before sharing.

Database
- Fresh LDE has a basic WordPress schema only.
- Database persists across stop/start but is removed on `vip dev-env destroy`.
- Warn before destructive actions that remove local database state.

Object cache
- Memcached runs in LDE.
- Flush cache with WP-CLI inside the container:
  - `vip dev-env exec --slug=<slug> -- wp cache flush`

PHP
- The set of supported local PHP versions changes between VIP-CLI releases. Check the current values with `vip dev-env create --help` (or `vip dev-env update --help`) rather than relying on a hard-coded list.

WordPress core path
- WordPress core and VIP MU plugins are container-managed; the app repo holds only the WordPress skeleton directories.
- For this LDE, the container mounts core under the VIP-CLI data directory (base path platform/version-dependent, commonly `~/.local/share/vip` on Linux/WSL2), at a path such as:
  - `<vip-data-dir>/dev-environment/<slug>/wordpress/`
- Treat this path as inspection-only. Do not edit core or MU-plugin files there; those edits are not part of the app repo, are easy to lose, and diverge from the platform image.
- Make changes in the local app repo instead; reset container-managed state by recreating or `vip dev-env destroy --soft`.

Quick service triage
1) `vip dev-env info --slug=<slug>` for URLs and ports.
2) `vip dev-env logs --slug=<slug>` for full stack context.
3) Follow the most relevant service (`php`, `nginx`, `database`, `elasticsearch`).

Common service and command errors
1) `Service '<name>' not found. Please choose from one: ...`
- Run `vip dev-env info --slug=<slug>` and retry with one of the listed service names.

2) `<tool> is not a known lando task`
- The task or service is not available in this env definition.
- Re-check the command target and enabled services before retrying.

3) `A WP-CLI command can only be executed on a running local environment.`
- Start the env first: `vip dev-env start --slug=<slug>`.

4) `Environment needs to be started first`
- Start the env first: `vip dev-env start --slug=<slug>`.

5) `A double dash ("--") must separate...`
- For WP-CLI use: `vip dev-env exec --slug=<slug> -- wp cache flush`
- For shell use: `vip dev-env shell --slug=<slug> -- ls -lha`

See also
- Use `references/command-syntax.md` when the failure is about separators, `--slug`, or `@app.env` targeting.
- Use `references/envvars.md` for local `.env` troubleshooting instead of service-level logs.
