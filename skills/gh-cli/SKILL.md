---
name: gh-cli
description: "Use when: scripting or running GitHub CLI (`gh`) commands — especially `gh api` calls, posting or editing PR/issue comments and review-thread replies, passing multi-line or special-character bodies, choosing `-f` vs `-F` fields, pagination, jq filtering, and avoiding silent wrong-output from quoting or stdin mistakes."
argument-hint: "Describe the gh task (e.g. reply to a PR review comment, query the API, edit a comment) and any body text."
user-invocable: true
---

# GitHub CLI (gh)

Use this skill when composing or running `gh` commands and the question is whether the command will produce the intended result — not merely whether it is safe. The most common failure mode is a command that runs successfully (exit 0) but posts wrong content: literal `@-`, an unexpanded variable, or mangled multi-line text.

**UTILITY SKILL.** INVOKES: terminal `gh` execution and read-only inspection of `gh` output. FOR SINGLE OPERATIONS: use to pick the right `gh api` field flag, format a comment body, reply to a review thread, or query the API with jq.

## Scope

- `gh api` field flags (`-f`/`--raw-field` vs `-F`/`--field`), request bodies, methods, pagination, and jq filtering.
- Posting and editing PR/issue comments, review-thread replies, and review submissions.
- Passing multi-line or special-character text (commit-message-like bodies, markdown) safely.
- `gh pr`/`gh issue`/`gh release` flags where `--body`/`--body-file` and quoting matter.

## DO NOT USE FOR:

- Git (not `gh`) operations like `git commit`/`git push`/`git rebase` — those are plain git.
- Destructive-command safety review in general (deletions, force-push) — that is a separate safety concern; this skill is about getting `gh` output correct.
- GitHub Actions workflow authoring or REST/GraphQL API design beyond invoking it through `gh`.

## Core Rules

The Checklist is the gating source of truth; these rules explain why.

- **`-f` sends the value literally; `-F` interprets it.** `gh api -f body=@x` posts the literal string `@x`. The `@file` / `@-` (stdin) and typed conventions (`true`, `false`, numbers, `null`) only work with `-F`/`--field`. To read a body from stdin: `... -F body=@-`. To send a literal string that must not be interpreted (e.g. text starting with `@`, or a value that looks like a number/bool you want kept as a string): use `-f`.
- **Prefer a here-doc or file for any body with newlines, quotes, backticks, `$`, or `!`.** Build the text once and pass it via stdin or a file, not inline in double quotes. Inline double-quoted bodies break on embedded `"`, undergo `$`/backtick expansion, and history-expand `!` in interactive shells.
- **Posting a comment body:**
  - One-liner, no special chars: `gh api .../comments -f body='single-quoted literal'` (single quotes prevent expansion; fails only if the text itself contains a single quote).
  - Multi-line or special chars: `printf '%s' "$body" | gh api .../comments -F body=@-`, or `gh ... --body-file file` / `gh ... --body-file -` where the subcommand supports it.
- **Replying to a PR review-thread comment** (threaded under an inline review comment) requires the dedicated replies endpoint: `POST /repos/{owner}/{repo}/pulls/{pr}/comments/{comment_id}/replies` with `-f body=...`. Posting to `/pulls/{pr}/comments` with `in_reply_to` also works; a top-level issue comment (`gh pr comment`) does NOT thread under the review.
- **Fixing a botched comment:** edit in place instead of posting a duplicate — `gh api --method PATCH /repos/{owner}/{repo}/pulls/comments/{comment_id} -f body='...'` (review comments) or `.../issues/comments/{id}` (issue comments).
- **Reading data:** use `--jq '<filter>'` to filter inline and `--paginate` for lists that exceed one page (the default page size silently truncates). `gh api` is REST; use `gh api graphql -f query='...'` for GraphQL.
- **Restate the resolved body before sending.** Expand variables, command substitutions, and confirm quoting in your reply so a wrong body is caught before it posts.

## Workflow

1. Identify the operation: read (query) or write (comment/edit/reply/create).
2. For writes, determine the body's content class: plain one-liner vs multi-line/special-character.
3. Choose the flag: `-f` for a literal string field; `-F` only when you need stdin (`@-`), a file (`@file`), or a typed value.
4. Choose the endpoint: review-thread reply vs top-level comment vs PATCH-to-edit.
5. Build the body via single-quoted literal, here-doc, or `printf | -F body=@-`.
6. Run, then verify the posted result (re-read the comment/field) when the body had any special characters.

## Checklist

- The field flag matches intent: `-f` for literal strings; `-F` only for `@-`/`@file`/typed values. No `@-` or `@file` passed to `-f`.
- Any body with newlines/quotes/backticks/`$`/`!` is passed via stdin (`-F body=@-`) or `--body-file`, not inline double quotes.
- Review-thread replies use the `/comments/{id}/replies` endpoint (or `in_reply_to`), not `gh pr comment`.
- A correction edits the existing comment via `PATCH`, not a new duplicate comment.
- List reads use `--paginate`; filtered reads use `--jq`.
- The resolved body is restated/verified before or after sending when it contains special characters.

## Examples

- Reply to a review comment from stdin (the reply endpoint includes the PR number; stdin handles markdown/backticks safely):

  ```sh
  printf '%s' 'Fixed in abc1234. See `foo()`.' | gh api repos/O/R/pulls/66/comments/123/replies -F body=@-
  ```

- Literal string that starts with `@` (must not be a file ref): `gh api ... -f body='@here is the note'`.
- Edit a wrong review comment in place instead of duplicating (the PATCH endpoint takes no PR number): `gh api --method PATCH repos/O/R/pulls/comments/123 -f body='corrected text'`.
- Paginated, filtered query: `gh api --paginate repos/O/R/pulls/66/comments --jq '.[] | {id, path, line, body}'`.
- Multi-paragraph PR body without quoting pain: `gh pr create --title T --body-file body.md` (or `--body-file -` for stdin).

## Anti-Patterns

- `gh api -f body=@-` (posts literal `@-`; use `-F body=@-`).
- Inline `-f body="...$VAR...`...`..."` with backticks/`$`/embedded quotes (expansion and breakage; use stdin or `--body-file`).
- `gh pr comment` to answer an inline review thread (does not thread; use the replies endpoint).
- Posting a second comment to correct a typo instead of `PATCH`-editing the first.
- A list query with no `--paginate`, then concluding "no results exist" from a truncated page.

## Definition Of Done

A `gh` command is ready only when:

- The field flag (`-f`/`-F`) matches whether the value is a literal string or a stdin/file/typed value.
- Any special-character body is delivered via stdin or a file, and the resolved content is restated or re-read.
- The endpoint matches the intent (review reply vs comment vs PATCH edit), and list reads paginate.
