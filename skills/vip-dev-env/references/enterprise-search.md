Read this when Enterprise Search needs to be tested locally.

# Use Enterprise Search on a VIP Local Development Environment

Risk level
- Level: High
- Why: Index setup can reset local index data.
- Controls: Apply controls from `references/security.md`.

Prereqs
- VIP-CLI installed and current.
- User can create a local environment.

Create a compatible environment
- Must be multisite and have Elasticsearch enabled.
- Must point to a local app repo.
- Example (check current `--multisite` values with `vip dev-env create --help`):
  - `vip dev-env create --multisite=<multisite> --elasticsearch --app-code=/absolute/path/to/repo --slug=<slug>`
  - `vip dev-env start --slug=<slug>`

Enable Enterprise Search in code
- Edit `vip-config/vip-config.php` in the app repo.
- Add:
  - `define( 'VIP_ENABLE_VIP_SEARCH', true );`
  - `define( 'VIP_ENABLE_VIP_SEARCH_QUERY_INTEGRATION', true );`

Create the Elasticsearch index
- `vip dev-env exec --slug=<slug> -- wp vip-search index --setup`
- Confirm the destructive prompt when asked.
- Warn users this can reset existing local index data.

Verify
- WP Admin: “Enterprise Search” menu item.
- Front end: Search Dev Tools in the admin toolbar.

Troubleshooting
1) Confirm multisite and Elasticsearch were enabled during creation.
2) Check Elasticsearch service logs for startup/index errors.
3) Re-run setup command only after confirming expected local data impact.
4) If `vip dev-env exec` reports that the env is not running, start it first with `vip dev-env start --slug=<slug>`.
5) If the command syntax error mentions a missing double dash, rerun as `vip dev-env exec --slug=<slug> -- wp vip-search index --setup`.
