---
name: pr-scope-slicer
description: "Use when: deciding whether a pull request, diff, or change set is too large or mixed to review in one pass, splitting an oversized PR into reviewable slices, separating refactor from behavior change or mechanical from semantic edits, or planning stacked or sequential PRs for a large change."
argument-hint: "Change inventory: files with change sizes, the concerns the change mixes, and any project-specific size thresholds."
user-invocable: true
---

# PR Scope Slicer

Decide whether a change set can be reviewed well in one pass, and when it cannot, produce an ordered slice plan where each slice is independently reviewable. Oversized or mixed-concern PRs are the main cause of multi-round reviews, because reviewers surface findings incrementally.

## When to Use

Use before opening a PR for a large or mixed change, or when an existing PR draws "too big to review" feedback. Out of scope: performing the review itself, architecture decomposition of systems (services, modules) unrelated to a pending change, and git mechanics of executing the split.

## Required Inputs

- Change inventory: files touched, approximate changed lines per file, and which changes are mechanical (renames, formatting, generated) versus semantic. When the inventory leaves some lines unclassified, treat them as semantic and say so under Size signals.
- The concerns the change contains (feature, refactor, infra, dependency bump, fix), as stated or as inferable from the inventory.
- Project-specific thresholds when the user supplies them; otherwise use the defaults below.

If no change inventory is available, emit the BLOCK template; do not guess sizes or contents.

## Size Signals (defaults, user-overridable)

Flag for splitting when any holds:

- More than 400 changed non-mechanical lines.
- More than 15 hand-written files touched.
- More than one concern mixed (refactor + behavior change, feature + infra, rename + logic edit, dependency bump + adaptation beyond the mechanical minimum).
- Generated or vendored content mixed with hand-written changes without separation.

State explicitly which thresholds were used and whether they are defaults or user-supplied.

## Split Axes

Prefer the first applicable axis:

1. Mechanical vs semantic: renames, formatting, generated output, and lockfiles go in their own fast-review slice.
2. Refactor vs behavior: a slice must never mix behavior-preserving restructuring with behavior change.
3. Dependency order: contracts and interfaces first, implementations second, call-site adoption third.
4. Subsystem independence: independent subsystems get independent slices.
5. Risk isolation: high-risk core changes separated from peripheral ones.

## Slice Rules

- Each slice builds and passes tests on its own and is independently revertible.
- Dependency order between slices is explicit; no cycles.
- Each slice names its review focus (what the reviewer should verify).
- Mechanical slices are labeled mechanical so review effort is calibrated.

## Output Format

```markdown
## Scope Slice Plan

- Change summary: <one sentence>
- Size signals: <lines / files / concerns vs thresholds; defaults or user-supplied>

Verdict: SINGLE-PASS-OK | SPLIT-RECOMMENDED | SPLIT-REQUIRED | BLOCK

### Slices

| Order | Slice | Contents | Review focus | Depends on |
|-------|-------|----------|--------------|------------|
| <1> | <slice name> | <files/changes> | <what the reviewer verifies> | <none \| slice name> |

### Tradeoffs

- <risks of splitting and of not splitting, one line each>
```

Verdict mapping: `SINGLE-PASS-OK` — no size signal fires; replace the Slices table with the line `No slices needed.` and keep Tradeoffs. `SPLIT-RECOMMENDED` — exactly one size signal other than the mixed-concern signal fires. `SPLIT-REQUIRED` — multiple signals fire, or the mixed-concern signal fires (for example refactor mixed with behavior change); when both `SPLIT-RECOMMENDED` and `SPLIT-REQUIRED` conditions apply, `SPLIT-REQUIRED` wins. `BLOCK` — insufficient input. Emit exactly one value for each enum field; do not copy enum lists or angle-bracket placeholders into the report.

### BLOCK Template (insufficient context)

```markdown
## Scope Slice Plan

Verdict: BLOCK

- Missing input: <change inventory, sizes, or concern breakdown>
- Cannot evaluate: <which size signals or split axes>
- Smallest addition to proceed: <concrete ask>
```

## Definition of Done

The verdict is justified by named size signals, every slice satisfies the slice rules with explicit ordering, and tradeoffs of the recommendation are stated.
