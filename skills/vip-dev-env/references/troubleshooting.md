Read this when the environment fails to start, is unstable, or services return errors.

# Troubleshooting VIP Local Development Environment

Before running commands
- Ask for `--slug` and the primary symptom first.
- Ask what changed last (VIP-CLI update, Docker update, repo switch, config change).
- Remind users to avoid sharing secrets from logs or SQL dumps.
- Apply security controls from `references/security.md` before risky actions.

## Incident intake template

- Slug: `<slug>`
- Primary symptom: startup failure | HTTP 500 | domain/DNS | DB sync/import | code not reflected
- What changed last: CLI/Docker/Node update, repo switch, config change, or unknown
- Scope and urgency: one env or several envs, blocking release/testing or not
- Available artifacts: sanitized logs, error snippet, last command output

## Error index (fast routing)

| Exact message (or prefix) | First fix command | Deep section |
| --- | --- | --- |
| `Environment doesn't exist.` / `Environment not found.` | `vip dev-env list` | Error-driven fixes 1 |
| `More than one environment found:` | `vip dev-env list` | Error-driven fixes 2 |
| `This command does not support @app.env notation.` | `vip dev-env <command> --slug=<slug>` | Error-driven fixes 3 |
| `docker binary could not be located!` / `Failed to connect to Docker.` | `docker --version` | Error-driven fixes 4 |
| `A double dash ("--") must separate...` | `vip dev-env exec --slug=<slug> -- wp option get home` | Error-driven fixes 5 |
| `A WP-CLI command can only be executed on a running local environment.` | `vip dev-env start --slug=<slug>` | Error-driven fixes 6 |
| `Service '<name>' not found.` | `vip dev-env info --slug=<slug>` | Error-driven fixes 7 |
| `Configuration file ... could not be loaded` | `vip dev-env create --slug=<slug>` | Error-driven fixes 8 |
| `Unknown or unsupported PHP version:` | `vip dev-env create --slug=<slug>` | Error-driven fixes 9 |
| `Provided path "..." does not point to a valid or existing directory.` | `vip dev-env update --app-code=/absolute/path --slug=<slug>` | Error-driven fixes 10 |
| `Environment already exists.` / `Environment already exists` | `vip dev-env start --slug=<slug>` | Error-driven fixes 16 |
| `There was an error reading file ".../instance.json"` | `vip dev-env destroy --soft --slug=<slug>` | Error-driven fixes 17 |
| `There was an error parsing file ".../instance.json"` | `vip dev-env destroy --soft --slug=<slug>` | Error-driven fixes 18 |
| `The provided path does not exist or it is not valid` | `vip dev-env import media /absolute/path --slug=<slug>` | Error-driven fixes 19 |
| `No environments to purge!` | `vip dev-env list` | Error-driven fixes 20 |
| `The provided file ... does not exist or it is not valid` | `vip dev-env import sql /absolute/path/file.sql --slug=<slug>` | Error-driven fixes 15 |
| `The environment variable "<NAME>" does not exist` | `vip dev-env envvar list --slug=<slug>` | Error-driven fixes 13 |
| `Error importing SQL file:` | `vip dev-env logs --service=database --slug=<slug> --follow` | Error-driven fixes 21 |
| `Error exporting SQL backup:` | `vip @<app>.<env> dev-env sync sql --slug=<slug> --table=<table>` | Error-driven fixes 22 |
| `No local environments found.` | `vip dev-env create --slug=<slug>` | Error-driven fixes 23 |
| `Interactive confirmation blocked automation` | `vip dev-env purge --force` (removes ALL local envs and their DB/runtime state; use `vip dev-env purge --soft --force` to keep configs) | Error-driven fixes 24 |

## Command-family matrix (primary plus fallback)

| Command family | Primary error signal | First fix command | Fallback error signal | Fallback fix command |
| --- | --- | --- | --- | --- |
| `create` | `Environment already exists.` | `vip dev-env start --slug=<slug>` | `Unknown or unsupported PHP version:` | `vip dev-env create --slug=<slug>` |
| `start` | `Environment doesn't exist.` | `vip dev-env create --slug=<slug>` | `Failed to connect to Docker.` | `docker --version` |
| `update` | `Provided path "..." does not point to a valid or existing directory.` | `vip dev-env update --app-code=/absolute/path --slug=<slug>` | `Configuration file ... could not be loaded` | `vip dev-env update --slug=<slug>` |
| `exec` | `A double dash ("--") must separate...` | `vip dev-env exec --slug=<slug> -- wp option get home` | `A WP-CLI command can only be executed on a running local environment.` | `vip dev-env start --slug=<slug>` |
| `shell` | `A double dash ("--") must separate...` | `vip dev-env shell --slug=<slug> -- ls -lha` | `Environment needs to be started first` | `vip dev-env start --slug=<slug>` |
| `logs` | `Service '<name>' not found.` | `vip dev-env info --slug=<slug>` | `More than one environment found:` | `vip dev-env logs --slug=<slug>` |
| `import sql` | `The provided file ... does not exist or it is not valid` | `vip dev-env import sql /absolute/path/file.sql --slug=<slug>` | `Error importing SQL file:` | `vip dev-env logs --service=database --slug=<slug> --follow` |
| `import media` | `The provided path does not exist or it is not valid` | `vip dev-env import media /absolute/path/uploads --slug=<slug>` | `Environment needs to be started first` | `vip dev-env start --slug=<slug>` |
| `sync sql` | `Environment needs to be started first` | `vip dev-env start --slug=<slug>` | `Error exporting SQL backup:` | `vip @<app>.<env> dev-env sync sql --slug=<slug> --table=<table>` |
| `envvar` | `Environment variable name must consist of A-Z, 0-9, or _, and must start with an uppercase letter.` | `vip dev-env envvar set --slug=<slug> API_TOKEN value` | `The environment variable "<NAME>" does not exist` | `vip dev-env envvar list --slug=<slug>` |
| `stop` | `Environment not found.` | `vip dev-env list` | `More than one environment found:` | `vip dev-env stop --slug=<slug>` |
| `destroy` | `Environment doesn't exist.` | `vip dev-env list` | `There was an error parsing file ".../instance.json":` | `vip dev-env destroy --soft --slug=<slug>` |
| `purge` | `No environments to purge!` | `vip dev-env list` | Interactive confirmation blocked automation | `vip dev-env purge --force` (removes ALL local envs and their DB/runtime state; `--soft` keeps configs) |
| `list`/`info` | `No local environments found.` | `vip dev-env create --slug=<slug>` | `Environment doesn't exist.` (on `info`) | `vip dev-env list` |

