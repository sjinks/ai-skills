# single-pass-review-completeness

> Use when: making one review round complete instead of incremental, enumerating review dimensions up front, sweeping a whole diff per dimension, declaring review coverage and uncovered dimensions, or preventing new findings on unchanged code in later review rounds.

This skill is aimed at review rounds that should be the only round, preventing the incremental-review pattern where new findings keep appearing on unchanged code.

It helps an assistant:

- lock the diff under review and enumerate eight dimensions (correctness, contracts, security, concurrency and state, performance, tests, maintainability, operability) before reporting anything
- sweep dimension by dimension across the whole diff and tag every finding with its dimension
- declare each dimension `swept`, justified `skipped`, or `n/a`, and surface uncovered file–dimension pairs as explicit coverage gaps
- keep pre-existing issues outside the locked diff separate from pass findings
- return `COMPLETE-PASS`, `PARTIAL-PASS`, or `BLOCK` with the coverage declaration table and an explicit no-findings path

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
