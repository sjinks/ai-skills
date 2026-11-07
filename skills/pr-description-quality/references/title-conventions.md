Read when Title is requested to select title conventions and check title fidelity.

# Title conventions

Apply explicit caller rules, then readable repository requirements, then consistent supplied history, then defaults. Record convention evidence or assumptions. Read configuration as text; do not execute it. Known required but unavailable definitions use BLOCK. Do not require Body or discover body templates for title-only work.

## Convention selection

Without a caller/repository convention rule, inspect all readable nonempty supplied historical PR titles, excluding the current draft. Select conventional mode only when strictly more than half match the conventional grammar below. A tie, minority or no usable history selects plain imperative mode. Do not cherry-pick history. Missing repository files do not discard usable supplied history.

These grammar and type policies are house defaults, not claims about every valid Conventional Commits implementation. Caller/repository style overrides defaults; disclosure rules remain mandatory.

## Defaults

Use one imperative line describing the primary outcome of the supplied whole change, without a trailing period. Target 72 characters; exceeding that default passes with a note. A required repository length limit overrides the target.

In conventional mode, use a lowercase type from feat/fix/docs/style/refactor/perf/test/build/ci/chore/revert, optional scope of comma-separated `[a-z0-9][a-z0-9-]*` tokens without spaces, optional `!`, then exactly `: ` and a description starting lowercase unless a proper noun/acronym.

Choose type by the stated primary user-visible or maintenance outcome, not commit/file counts. If multiple types remain equally primary, choose the first applicable type in this order: feat, fix, perf, refactor, docs, test, build, ci, style, chore, revert. Higher-precedence type-selection rules override this tie order.

Confirmed breaking changes require `!` in conventional mode and concrete disclosure when Body is requested. A supplied `!` with unknown breaking intent needs author input for the affected requested parts. If evidence establishes no breaking change, rewrite removes the unsupported marker; validate reports it. For title-only work, note an evidenced body-disclosure follow-up under Input/information without assessing or demanding Body.

A passing title over the default target uses `pass (length: N chars, over 72)`. Exceeding a required limit fails. Explain a different selected target in Findings.

## Sources

- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) — background for type/scope and breaking notation; the exact defaults are defined above.