## Error-driven fixes

Use exact CLI output when available. Start here before broader triage.

1) `Environment doesn't exist.`
- Level: High
- Why: The command is targeting a local env that is missing or addressed incorrectly.
- Controls: Apply controls from `references/security.md`.
- Confirm the target slug with `vip dev-env list`.
- If the command was `vip dev-env stop`, the CLI can also return `Environment not found.`; treat it as the same missing-slug or missing-env condition.
- If the user ran `vip @<app>.<env> dev-env <local-command>`, switch to `vip dev-env <command> --slug=<slug>` unless the command explicitly supports `@app.env`.
- If the env was never created, run `vip dev-env create --slug=<slug>`.

2) `More than one environment found:`
- Level: Medium
- Why: VIP-CLI refused to guess the target when multiple local environments exist.
- Controls: Apply controls from `references/security.md`.
- Re-run every follow-up command with `--slug=<slug>`.
- Use `vip dev-env list` if the correct slug is unknown.

3) `This command does not support @app.env notation. Use '--slug=...'`
- Level: Medium
- Why: The user mixed remote app targeting with a local-only dev-env command.
- Controls: Apply controls from `references/security.md`.
- Replace `vip @<app>.<env> dev-env <command>` (for local-only commands such as `start`, `stop`, `logs`, `exec`, `shell`, and `update`) with `vip dev-env <command> --slug=<slug>`.
- Keep `@<app>.<env>` only for remote-backed flows such as `vip @<app>.<env> dev-env sync sql --slug=<slug>`.

4) `docker binary could not be located!` or `Failed to connect to Docker.`
- Level: High
- Why: LDE lifecycle commands cannot run without a working Docker engine and compose stack.
- Controls: Apply controls from `references/security.md`.
- Verify Docker is installed: `docker --version`.
- Start Docker Desktop or the Docker daemon, then retry the same `vip dev-env` command.
- If compose is the issue, verify Docker Compose v2 is available.

5) `A double dash ("--") must separate...`
- Level: Low
- Why: This is a command syntax error, not an environment failure.
- Controls: Apply controls from `references/security.md`.
- For WP-CLI: `vip dev-env exec --slug=<slug> -- wp option get home`
- For shell commands: `vip dev-env shell --slug=<slug> -- ls -lha`

6) `A WP-CLI command can only be executed on a running local environment.` or `Environment needs to be started first`
- Level: High
- Why: The target containers are down, so exec/import/sync cannot complete safely.
- Controls: Apply controls from `references/security.md`.
- Start the env: `vip dev-env start --slug=<slug>`.
- If start fails, switch to the startup playbook below.
- For SQL import validation, ensure both PHP and database services are running before retrying.

7) `Service '<name>' not found.` or `<tool> is not a known lando task`
- Level: Medium
- Why: The requested service or task does not exist in the current env.
- Controls: Apply controls from `references/security.md`.
- Inspect available services and URLs with `vip dev-env info --slug=<slug>`.
- Retry with a supported service name such as `php`, `nginx`, `database`, or `elasticsearch` when enabled.

8) `Configuration file ... could not be loaded` or `invalid configuration-version key`
- Level: Medium
- Why: `vip-dev-env.yml` parsing or schema validation failed before env actions started.
- Controls: Apply controls from `references/security.md`.
- Ensure the file contains at least:
  - `configuration-version: 1`
  - `slug: <slug>`
- Re-check YAML syntax, then rerun `vip dev-env create` or `vip dev-env update`.

9) `Unknown or unsupported PHP version:` or `Unknown or unsupported WordPress version:`
- Level: Medium
- Why: The requested runtime image tag is not supported by the current VIP-CLI metadata.
- Controls: Apply controls from `references/security.md`.
- Choose a supported version from the interactive prompt or remove the invalid flag and rerun.
- Update VIP-CLI if the desired version should be newly available.

10) `Provided path "..." does not point to a valid or existing directory.`
- Level: Medium
- Why: `--app-code` or `--mu-plugins` points to a path that cannot be mounted.
- Controls: Apply controls from `references/security.md`.
- Replace it with an absolute path to a real local directory.
- Re-run `vip dev-env update --app-code=/absolute/path --slug=<slug>`.

11) `Media redirect domain must be a domain name or an URL`
- Level: Low
- Why: The media redirect option received a boolean-like value instead of a host or URL.
- Controls: Apply controls from `references/security.md`.
- Supply a real domain or URL, or disable it explicitly.

12) `Environment variable name must consist of A-Z, 0-9, or _, and must start with an uppercase letter.`
- Level: Low
- Why: The local envvar name failed client-side validation before any file update happened.
- Controls: Apply controls from `references/security.md`.
- Rename it to an uppercase identifier such as `API_TOKEN` or `FEATURE_FLAG_1`.
- Retry with `vip dev-env envvar set --slug=<slug> NAME VALUE`.

13) `The environment variable "<NAME>" does not exist`
- Level: Low
- Why: The selected variable was not found in the local `.env` file.
- Controls: Apply controls from `references/security.md`.
- Verify the name with `vip dev-env envvar list --slug=<slug>`.
- Recreate it with `vip dev-env envvar set --slug=<slug> <NAME> <VALUE>` if needed.

14) `There are no environment variables`
- Level: Low
- Why: The local `.env` file contains no active entries for the selected slug.
- Controls: Apply controls from `references/security.md`.
- Initialize the first variable with `vip dev-env envvar set --slug=<slug> MY_VARIABLE MY_VALUE`.

15) `The provided file ... does not exist or it is not valid (see "--help" for examples)`
- Level: Medium
- Why: A local import or file-based operation was pointed at a missing or invalid path.
- Controls: Apply controls from `references/security.md`.
- Verify the file path exists and is readable.
- Prefer an absolute path before retrying the import or file-based command.

