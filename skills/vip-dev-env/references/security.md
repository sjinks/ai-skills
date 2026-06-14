Read this before running risky commands or sharing diagnostic artifacts.

# Security and safe operations for VIP Local Development Environment

## Security defaults

- Keep networking local-first: use `127.0.0.1` unless LAN access is explicitly required.
- Ask for `--slug` before any single-environment modify, sync, destroy, or update command. For global commands that do not take `--slug` (`purge`, `stop --all`), confirm scope with `vip dev-env list` and get explicit confirmation first.
- Use least privilege for each task.
- Treat logs, SQL dumps, and command output as sensitive by default.

## Risk levels and operator behavior

High risk
- Commands that can overwrite or delete local data.
- Commands that expose services to non-local networks.
- Actions that reset index state.
- Required behavior: warn first, confirm intent, recommend backup.

Medium risk
- Commands that restart or reconfigure services.
- Actions that can change routing/domain behavior.
- Required behavior: call out expected impact and rollback path.

Low risk
- Read-only diagnostics such as info/log collection.
- Required behavior: still sanitize output before sharing.

## Sensitive data handling

- Redact tokens, passwords, cookies, email addresses, and personal data from logs.
- Share only relevant log windows, not full unfiltered dumps.
- Avoid posting raw SQL dumps in chat or tickets.

## Destructive actions checklist

1) Confirm scope: the target slug for single-environment commands, or the full set of affected environments (via `vip dev-env list`) for global commands like `purge` and `stop --all`.
2) Confirm user intent and data impact.
3) Take local backup/export when applicable.
4) Execute minimal-scope command first.
5) Validate health after change.

## Network exposure checklist

1) Prefer `bindAddress: 127.0.0.1`.
2) If LAN access is required, prefer specific local IP over `0.0.0.0`.
3) Confirm trusted network context.
4) Verify DNS/hosts maps to the configured bind address.

## Command classes by risk

High
- `vip dev-env destroy --slug=<slug>`
- `vip @<app>.<env> dev-env sync sql --slug=<slug>`
- `vip dev-env exec --slug=<slug> -- wp vip-search index --setup`

Medium
- `vip dev-env update --app-code=/absolute/path --slug=<slug>`
- `vip dev-env start --slug=<slug>` after config changes

Low
- `vip dev-env info --slug=<slug>`
- `vip dev-env logs --slug=<slug>`
