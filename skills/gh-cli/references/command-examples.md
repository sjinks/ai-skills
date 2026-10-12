Read this reference when adapting a transport, reply/edit, pagination, or result example, or verifying flag and endpoint behavior. The core owns all decision rules; examples do not add execution authority.

# Command examples

Shell examples use POSIX `sh` syntax. Replace `O`, `R`, numeric IDs, and local paths with resolved task values. Commands that write to GitHub are illustrations, not requests to execute them. Use installed subcommand help to confirm available flags.

## Literal text versus references

These requests deliberately deliver different content:

```sh
# The requested body is literally the two characters @-.
gh api --method POST repos/O/R/issues/66/comments -f 'body=@-'

# The requested body is the exact text already stored in body.md.
gh api --method POST repos/O/R/issues/66/comments -F 'body=@body.md'

# body is already populated with the intended text; printf adds no newline.
printf '%s' "$body" | gh api --method POST repos/O/R/issues/66/comments -F 'body=@-'
```

Use the same literal-string distinction for text such as `@file`, `true`, `null`, or `123`. For a typed Boolean parameter, `-F enabled=true` expresses a different intent from the string `-f enabled=true`.

## Special-character payloads

This example deliberately stores a terminal LF. The quoted delimiter preserves the apostrophe, backticks, dollar sign, and exclamation mark as literal body text. Choose a delimiter absent from the intended body; preserve an existing exact-byte file when different newline behavior is required.

```sh
cat > body.md <<'GH_BODY'
I've updated `foo()`.

The literal example is $HOME, not an expansion!
GH_BODY
gh api --method POST repos/O/R/pulls/66/comments/123/replies -F 'body=@body.md'
```

For that reply, `123` must already be resolved as the thread's top-level review-comment ID. If a supplied comment has `in_reply_to_id`, inspect that parent and establish the root before constructing the write. Never substitute `gh pr comment` for this destination.

For a top-level PR conversation comment, a supporting subcommand offers another transport:

```sh
gh pr comment 66 --repo O/R --body-file body.md
```

`gh api --body-file body.md` is invalid. API fields read text using `-F`; `--input` instead sends a preconstructed request body such as JSON, rather than wrapping arbitrary Markdown in a `body` field. When using `--input`, field flags go into the query string; set the required method explicitly and inspect the prepared request structure.

## Correct an existing comment

```sh
# Review comment: the edit endpoint has no PR number.
gh api --method PATCH repos/O/R/pulls/comments/123 -F 'body=@body.md'

# Issue/PR conversation comment: use its issue-comment ID.
gh api --method PATCH repos/O/R/issues/comments/456 -F 'body=@body.md'
```

For every write example, compare the returned object or read-back with the intended resource and exact body. For replies, also check the parent relationship. If the result cannot be verified, use `INCOMPLETE`; a local preview does not establish persistence.

## Reads with parameters and pagination

```sh
# Fields on a REST read need an explicit GET method.
gh api --method GET --paginate repos/O/R/issues -f state=open --jq '.[] | {number, title}'

# Each REST page is an array; --slurp adds an outer array for a global count.
gh api --paginate --slurp repos/O/R/pulls/66/comments | jq '[.[][]] | length'
```

`--jq` filters each page; external `jq` aggregates the slurped pages. `--slurp` cannot be combined with `--jq` or `--template`. The aggregation pipeline requires external `jq`; confirm that it is installed. A successful final filter does not prove the preceding `gh` command succeeded: verify both stages and page completion before reporting a count or treating an empty result as evidence of absence. For explicitly bounded reads, report that scope and do not describe it as exhaustive.

```sh
gh api graphql --paginate -f owner=O -f name=R -f query='
query($owner: String!, $name: String!, $endCursor: String) {
  repository(owner: $owner, name: $name) {
    issues(first: 100, after: $endCursor) {
      nodes { number title }
      pageInfo { hasNextPage endCursor }
    }
  }
}'
```

GraphQL pages are objects. Inspect `errors` and cursor/page completion before claiming success. Do not reuse the REST array aggregation filter for GraphQL objects.

## Complete result examples

Illustrative preparation-only result:

```text
GH operation: Read all open issues
GH target: github.com, O/R, issues
GH status: PREPARED
GH evidence: gh api --method GET --paginate repos/O/R/issues -f state=open
GH limitation: None
```

Illustrative result after a verified reply; the ID and observation describe a hypothetical execution, not evidence from this package:

```text
GH operation: Reply to review comment 123
GH target: github.com, O/R, PR 66, root review comment 123
GH status: VERIFIED
GH evidence: Returned comment 789 has the intended body, PR target, and in_reply_to_id 123
GH limitation: None
```

Illustrative uncertain-write result:

```text
GH operation: Reply to review comment 123
GH target: github.com, O/R, PR 66, root review comment 123
GH status: INCOMPLETE
GH evidence: Request timed out; destination inspection also failed; no retry attempted
GH limitation: Commit outcome unknown; inspect destination state before considering a retry
```

Illustrative missing-target result:

```text
GH operation: Reply to a review thread
GH target: Unresolved
GH status: BLOCKED
GH evidence: None
GH limitation: Provide the repository, PR, and review-comment ID
```

## Sources

- [GitHub CLI API manual](https://cli.github.com/manual/gh_api): methods, field conversion, placeholder expansion, stdin/files, raw request bodies, pagination, and page aggregation. Inspect installed `gh api --help` for version-specific support.
- [GitHub CLI API command implementation](https://github.com/cli/cli/blob/trunk/pkg/cmd/api/api.go): incompatible output flags and the external `jq` aggregation example.
- [Review comment endpoints](https://docs.github.com/en/rest/pulls/comments): root-comment reply restriction, reply parent fields, and review-comment updates.
- [Issue comment endpoints](https://docs.github.com/en/rest/issues/comments#update-an-issue-comment): issue/PR conversation-comment updates.
- [PR comment manual](https://cli.github.com/manual/gh_pr_comment): top-level comments and supported body-file transport.
- [POSIX shell command language](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html#tag_19_07_04): quoted heredoc delimiter and newline behavior.