16) `Environment already exists.` or `Environment already exists`
- Level: Low
- Why: The requested create action is redundant because the slug already has local environment state.
- Controls: Apply controls from `references/security.md`.
- Start existing env: `vip dev-env start --slug=<slug>`.
- If configuration changed, apply update: `vip dev-env update --slug=<slug>`.
- Only destroy/recreate when intentionally resetting local state.

17) `There was an error reading file ".../instance.json": ...`
- Level: Medium
- Why: VIP-CLI could not read local environment metadata from disk.
- Controls: Apply controls from `references/security.md`.
- Verify slug path exists and permissions are valid.
- If the file is irrecoverable, preserve config and reset runtime state with `vip dev-env destroy --soft --slug=<slug>`.
- Recreate or start again after metadata recovery.

18) `There was an error parsing file ".../instance.json": ... You may need to recreate the environment.`
- Level: High
- Why: Local environment metadata is corrupted and cannot be parsed safely.
- Controls: Apply controls from `references/security.md`.
- Capture a backup copy of the broken metadata for debugging.
- Rebuild with `vip dev-env destroy --soft --slug=<slug>` and then `vip dev-env create --slug=<slug>`.
- Re-apply local customizations and retry start.

19) `The provided path does not exist or it is not valid (see "--help" for examples)`
- Level: Medium
- Why: A local directory path argument (for example media import source) is missing or invalid.
- Controls: Apply controls from `references/security.md`.
- Use an absolute path to an existing local directory.
- Retry: `vip dev-env import media /absolute/path/uploads --slug=<slug>`.

20) `No environments to purge!`
- Level: Low
- Why: Purge found nothing locally, so there is no runtime state to clean up.
- Controls: Apply controls from `references/security.md`.
- Stop purge flow and create/start the target slug if needed.
- Confirm current local state with `vip dev-env list`.

21) `Error importing SQL file:`
- Level: High
- Why: SQL import failed during local apply, usually due to service health or runtime state.
- Controls: Apply controls from `references/security.md`.
- Check DB service logs: `vip dev-env logs --service=database --slug=<slug> --follow`.
- Ensure the environment is started before retrying: `vip dev-env start --slug=<slug>`.
- Retry import only after database service health is confirmed.

22) `Error exporting SQL backup:`
- Level: High
- Why: Remote export failed before local apply, so sync cannot safely continue.
- Controls: Apply controls from `references/security.md`.
- Retry with narrower scope: `vip @<app>.<env> dev-env sync sql --slug=<slug> --table=<table>`.
- Re-run with sanitized debug output if failure repeats.

23) `No local environments found.`
- Level: Low
- Why: The command requires local environment state, but none exists yet.
- Controls: Apply controls from `references/security.md`.
- Create a local environment: `vip dev-env create --slug=<slug>`.
- Verify local state with `vip dev-env list`.

24) `Interactive confirmation blocked automation`
- Level: High
- Why: The blocked command is `purge`, which removes ALL local environments and their DB/runtime state; bypassing the prompt with `--force` makes this irreversible mass cleanup.
- Controls: Apply controls from `references/security.md`.
- Confirm scope first with `vip dev-env list`, and back up any local data you need.
- To keep configs and remove only runtime state, prefer `vip dev-env purge --soft --force`.
- Only use the full non-interactive form `vip dev-env purge --force` after confirming the data impact.

## Quick triage (symptom first)

Severity legend used in this file:
- High: blocks startup, data workflows, or active validation.
- Medium: partially blocks workflow but usually has safe workarounds.
- Low: command-shape, syntax, or local-config issues with limited impact and a quick fix.

1) Environment does not start
- Level: High
- Why: Startup failures block all local validation and development.
- Controls: Apply controls from `references/security.md`.
- Before deep Docker diagnosis, run quick eliminations from [Known Docker false positives](#known-docker-false-positives-avoid-unnecessary-escalations).
- Run baseline checks and start with debug.
- Then inspect service logs and Docker health.

2) Site responds with HTTP 500
- Level: High
- Why: Server-side failures block normal site behavior and can indicate broader breakage.
- Controls: Apply controls from `references/security.md`.
- Check PHP logs first, then NGINX, then recent code/config changes.

3) Domain/DNS does not resolve or opens wrong env
- Level: Medium
- Why: Routing issues usually do not damage data but can block access.
- Controls: Apply controls from `references/security.md`.
- Validate false-positive cases in [Known Docker false positives](#known-docker-false-positives-avoid-unnecessary-escalations) before daemon/network escalation.
- Validate `bindAddress`, domain pattern, and hosts/DNS entries.

4) DB sync/import problems
- Level: High
- Why: Sync/import actions can overwrite local data and require guarded execution.
- Controls: Apply controls from `references/security.md`.
- Backup local DB first, then retry with a targeted command.

5) App code changes are not reflected
- Level: Medium
- Why: Mount or branch issues are disruptive but typically reversible.
- Controls: Apply controls from `references/security.md`.
- Confirm this is not a targeting/syntax issue from [Known Docker false positives](#known-docker-false-positives-avoid-unnecessary-escalations).
- Confirm `--app-code` path and branch/worktree state.

## Baseline checks (run for most incidents)

- Version snapshot (run each independently so one missing tool does not skip the rest):
  - `vip -v || true`
  - `node -v || true`
  - `npm -v || true`
  - `docker --version || true`
- Compose snapshot (run both; the standalone v1 binary may be absent):
  - `docker compose version || true`
  - `docker-compose version || true`
- Update VIP-CLI if outdated:
  - `npm install -g @automattic/vip`
- Use latest active Node.js LTS.
- Use a current Docker version; outdated versions can break `docker.sock`. Confirm the minimum against the official requirements page (linked below) rather than a hard-coded value.
- If `DOCKER COMPOSE` and `COMPOSE PLUGIN` differ, treat this as a compatibility signal and prefer the Docker plugin path (`docker compose`) during diagnostics.
- Stop other local stacks that can occupy common ports.
- Restart the local machine when Docker/network changes were recently applied.
- Check platform health for suspected external issues:
  - `https://wpvipstatus.com/`
- Reconfirm prerequisites with official docs when local setup looks inconsistent:
  - `https://docs.wpvip.com/vip-local-development-environment/requirements/`

## Docker quick-check (10-second triage)

Use this table before the full Docker playbook when the first signal mentions Docker, daemon, socket, compose, or container startup.
If escalation is needed, use `Escalation bundle (fast copy variant)` for urgent triage and `Escalation bundle command pack (single run)` for complete handoff evidence.

### Operator checklist (one-screen)

1) Run `60-second triage macro` to capture first-pass evidence.
2) Capture `COMMAND LOG FILE` path and `tail -n 120` excerpt.
3) Choose one targeted Docker branch (Step 1, 2, 5, 6, or 8).
4) Score confidence using `Confidence scoring for escalation decisions`.
5) Escalate with `fast` or `full` bundle based on urgency and evidence quality.

