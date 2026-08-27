# Source Map

Read this when you need to understand where the shell-safety rules came from and which claims are guidance versus locally enforced policy.

## Source Confidence

- Shell quoting, expansion, heredoc, `set`, and pipeline behavior: high confidence from POSIX shell behavior plus bash and zsh manuals.
- Git command-risk guidance: high confidence from git command semantics for commit-message options, destructive working-tree operations, branch deletion, and force push behavior.
- Filesystem, process, archive, SSH, cloud, IaC, container, database, service-control, and secret-handling rules: policy guidance derived from common incident classes and safe-operations practice. Treat these as conservative assistant-side guardrails, not a substitute for organization-specific production change policy.
- Tool-specific recommendations can change. For high-impact production mutations, verify the current vendor documentation and the exact target environment before authorizing the command.

## Provenance Notes

- The skill is intentionally command-centric: it reviews one command, script fragment, or proposed terminal action before execution.
- The pattern IDs are local stable labels for reporting and eval assertions; they are not external standards identifiers.
- Confirmation gates are scoped to the normalized command, working directory, interpreter, resolved non-secret expansions, authenticated identity, platform/repository context, target identifiers, reviewed preview or plan digest, and relevant branch tips or object versions. Refresh mutable evidence immediately before execution; any changed or unverifiable binding requires reclassification.