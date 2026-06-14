Read this when you need to judge how trustworthy a piece of guidance is, or to find the authoritative source to verify a command, default, or error string before acting.

# Source map and confidence

## Confidence levels

- High: command shapes, targeting rules (`--slug` vs `@app.env`), and error strings that match current VIP-CLI output and official VIP/Docker docs.
- Medium: triage heuristics, false-positive patterns, and escalation flows derived from observed support cases; verify against live CLI output before relying on them.
- Low / time-sensitive: specific version numbers (Docker minimums, Node LTS), upstream Docker regression links, and image-tag support. Re-check against the live sources below before quoting them.

## Verify-before-quote items

- Exact CLI error strings and `--help` option shapes: run `vip dev-env <command> --help` against the installed VIP-CLI; CLI wording can change between releases.
- Supported PHP/WordPress versions and Docker minimum version: confirm against the official requirements page rather than memory.
- Log and config file paths (for example `~/.local/share/vip/lando/...`): confirm on the user's platform; paths differ across OS and VIP-CLI versions.

## Authoritative sources

- `https://docs.wpvip.com/vip-local-development-environment/` — LDE overview and requirements.
- `https://docs.wpvip.com/vip-cli/` — VIP-CLI command reference.
- `https://docs.wpvip.com/vip-cli/commands/` — per-command syntax, options, and defaults.
- `https://docs.wpvip.com/vip-cli/target-environments/` — `@app.env` vs local slug-based targeting rules.
- `https://docs.wpvip.com/vip-local-development-environment/troubleshooting-dev-env/` — upstream LDE troubleshooting.
- `https://docs.wpvip.com/vip-cli/troubleshooting/` — upstream VIP-CLI troubleshooting.
- `https://docs.docker.com/engine/daemon/troubleshoot/` — Docker daemon diagnostics.
- `https://docs.docker.com/engine/install/linux-postinstall/` — Linux daemon permissions and non-root usage.
- `https://docs.docker.com/config/containers/logging/configure/` — log-driver and rotation behavior.