### 60-second triage macro

Use this when you need a fast first-pass packet before choosing a Docker branch.
This macro assumes a slug-scoped reproducer: replace `<command>` with a single-environment subcommand that accepts `--slug` (for example `start`), and set `slug` to a known-good slug. Do not pass untrusted or interpolated strings, because the snippet runs `vip` directly in your shell. If the failing command is a global command that does not take `--slug` (`purge`, `stop --all`), run that command separately to capture its error, and still use a slug-scoped command such as `start` here to collect Docker evidence. The log path below is platform- and version-dependent (it differs across macOS, Linux, and WSL2); prefer the `COMMAND LOG FILE` line from the command output and treat this path only as a fallback.

```bash
slug="<slug>"
tmp_out="$(mktemp 2>/dev/null || mktemp -t vip-dev-env)"

vip dev-env <command> --slug="$slug" 2>&1 | tee "$tmp_out" || true

# Parse everything after the label so paths containing spaces (e.g. macOS /Users/First Last/...) survive.
command_log_path="$(grep 'COMMAND LOG FILE' "$tmp_out" | tail -n 1 | sed -E 's/^.*COMMAND LOG FILE[[:space:]:]*//')"
if [ -z "$command_log_path" ]; then
  command_log_path="$(ls -1t ~/.local/share/vip/lando/logs/vip-dev-env-*.log 2>/dev/null | head -n 1)"
fi

echo "command_log_path=${command_log_path:-not-found}"
[ -n "$command_log_path" ] && [ -f "$command_log_path" ] && tail -n 120 "$command_log_path"

docker info || true
docker context ls || true
vip dev-env logs --slug="$slug" || true
```

Use the command output plus command-log excerpt to choose the next branch (Step 1, 2, 5, 6, or 8).

| Symptom or error text | Run first | If this fails | Then jump to |
| --- | --- | --- | --- |
| `docker binary could not be located!` | `docker --version` | Docker not installed or not on PATH | Docker playbook Step 1 |
| `Failed to connect to Docker.` | `docker info` | Daemon/Desktop not reachable | Docker playbook Step 1 |
| `permission denied ... /var/run/docker.sock` | `docker info` | Non-root socket access blocked | Docker playbook Step 2 |
| `Cannot connect to the Docker daemon` | `docker info` | Daemon stopped or wrong context | Docker playbook Step 1 |
| `error during connect` with host mismatch | `echo "$DOCKER_HOST"` and `docker context ls` | Remote/misconfigured Docker host | Docker playbook Step 1 |
| Env starts but URL/service is unreachable | `vip dev-env info --slug=<slug>` | Service healthy mismatch or Docker network issue | Docker playbook Step 6 |
| Import/extract fails with low space signals | `df -h` and `docker system df` | Disk pressure/log growth | Docker playbook Step 5 |
| Unknown Docker-related startup failure | `vip dev-env start --slug=<slug> --debug=@automattic/vip:bin:dev-environment` | No clear root cause from message text | Docker playbook Step 4 |

If failures started right after a Docker upgrade and local branches do not resolve the issue, jump to Docker playbook Step 8 to check upstream known regressions.
If `vip dev-env` output includes `COMMAND LOG FILE`, capture that path immediately and use the referenced log excerpt as primary evidence.

### Stop-and-escalate gate (use early)

Stop local troubleshooting and escalate when any of the following is true:

- The same Docker failure persists after completing Step 1 plus one targeted branch (Step 2, 5, or 6).
- The environment fails immediately after `vip dev-env start --slug=<slug> --debug=@automattic/vip:bin:dev-environment` with no actionable error.
- Daemon-level errors indicate host or Desktop instability that is outside VIP command scope.

Escalation packet (sanitized):

- Exact VIP command and full error text.
- `COMMAND LOG FILE` absolute path from the failing `vip dev-env` output.
- Timestamp-aligned excerpt from that command log file (failure window first).
- Versions, captured independently so one missing tool does not skip the rest: `vip -v || true`, `node -v || true`, `docker --version || true`.
- `docker info` output (redacted if needed).
- Docker diagnostics ID (Desktop) or `journalctl -u docker.service --since "30 min ago"` excerpt (Linux).
- `vip dev-env logs --slug=<slug>` excerpt aligned to failure timestamp.

### Copy-paste escalation template

```text
Docker escalation summary

Issue:
- Command: vip dev-env <command> --slug=<slug>
- First failure time (local): <timestamp>
- Exact error text: <paste>

Environment:
- OS: <linux|macos|windows>
- vip version: <paste output from vip -v>
- node version: <paste output from node -v>
- docker version: <paste output from docker --version>

Checks performed:
- Step 1 (client/daemon reachability): <pass|fail + notes>
- Targeted branch executed: <Step 2|Step 5|Step 6>
- Retry result after remediation: <pass|fail + notes>

Evidence:
- COMMAND LOG FILE path:
<paste>

- COMMAND LOG FILE excerpt near failure:
<paste>

- docker info (sanitized):
<paste>

- Docker diagnostics ID (Desktop) or journal excerpt (Linux):
<paste>

- vip dev-env logs excerpt near failure:
<paste>

Request:
- Need help with next action after baseline + targeted branch did not resolve the issue.
```

### Support ticket output template (ready to paste)

