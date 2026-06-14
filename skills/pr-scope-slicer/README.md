# pr-scope-slicer

> Use when: deciding whether a pull request, diff, or change set is too large or mixed to review in one pass, splitting an oversized PR into reviewable slices, separating refactor from behavior change or mechanical from semantic edits, or planning stacked or sequential PRs for a large change.

This skill is aimed at change sets that may be too large or too mixed to review well in one pass, where incremental reviewer discovery would otherwise stretch into many rounds.

It helps an assistant:

- apply explicit, user-overridable size signals (non-mechanical line count, file count, mixed concerns, generated-content mixing) and state which fired
- split along a preferred axis order: mechanical vs semantic, refactor vs behavior, dependency order, subsystem independence, and risk isolation
- keep each slice independently buildable, testable, revertible, and labeled with its review focus and dependencies
- state the tradeoffs of splitting versus not splitting instead of treating splitting as free
- return `SINGLE-PASS-OK`, `SPLIT-RECOMMENDED`, `SPLIT-REQUIRED`, or `BLOCK` with the ordered slice table when a split is called for

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
