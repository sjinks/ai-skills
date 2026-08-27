# shell-safety

> Use when: composing or running any shell command in `run_in_terminal`, terminal, bash, zsh, or sh. Covers destructive commands, quoting and expansion hazards, unsafe pipes and redirects, git history mutations, privilege escalation, cloud/IaC/container/database mutations, archive extraction, and secret leakage.

This skill is aimed at preventing data loss, credential disclosure, accidental production changes, and malformed shell invocations before a command is sent to a terminal.

It helps an assistant:

- classify command segments by stable pattern IDs and apply the most restrictive decision gate
- distinguish commands that are `SAFE`, require a `REWRITE`, need exact-target confirmation, are already `AUTHORIZED`, or must be `BLOCKED`
- rewrite fragile or dangerous forms such as `git commit -m` bodies, bare force pushes, network-to-shell pipes, unquoted variables, unsafe globs, and secret-bearing argv
- require preview, identity, target, recovery, and environment checks before destructive operations
- restate exact commands with quoting visible while keeping secret values redacted

It is **not** for portability-only shell reviews, generic shell tutoring, or non-shell languages. Portability concerns are in scope only when they affect whether the proposed command can be executed safely in the current context.

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- [`references/command-construction.md`](references/command-construction.md) — commit messages, quoting, shell construction, secret hygiene, and encoding.
- [`references/host-and-repository-changes.md`](references/host-and-repository-changes.md) — Git, filesystem, processes, privilege, signing, services, and archives.
- [`references/remote-delivery.md`](references/remote-delivery.md) — network-to-shell and SSH delivery safety.
- [`references/platform-and-data-operations.md`](references/platform-and-data-operations.md) — cloud, IaC, container, and database operations.
- [`references/quoting-rules.md`](references/quoting-rules.md) — bash/zsh quoting, expansion, heredoc, and mode details.
- [`references/source-map.md`](references/source-map.md) — provenance and source-confidence notes.