```text
VIP LDE Docker incident handoff

Summary:
- Slug: <slug>
- Failing command: vip dev-env <command> --slug=<slug>
- First failure timestamp: <timestamp>
- Exact error text: <paste>

Primary evidence:
- COMMAND LOG FILE path: <absolute path>
- COMMAND LOG FILE excerpt: <paste>

Environment snapshot:
- OS: <linux|macos|windows>
- vip version: <vip -v>
- node version: <node -v>
- docker version: <docker --version>
- docker context: <paste relevant line from docker context ls>

Troubleshooting performed:
- 60-second triage macro: <completed|not completed>
- Targeted branch: <Step 1|Step 2|Step 5|Step 6|Step 8>
- Retry result: <pass|fail + notes>

Regression assessment:
- Confidence score: <0-7>
- Confidence level: <low|medium|high>
- Upstream issues reviewed:
  - <link 1>
  - <link 2>

Escalation artifacts:
- Bundle type: <fast|full>
- Bundle filename: <vip-docker-escalation-...tar.gz>
- Additional logs attached: <docker-info|vip-dev-env-logs|docker-journal|command-log-tail>

Ask:
- Requested next action from support/engineering.
```

### Escalation bundle command pack (single run)

Choose this when support needs complete diagnostics, or when a fast bundle was insufficient to identify next actions.
This bundle captures local diagnostic metadata and logs, then creates one archive to share after redaction review.

```bash
slug="<slug>"
ts="$(date +%Y%m%d-%H%M%S)"
out_dir="./vip-docker-escalation-${slug}-${ts}"

mkdir -p "$out_dir"

# Prefer the COMMAND LOG FILE path from the failing command output (authoritative, cross-platform).
# Export it first: COMMAND_LOG_FILE="<path from the vip output>". Otherwise fall back to a best-effort
# guess in the common Linux/WSL2 location, which may pick an unrelated newest log or miss on other platforms.
command_log_path="${COMMAND_LOG_FILE:-$(ls -1t ~/.local/share/vip/lando/logs/vip-dev-env-*.log 2>/dev/null | head -n 1)}"

{
  echo "timestamp: $(date +%Y-%m-%dT%H:%M:%S%z)"
  echo "command: vip dev-env <command> --slug=$slug"
  echo "command_log_path: ${command_log_path:-not-found}"
} > "$out_dir/context.txt"

{
  vip -v || true
  node -v || true
  docker --version || true
} > "$out_dir/versions.txt" 2>&1

docker info > "$out_dir/docker-info.txt" 2>&1 || true
docker context ls > "$out_dir/docker-context.txt" 2>&1 || true
docker system df > "$out_dir/docker-system-df.txt" 2>&1 || true
df -h > "$out_dir/df-h.txt" 2>&1 || true

vip dev-env info --slug="$slug" > "$out_dir/vip-dev-env-info.txt" 2>&1 || true
vip dev-env logs --slug="$slug" > "$out_dir/vip-dev-env-logs.txt" 2>&1 || true

if [ -n "$command_log_path" ] && [ -f "$command_log_path" ]; then
  cp "$command_log_path" "$out_dir/command-log-full.log" 2>/dev/null || true
  tail -n 200 "$command_log_path" > "$out_dir/command-log-tail-200.txt" 2>&1 || true
fi

if command -v journalctl >/dev/null 2>&1; then
  journalctl -u docker.service --since "30 min ago" > "$out_dir/docker-journal-30m.txt" 2>&1 || true
fi

tar -czf "${out_dir}.tar.gz" "$out_dir"
echo "Bundle created: ${out_dir}.tar.gz"
echo "Review and redact secrets/tokens before sharing."
```

### Escalation bundle (fast copy variant)

Choose this when incident response is time-sensitive and you need a minimal high-signal packet in under a minute.
It skips optional systemd logs and keeps only the highest-signal files.

```bash
slug="<slug>"
ts="$(date +%Y%m%d-%H%M%S)"
out_dir="./vip-docker-escalation-fast-${slug}-${ts}"

mkdir -p "$out_dir"

# Prefer the authoritative COMMAND LOG FILE path: export COMMAND_LOG_FILE="<path from the vip output>".
# The fallback glob is a best-effort guess for the common Linux/WSL2 location only.
command_log_path="${COMMAND_LOG_FILE:-$(ls -1t ~/.local/share/vip/lando/logs/vip-dev-env-*.log 2>/dev/null | head -n 1)}"

{ vip -v; node -v; docker --version; } > "$out_dir/versions.txt" 2>&1 || true
docker info > "$out_dir/docker-info.txt" 2>&1 || true
vip dev-env info --slug="$slug" > "$out_dir/vip-dev-env-info.txt" 2>&1 || true
vip dev-env logs --slug="$slug" > "$out_dir/vip-dev-env-logs.txt" 2>&1 || true

if [ -n "$command_log_path" ] && [ -f "$command_log_path" ]; then
  tail -n 120 "$command_log_path" > "$out_dir/command-log-tail-120.txt" 2>&1 || true
fi

tar -czf "${out_dir}.tar.gz" "$out_dir"
echo "Bundle created: ${out_dir}.tar.gz"
echo "Review and redact secrets/tokens before sharing."
```

### What to review before sharing

- `docker-info.txt` for registry auth, hostnames, or environment variables.
- `command-log-full.log` and `command-log-tail-*.txt` for tokens, signed URLs, or credentials.
- `vip-dev-env-logs.txt` for API tokens, signed URLs, or local credentials.
- `docker-journal-30m.txt` for network topology details you do not want broadly shared.

### Known Docker false positives (avoid unnecessary escalations)

These signals often look like Docker failures but are usually configuration, targeting, or local command-shape issues.

