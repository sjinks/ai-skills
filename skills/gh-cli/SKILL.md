---
name: gh-cli
description: "Use when: composing or running GitHub CLI commands where field types, body transport, comment destinations, request methods, pagination, or result verification determine correctness. Do not use for plain Git operations, general destructive-action review, workflow authoring, or API design."
argument-hint: "Provide the gh operation, target, intended body or query, and whether to prepare or execute it."
---

# GitHub CLI Correctness

Prepare or execute one `gh` operation that produces the intended payload, destination, and verified outcome. Command correctness does not grant execution authority; follow the caller's authorization and runtime restrictions.

**UTILITY SKILL.** INVOKES: command preparation, terminal `gh` execution, and result inspection. FOR SINGLE OPERATIONS: preserve payload, target, and outcome correctness.

## DO NOT USE FOR:

- Plain Git operations, general destructive-action review, workflow authoring, or API design.

## Workflow

1. Establish preparation versus execution, read versus write, hostname, repository, resource IDs, intended content, and requested read limit. Resolve ambiguous targets before execution. Confirm needed flags with installed subcommand help.
   For `gh api`, pass the resolved hostname with `--hostname`. For other subcommands, use a supported host-qualified target or set `GH_HOST` to the resolved hostname. Do not rely on an ambient default that can disagree with `GH target`.
2. Select the endpoint and method. For REST reads with fields, set `--method GET`; adding fields otherwise selects POST. For REST writes, use the documented endpoint method. GraphQL uses `gh api graphql`; distinguish queries from mutations by their operation, not HTTP method.
3. Select field interpretation by intent: `-f` preserves a string, including literal `@-`, `@file`, `true`, or `123`. Use `-F` for intentional file/stdin references, typed values, or repository placeholders. For API body text from a file/stdin, use `-F body=@PATH` or `-F body=@-`. Use `--body-file` only on a subcommand whose help supports it; `gh api` does not.
4. Prepare the exact payload once. For bodies containing newlines, quotes, backticks, `$`, or `!`, use a file or stdin. Preserve intended bytes, including terminal newlines. Never evaluate literal body text as shell code. Check quoting, expansion intent, argument boundaries, and stdin delivery in the actual shell before submission.
5. Apply Target and completeness rules. For preparation-only requests, return `PREPARED` without execution. Otherwise execute within the caller's authorization, inspect errors, and verify the result: for writes, compare returned-object or read-back target and content with the intended operation; for reads, confirm the requested scope and successful completion before interpreting filtered results or making absence claims. A preview alone does not verify execution.
6. Return the Output fields. Stop when the requested result is verified or a failure branch requires hand-back.

## Target and completeness rules

- For review-thread replies, resolve the top-level review-comment ID. If given a reply, inspect its `in_reply_to_id` and validate the root against the repository and PR. POST to `/repos/{owner}/{repo}/pulls/{pr}/comments/{root_id}/replies`. `gh pr comment` creates a top-level conversation comment.
- For comment corrections, PATCH the existing review comment at `/repos/{owner}/{repo}/pulls/comments/{id}` or issue comment at `/repos/{owner}/{repo}/issues/comments/{id}`; do not create a duplicate.
- For complete REST collection reads, use `--paginate`. For complete GraphQL connection reads, also supply `$endCursor`, `after: $endCursor`, and `pageInfo { hasNextPage endCursor }`. For explicitly bounded reads, preserve and report the requested limit; do not claim exhaustive results. Use `--jq` for per-page filtering. For cross-page aggregation, confirm page shape and external `jq` availability, capture `--paginate --slurp` JSON in a fresh file, run `jq` only after `gh` succeeds, and check `jq`'s status; never combine `--slurp` with `--jq` or `--template`.

## Error handling

If a prerequisite for the requested preparation or execution is unresolved, return `BLOCKED` and name the smallest missing prerequisite. Check intent, target, and needed capabilities; authentication and execution authority are required only for execution. Do not guess a destination or change operation type.

After an attempted operation, command errors, GraphQL `errors`, partial pagination, mismatched results, and unverifiable outcomes require `INCOMPLETE`. Report observed progress and the failed check. For an uncertain write, inspect destination state before retrying. Retry only after confirming the intended result was not committed and execution remains authorized; otherwise stop with uncertainty. Never retry a failed review reply as a top-level comment.

## Output

Return these five fields once, in order. Replace angle-bracket placeholders with actual values. Each value occupies one line; reference an artifact for multiline commands or content.

```text
GH operation: <requested operation>
GH target: <hostname, repository, resource; Unresolved if unknown>
GH status: <PREPARED, VERIFIED, INCOMPLETE, or BLOCKED>
GH evidence: <prepared command or observed result and verification; None if unavailable>
GH limitation: <missing prerequisite, failed check, uncertainty, or None>
```

`PREPARED` means a checked command was supplied directly or by artifact reference without execution. `VERIFIED` means execution produced the requested result with the verification required by Workflow step 5. `INCOMPLETE` means execution was attempted but failed or its requested result is unverified. `BLOCKED` means a prerequisite prevents preparation or execution and no operation was attempted. For either failure status, include the required next action in `GH limitation`. Never include credentials in output.

## Checklist and done

The checklist gates completion:

- For `PREPARED` or `VERIFIED`, intent, supported transport, shell delivery, target, method, and read scope satisfy the workflow and target rules.
- Execution and verification claims match evidence; status matches preparation, success, or the applicable failure branch.
- All five Output fields occur once in order. Stop after returning them.

## Examples and sources

Read [command examples](references/command-examples.md) when adapting body transport, reply/edit commands, paginated queries, result reports, or checking authoritative flag and endpoint sources.
