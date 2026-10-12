# gh-cli

> Prepare or execute GitHub CLI operations with the intended payload, destination, and verified outcome.

This skill prevents successful commands from producing wrong content, targeting the wrong comment surface, or reporting incomplete reads as exhaustive results. It covers field interpretation, supported body transport, methods, root-comment selection for review replies, REST and GraphQL pagination, and persisted result verification.

It distinguishes prepared commands, verified operations, incomplete attempts, and blockers. Failure handling preserves uncertainty and requires reconciliation before retrying a potentially committed write. Plain Git operations, general destructive-action review, workflow authoring, and API design are outside its scope.

The core contains the normal workflow, failure branches, completion gates, and five `GH` result fields. The reference provides optional command and report examples with authoritative sources. Static checks and instruction audits do not establish actual GitHub outcomes or measured model compatibility.

## Files

- [`SKILL.md`](SKILL.md) — workflow, decision rules, failure handling, output contract, and completion checklist.
- [`references/command-examples.md`](references/command-examples.md) — transport, reply/edit, pagination, and result examples; CLI and endpoint sources.