| Signal | Why it looks like Docker | Quick verification | Actual fix |
| --- | --- | --- | --- |
| `Environment doesn't exist.` | Startup fails before containers appear | `vip dev-env list` | Use the correct slug or create env first |
| `More than one environment found:` | Command appears to target the wrong container stack | `vip dev-env list` | Add `--slug=<slug>` to every command |
| `This command does not support @app.env notation.` | User assumes Docker context is broken | Re-run command with local target form | Replace `@app.env` with `vip dev-env <command> --slug=<slug>` |
| `A double dash ("--") must separate...` | `exec`/`shell` call returns error that looks runtime-related | Check command shape against `references/command-syntax.md` | Use separator correctly: `vip dev-env exec --slug=<slug> -- <cmd>` |
| Site opens wrong content or not at all while env is running | Interpreted as container/network outage | `vip dev-env info --slug=<slug>` then check domain and DNS | Fix bind address/domain/DNS mapping via networking playbook |
| `scan failed ... status code 302` followed by `Setting to good` in command log | Looks like Docker/network startup failure | Check `COMMAND LOG FILE` for both lines, then open the URL and inspect redirect target | Treat as app-level redirect/routing behavior first, not Docker outage |
| `Service '<name>' not found.` | Treated as broken Docker services | Inspect available services in `vip dev-env info --slug=<slug>` | Use valid service name from stack output |

Escalate only after these quick verifications pass and the Docker branches still fail.

## Playbook: Docker troubleshooting decision tree

- Level: High
- Why: VIP local dev environments depend on a healthy Docker daemon, socket, network, and disk state.
- Controls: Apply controls from `references/security.md`.

Use this sequence for any Docker-related signal, then retry the original `vip dev-env` command.

### Step 0: Capture COMMAND LOG FILE from failing VIP output

Do this first whenever available. The command-specific log usually has the cleanest failure context.

1) Run or re-run the failing command and copy the line that starts with `COMMAND LOG FILE`.

2) If the path was missed, find the newest VIP command log under the VIP-CLI data directory (commonly `~/.local/share/vip` on Linux/WSL2; platform/version-dependent) and inspect it:
- `ls -1t ~/.local/share/vip/lando/logs/vip-dev-env-*.log | head -n 1`

3) Attach a short failure-window excerpt to the escalation packet:
- `tail -n 120 <command-log-file-path>`

4) If endpoint issues are suspected, quickly detect redirect false-positive pattern:
- `grep -E "scan failed|status code 302|Setting to good" <command-log-file-path> | tail -n 20`

### Step 1: Confirm client and daemon reachability

1) Verify Docker client exists:
- `docker --version`

2) Verify daemon connectivity:
- `docker info`

3) If `docker info` fails, branch by failure type:
- `Cannot connect to the Docker daemon ...` -> start Docker Desktop or daemon service, then retry.
- `permission denied while trying to connect to the Docker daemon socket` -> follow Step 2 (Linux socket permissions).
- `error during connect` with remote host hints -> check `DOCKER_HOST` and current context:
  - `echo "$DOCKER_HOST"`
  - `docker context ls`
  - Prefer default local context for LDE unless user intentionally configured remote Docker.

### Step 2: Linux socket and permission recovery

Use when Docker is installed but non-root access fails.

1) Check docker group membership:
- `groups`

2) If needed, add user to `docker` group:
- `sudo usermod -aG docker $USER`

3) Re-evaluate session and retest:
- Log out/in (or restart shell session), then run `docker info`.

4) If `~/.docker` permission warnings appear after earlier `sudo` usage, restore ownership to your user and restrict access (the directory can hold client credentials/config, so avoid group/other access):
- `sudo chown -R "$USER":"$USER" ~/.docker`
- `chmod -R u+rwX,go-rwx ~/.docker`

### Step 3: Docker Desktop diagnostics (macOS/Windows)

Use when daemon appears running but startup still fails.

1) Restart Docker Desktop, then retest:
- `docker info`

2) Collect Desktop diagnostics from the UI and save Diagnostics ID for escalation.

3) If errors mention privileged ports or vmnetd, validate Docker Desktop advanced networking settings and retry.

### Step 4: Daemon logs and debug mode

Use when failures persist and message-only fixes are not enough.

1) Enable daemon debug logging temporarily, reproduce once, then collect sanitized logs.

2) Linux daemon logs (systemd):
- `journalctl -u docker.service --since "30 min ago"`

3) If troubleshooting requires stack traces from daemon activity, capture them in a controlled run and redact secrets before sharing.

### Step 5: Container log growth and disk pressure

Use when containers fail unexpectedly, restart-loop, or extraction/import fails with storage signals.

1) Check local disk headroom:
- `df -h`

2) Inspect Docker disk usage:
- `docker system df`

3) Review log growth under default `json-file` driver and apply log rotation policy if needed.

4) Remove only clearly unused artifacts when safe:
- `docker image prune`
- `docker volume prune`
- `docker system prune`

Run destructive cleanup commands only after explicit user confirmation and scope check.

### Step 6: Network and DNS branch for Docker-backed failures

Use when services start but endpoints are unreachable.

1) Verify VIP env endpoint status first:
- `vip dev-env info --slug=<slug>`

2) Confirm local DNS resolution and curl reachability:
- `dig <slug>.vipdev.lndo.site`
- `curl -v -o /dev/null <slug>.vipdev.lndo.site`

3) If `COMMAND LOG FILE` shows `status code 302` plus `Setting to good`, treat this as app redirect behavior first:
- verify redirect target from `curl -I <slug>.vipdev.lndo.site`
- check local app routing/auth/redirect logic before daemon restart.

4) If Docker network errors are reported in daemon/service logs, restart Docker networking stack (Desktop/daemon restart) and retry start.

5) If the failure pattern still matches common command-shape/targeting errors, re-check [Known Docker false positives](#known-docker-false-positives-avoid-unnecessary-escalations) before escalating.

### Step 7: Validate and retry VIP flow

After Docker remediation:

1) Retry the original failing command first.

2) If still failing, run targeted startup debug:
- `vip dev-env start --slug=<slug> --debug=@automattic/vip:bin:dev-environment`

3) Collect escalation packet (sanitized):
- exact VIP error text
- `COMMAND LOG FILE` path and failure-window excerpt
- versions captured independently so one missing tool does not skip the rest: `vip -v || true`, `node -v || true`, `docker --version || true`
- Docker diagnostics ID (Desktop) or daemon log window (Linux)
- `vip dev-env logs --slug=<slug>` excerpt relevant to failure

### Step 8: Check upstream Docker issues for known regressions

Use this step after local checks are complete and before final escalation. It is especially useful right after Docker Desktop or Engine upgrades.

