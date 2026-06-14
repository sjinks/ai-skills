Read this when bringing VIP Platform data into a local environment.

# Sync or import database content

Risk level
- Level: High
- Why: Sync/import can overwrite local data.
- Controls: Apply controls from `references/security.md`.

Prereqs
- LDE is created and running.
- User has at least Org admin or App admin for the target app.

Safety first
- Sync/import can overwrite local data. Back up local DB before running.
- Avoid sharing SQL dumps or logs that may include personal or sensitive data.

Sync latest backup
- `vip @<app>.<env> dev-env sync sql --slug=<slug>`

Import a local SQL file
- `vip dev-env import sql /absolute/path/file.sql --slug=<slug>`

Common import options
- Search and replace during import:
  - `vip dev-env import sql /absolute/path/file.sql --search-replace="old.example.com,<slug>.vipdev.lndo.site" --slug=<slug>`
- Perform the search and replace in the local file before import:
  - `vip dev-env import sql /absolute/path/file.sql --search-replace="old.example.com,<slug>.vipdev.lndo.site" --in-place --slug=<slug>`
- Skip Elasticsearch reindex after import:
  - `vip dev-env import sql /absolute/path/file.sql --skip-reindex --slug=<slug>`
- Skip file validation only when the file is trusted and validation is the blocker:
  - `vip dev-env import sql /absolute/path/file.sql --skip-validate --slug=<slug>`

Partial sync
- Limit to a table:
  - `vip @<app>.<env> dev-env sync sql --slug=<slug> --table=wp_posts`
- Limit to multiple tables:
  - `vip @<app>.<env> dev-env sync sql --slug=<slug> --table=wp_posts --table=wp_comments`
  - `vip @<app>.<env> dev-env sync sql --slug=<slug> --table=wp_posts,wp_comments`
- For multisite, target a site ID:
  - `vip @<app>.<env> dev-env sync sql --slug=<slug> --site-id=<id>`
- For multiple sites, repeat `--site-id` or use a comma-separated list.
- For complex partial sync rules, use a local JSON config file:
  - `vip @<app>.<env> dev-env sync sql --slug=<slug> --config-file=/absolute/path/dev-env-sync-config.json`
- For custom extraction logic, use a WP-CLI selector command:
  - `vip @<app>.<env> dev-env sync sql --slug=<slug> --wpcli-command='<wp-cli export selector>'`

Multisite URL behavior
- Primary domains become `<slug>.vipdev.lndo.site`.
- Secondary domains become `<slugified-domain>.<slug>.vipdev.lndo.site`.

Troubleshooting
1) If sync fails, retry with `--table=<table>` to isolate failures.
2) For multisite mismatches, verify `--site-id=<id>`.
3) After sync, test front end and wp-admin for URL and login behavior.

Common sync/import errors and fixes
1) `Environment needs to be started first`
- Start the local env before `vip dev-env import sql` or `vip @<app>.<env> dev-env sync sql`.
- Ensure both PHP and database services are up.

2) `Error extracting the SQL file:` or `Error extracting the SQL export:`
- Verify the archive is readable and there is enough local disk space for extraction.

3) `Error extracting site URLs:` or `Error getting site URLs from SDS:`
- Retry the sync after confirming the export completed and the target app/environment metadata is valid.

4) `Error replacing domains:`
- Treat this as a search-replace failure. Retry with sanitized debug output and verify the dump is not malformed.

5) `Error importing SQL file:`
- Check local database health with `vip dev-env logs --service=database --slug=<slug> --follow`.
- Retry only after the env is healthy.

6) `WARNING: data cleanup failed.`
- The import may still have succeeded.
- Validate front end, wp-admin, and critical content before deciding on a rerun.

7) `The provided file ... does not exist or it is not valid (see "--help" for examples)`
- Verify the SQL file path exists and points to a readable local file.
- Prefer an absolute path before retrying `vip dev-env import sql`.
