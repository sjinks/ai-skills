# gh-cli

> Use when: scripting or running GitHub CLI (`gh`) commands — especially `gh api` calls, posting or editing PR/issue comments and review-thread replies, passing multi-line or special-character bodies, choosing `-f` vs `-F` fields, pagination, jq filtering, and avoiding silent wrong-output from quoting or stdin mistakes.

This skill targets the failure mode where a `gh` command exits 0 but produces the wrong result — a literal `@-`, an unexpanded variable, mangled multi-line text, or a comment that does not thread under a review.

It helps an assistant:

- choose `gh api -f`/`--raw-field` (literal) vs `-F`/`--field` (stdin `@-`, `@file`, typed values) correctly
- pass multi-line or special-character comment bodies via stdin or `--body-file` instead of fragile inline double quotes
- reply to PR review threads via the `/comments/{id}/replies` endpoint rather than a non-threading top-level comment
- correct a botched comment with a `PATCH` edit instead of a duplicate
- read with `--jq` filtering and `--paginate` so list results are not silently truncated

It is **not** for plain git operations, general destructive-command safety review, or GitHub Actions/API design beyond invoking it through `gh`.

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