1) Search by component first:
- Docker Desktop: `https://github.com/docker/desktop-feedback/issues`
- Docker Engine: `https://github.com/moby/moby/issues`
- Docker CLI: `https://github.com/docker/cli/issues`
- Docker Compose: `https://github.com/docker/compose/issues`

2) Build targeted queries using version + OS + exact error text. Example patterns:
- `is:issue is:open "Cannot connect to the Docker daemon" "Docker Desktop 4.43" macOS`
- `is:issue is:open "permission denied" "/var/run/docker.sock" Ubuntu 24.04`
- `is:issue is:open "error during connect" "docker context" Windows`

3) Treat an issue as a likely match only when most of these are true:
- Same Docker product and nearby version family.
- Same OS/platform.
- Matching error string and reproduction pattern.
- Recent activity or maintainer acknowledgment.

4) Apply reported workarounds carefully:
- Prefer reversible changes first.
- Avoid destructive cleanup unless explicitly approved and scoped.
- Retry the original `vip dev-env` command immediately after each change.

5) If no strong match is found in 10-15 minutes, stop searching and escalate with the existing packet plus any relevant issue links reviewed.

### Confidence scoring for escalation decisions

Use this scoring after Step 7 or Step 8 to decide whether to continue local troubleshooting or escalate.

| Signal | Score |
| --- | --- |
| Failure started immediately after Docker upgrade | +2 |
| Matching upstream issue with same product + OS + nearby version | +2 |
| Maintainer acknowledgment or linked fix PR in matched issue | +2 |
| Same failure signature repeated in `COMMAND LOG FILE` after retry | +1 |
| `COMMAND LOG FILE` shows `status code 302` and `Setting to good` during URL scan | -1 |
| Failure resolved by local targeting/syntax/config correction | -2 |

Decision thresholds:
- High confidence upstream regression (`score >= 4`): escalate with issue links and full packet.
- Medium confidence (`score 2-3`): run one more targeted local branch, then escalate if unchanged.
- Low confidence (`score <= 1`): prioritize local false-positive checks and Docker branches before escalation.

### Docker error-to-action matrix

| Docker signal | First check | Next action |
| --- | --- | --- |
| `docker binary could not be located!` | `docker --version` | Install Docker Engine/Desktop and retry original VIP command |
| `Failed to connect to Docker.` | `docker info` | Start Docker daemon/Desktop; verify local context |
| `permission denied ... /var/run/docker.sock` | `groups` | Add user to `docker` group, refresh session, retest |
| `Cannot connect to the Docker daemon` | `docker info` | Start/restart daemon, then retry VIP start |
| `error during connect` with host/context mismatch | `echo "$DOCKER_HOST"` and `docker context ls` | Switch back to local/default context for LDE |
| Disk full / extraction failures | `df -h` and `docker system df` | Free space and prune unused Docker artifacts safely |

Official references for this playbook
- `https://docs.docker.com/engine/daemon/troubleshoot/`
- `https://docs.docker.com/engine/install/linux-postinstall/`
- `https://docs.docker.com/config/containers/logging/configure/`

## Playbook: lifecycle command recovery (stop, destroy, purge)

- Level: High
- Why: Lifecycle commands can remove running containers, local DB state, or all local environments.
- Controls: Apply controls from `references/security.md`.

1) Confirm target scope first:
- One env: `vip dev-env info --slug=<slug>`
- All envs: `vip dev-env list`

2) Recover `stop` failures:
- Single env: `vip dev-env stop --slug=<slug>`
- All envs: `vip dev-env stop --all`
- If stop returns `Environment not found.`, verify slug with `vip dev-env list`.

3) Recover `destroy` failures safely:
- Preserve config for rebuild: `vip dev-env destroy --soft --slug=<slug>`
- Full remove (containers, volumes, config files): `vip dev-env destroy --slug=<slug>`
- If destroy returns `Environment doesn't exist.`, verify slug or skip destroy and recreate only when needed.

4) Recover `purge` failures safely:
- Dry decision with prompt: `vip dev-env purge`
- Non-interactive automation: `vip dev-env purge --force`
- Preserve config files while removing runtime state: `vip dev-env purge --soft`
- If output says `No environments to purge!`, stop here and proceed with create/start as needed.

5) After lifecycle action:
- Verify with `vip dev-env list`
- Recreate or restart only required environments.

## Playbook: environment does not start

- Level: High
- Why: Startup failure blocks all local environment use.
- Controls: Apply controls from `references/security.md`.

1) Start with verbose output:
- `vip dev-env start --slug=<slug> --debug=@automattic/vip:bin:dev-environment`

Common start-path failures
- `docker binary could not be located!` -> install Docker first.
- `Failed to connect to Docker.` -> start Docker, then retry.
- `Environment doesn't exist.` -> verify slug or create the env.
- `Environment already exists.` during create -> start the existing env instead of creating again.

2) Inspect logs:
- `vip dev-env logs --slug=<slug>`
- `vip dev-env logs --service=nginx --slug=<slug> --follow`
- `vip dev-env logs --service=php --slug=<slug> --follow`

3) Verify service endpoints:
- `vip dev-env info --slug=<slug>`

4) If still failing, restart Docker Desktop/daemon and retry.
5) If the CLI asks for debug logs, re-run with `--debug=@automattic/vip:bin:dev-environment` and capture only sanitized output.

DOWN-state deep check (from debug scan)
- In debug output, search for `DEBUG ==> scan results`.
- Identify URLs with `status=false`; these are the failing reachability checks.
- If a failing URL shows `ECONNREFUSED`, investigate port conflicts first (other local dev apps, Apache/NGINX/MySQL, proxies/tunnels/security tools).

Known macOS mount race
- If startup returns `WordPress Core files not found` or `Failed opening required '/wp/config/wp-config.php'`:
  - Recreate once: `vip dev-env destroy --soft --slug=<slug>` then `vip dev-env create --slug=<slug>`.
  - If it persists on Docker Desktop/macOS, switch file sharing to VirtioFS and retry start.

## Playbook: HTTP 500

- Level: High
- Why: Runtime application failure can indicate critical app or config errors.
- Controls: Apply controls from `references/security.md`.

