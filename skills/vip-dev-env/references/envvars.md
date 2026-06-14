Read this when managing `.env` values for a local development environment with `vip dev-env envvar`.

# Local environment variables

Risk level
- Level: Medium
- Why: Env var changes alter runtime behavior and may expose secrets if shared carelessly.
- Controls: Apply controls from `references/security.md`.

Core behavior
- Local env vars are stored in the LDE `.env` file for the selected slug.
- `set` writes or updates the variable.
- `get`, `get-all`, and `list` read the local `.env` state.
- `delete` removes the variable from the local `.env` file.
- After `set` or `delete`, VIP-CLI prints an important reminder to restart the environment before the change takes effect.

Common commands
- List names:
  - `vip dev-env envvar list --slug=<slug>`
- List names as CSV or JSON:
  - `vip dev-env envvar list --slug=<slug> --format=csv`
  - `vip dev-env envvar list --slug=<slug> --format=json`
- List names and values:
  - `vip dev-env envvar get-all --slug=<slug>`
- List names and values as CSV or JSON:
  - `vip dev-env envvar get-all --slug=<slug> --format=csv`
  - `vip dev-env envvar get-all --slug=<slug> --format=json`
- Read one value:
  - `vip dev-env envvar get --slug=<slug> MY_VARIABLE`
- Set one value inline:
  - `vip dev-env envvar set --slug=<slug> MY_VARIABLE MY_VALUE`
- Set a multiline value from file:
  - `vip dev-env envvar set --slug=<slug> MULTILINE_ENV_VAR --from-file=envvar-value.txt`
- Delete one value:
  - `vip dev-env envvar delete --slug=<slug> MY_VARIABLE`

Exact envvar errors and fixes
1) `Environment variable name must consist of A-Z, 0-9, or _, and must start with an uppercase letter.`
- Rename the variable so it matches the CLI validator.
- Good examples: `API_TOKEN`, `FEATURE_FLAG_1`
- Bad examples: `api_token`, `1TOKEN`, `MY-VAR`

2) `The environment variable "<NAME>" does not exist`
- Confirm the exact name with `vip dev-env envvar list --slug=<slug>`.
- If the variable should exist, recreate it with `vip dev-env envvar set --slug=<slug> <NAME> <VALUE>`.

3) `There are no environment variables`
- The `.env` file has no active entries for that local environment.
- Create the first one with `vip dev-env envvar set --slug=<slug> MY_VARIABLE MY_VALUE`.

4) `Environment doesn't exist.`
- Confirm the slug with `vip dev-env list`.
- Create the env first if needed.

5) File-read failure while using `--from-file`
- Verify the UTF-8 text file path exists and is readable from the current shell.
- Prefer an absolute path when the current working directory is unclear.

Operational guidance
- Use `--from-file` for multiline values instead of interactive paste.
- Do not paste secrets into shared terminals or tickets.
- Restart after `set` or `delete`:
  - `vip dev-env start --slug=<slug>`

Copy-paste recovery commands
- Inspect what exists:
  - `vip dev-env envvar list --slug=<slug>`
- Read all values for a local audit:
  - `vip dev-env envvar get-all --slug=<slug>`
- Correct a bad variable name:
  - `vip dev-env envvar set --slug=<slug> API_TOKEN my-value`
- Delete and recreate a variable cleanly:
  - `vip dev-env envvar delete --slug=<slug> API_TOKEN`
  - `vip dev-env envvar set --slug=<slug> API_TOKEN my-value`
- Restart so the new value takes effect:
  - `vip dev-env start --slug=<slug>`