1) Tail PHP logs first:
- `vip dev-env logs --service=php --slug=<slug> --follow`

2) Check web server logs:
- `vip dev-env logs --service=nginx --slug=<slug> --follow`

3) Validate app wiring and code state:
- `vip dev-env info --slug=<slug>`
- Confirm the expected local repo path is attached via `--app-code`.

4) If error started after a sync/import, verify URLs and serialized data behavior.
5) If app code was recently rewired, confirm `--app-code` points to a valid absolute directory and rerun `vip dev-env update` if needed.

## Playbook: DNS/domain issues

- Level: Medium
- Why: Access and routing failures are disruptive but generally non-destructive.
- Controls: Apply controls from `references/security.md`.

1) Inspect effective URLs:
- `vip dev-env info --slug=<slug>`

2) Confirm bind address and domain config:
- Check `<vip-data-dir>/lando/config.yml` (commonly under `~/.local/share/vip` on Linux/WSL2; the base path is platform/version-dependent).

3) Ensure hosts/DNS maps each required domain to the configured bind address.
4) If VIP-CLI warns `Failed to resolve <domain>` or `<domain> resolves to <ip> instead of 127.0.0.1`, add the suggested hosts entries or align DNS with `bindAddress`.
5) Recreate env only if domain/base config changed after creation.

DNS and proxy checks
- Validate DNS answer resolves to `127.0.0.1`:
  - macOS/Linux: `dig <slug>.vipdev.lndo.site`
  - Windows: `nslookup <slug>.vipdev.lndo.site`
- Verify HTTP reachability and headers: `curl -v -o /dev/null <slug>.vipdev.lndo.site`
- If curl reaches localhost but browser still fails, investigate local proxies/VPN/security tooling.

Known privileged port mapping failures (Docker Desktop)
- Error pattern 1: `failed to connect to /var/run/com.docker.vmnetd.sock`
- Error pattern 2: `Ports are not available ... not allowed as current user`
- Resolution: enable Docker Desktop advanced setting `Enable privileged port mapping` (toggle off/on if already enabled), then restart the env.

## Playbook: DB sync/import issues

- Level: High
- Why: Data operations may overwrite local state and require explicit safeguards.
- Controls: Apply controls from `references/security.md`.

1) Protect local data first (backup/export) before retrying sync/import.

2) Retry minimal scope:
- `vip @<app>.<env> dev-env sync sql --slug=<slug> --table=<table>`

3) For multisite, verify site targeting:
- `vip @<app>.<env> dev-env sync sql --slug=<slug> --site-id=<id>`

4) Re-test wp-admin and front end after operation.
5) Use exact failure text when available:
- `Error exporting SQL backup:` -> check remote backup/export access and retry.
- `Error extracting the SQL export:` or `Error extracting the SQL file:` -> verify the archive is readable and has disk space for extraction.
- `Error extracting site URLs:` or `Error getting site URLs from SDS:` -> retry the sync after confirming the dump and remote environment metadata are healthy.
- `Error replacing domains:` -> treat as search-replace failure and retry with sanitized debug output.
- `Error importing SQL file:` -> inspect local database service health and retry import once services are up.
- `WARNING: data cleanup failed.` -> the import may still have completed; validate the site, then decide whether cleanup must be rerun manually.

## Playbook: app code not reflected

- Level: Medium
- Why: Code mount and branch state issues impact delivery velocity but are recoverable.
- Controls: Apply controls from `references/security.md`.

1) Verify app code mount path:
- `vip dev-env info --slug=<slug>`
- `vip dev-env update --app-code=/absolute/path/to/repo --slug=<slug>`

2) Restart and retest:
- `vip dev-env start --slug=<slug>`

3) Confirm branch/worktree is correct locally.
4) If update warns that the provided path is invalid, fix the path first because VIP-CLI will ignore the bad `--app-code` value.
5) If update says the env was created before update was supported, destroy and recreate the env after confirming local data impact.

Escalate
- If the above fails, collect sanitized debug output (`--debug`), service logs, OS, Docker version, Node version, and VIP-CLI version before escalating.

## Command syntax quick fixes

- If the error mentions `@app.env notation`, switch to `vip dev-env <command> --slug=<slug>` for local-only commands.
- If the error mentions `A double dash ("--") must separate...`, fix the inner command form first:
  - `vip dev-env exec --slug=<slug> -- wp option get home`
  - `vip dev-env shell --slug=<slug> -- ls -lha`
- If multiple local envs exist, require `--slug=<slug>` on every command, including `logs`, `info`, `exec`, `shell`, and `envvar`.
- For deeper syntax guidance, use `references/command-syntax.md`.

## Copy-paste recovery appendix

Startup and targeting
- `vip dev-env list`
- `vip dev-env info --slug=<slug>`
- `vip dev-env start --slug=<slug> --debug=@automattic/vip:bin:dev-environment`
- `vip dev-env stop --all`
- `vip dev-env destroy --soft --slug=<slug>` (drops one env's runtime/DB state; keeps configs. Omit `--soft` to remove configs too)
- `vip dev-env purge --force` (DESTRUCTIVE: removes ALL local envs and their DB/runtime state; add `--soft` to keep configs. Confirm scope with `vip dev-env list` first)

Logs and services
- `vip dev-env logs --slug=<slug>`
- `vip dev-env logs --service=php --slug=<slug> --follow`
- `vip dev-env logs --service=nginx --slug=<slug> --follow`
- `vip dev-env logs --service=database --slug=<slug> --follow`

Command syntax repairs
- `vip dev-env exec --slug=<slug> -- wp option get home`
- `vip dev-env shell --slug=<slug> -- env | sort`
- `vip @<app>.<env> dev-env sync sql --slug=<slug>`

Envvar recovery
- `vip dev-env envvar list --slug=<slug>`
- `vip dev-env envvar get-all --slug=<slug>`
- `vip dev-env envvar set --slug=<slug> API_TOKEN my-value`
- `vip dev-env start --slug=<slug>`

Database recovery
- `vip @<app>.<env> dev-env sync sql --slug=<slug> --table=wp_posts`
- `vip @<app>.<env> dev-env sync sql --slug=<slug> --site-id=<id>`
