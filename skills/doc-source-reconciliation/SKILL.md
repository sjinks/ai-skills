---
name: doc-source-reconciliation
description: "Use when: a specification, architecture, README, or other doc claims to reflect the current implementation ('amended from implementation', 'current state') and may have drifted; verifying file extensions, target/example names, dependency lists, public type/option/enumerator names, and baked-in counts against the live tree; or flagging stale 'excluded/absent' claims before trusting a doc."
argument-hint: "The doc that claims to reflect current source, plus the repository/path to reconcile it against."
user-invocable: true
---

# Doc–Source Reconciliation

Use this skill to verify that a document claiming to describe the **current** codebase actually matches it, before that document is trusted, merged, or handed off. The recurring failure mode it prevents is silent drift: a spec that still says `.hpp` after the code moved to `.h`, lists a dependency that was removed, names an example target that was renamed, enumerates an error enum that gained members, or bakes in "127 tests" that is now wrong.

The governing rule: **facts that the tree can confirm are verified against the tree, not copied from a prior artifact or from memory.**

## When to Use

Use when a doc is described as "amended from implementation", "current state", "reflects the code", or is simply older than recent changes and about to be relied on (merged, published, used for handoff). Out of scope: forward-looking design docs that intentionally describe a *future* state, and pure product requirements with no implementation claims yet.

## Required Inputs

- The doc (or section) that claims to reflect current source.
- The repository or path to reconcile against (read-only inspection).

If the repository is unavailable, emit the `## Unverifiable` section (a BLOCK result) listing every claim you could not confirm, rather than asserting any of them are correct.

## What To Reconcile

Reconcile against the **source of truth** — the tracked source, headers, and manifests — not generated, build, or vendored copies (`build/`, `out/`, `node_modules/`, `vendor/`, `third_party/`). If the only evidence sits in such a path, or the checkout itself looks stale or generated, mark the claim `unverifiable`, not `stale`. Sweep the doc for each class of fact and confirm against that source of truth:

1. **File names and extensions** — header/source extensions (`.h` vs `.hpp`), paths, and module names mentioned in the doc still exist as written.
2. **Target / example / artifact names** — build targets, example executables, and library names match the actual build files (not an old planning name).
3. **Dependency lists** — declared/excluded dependencies match the manifest. A doc that says a dependency is "excluded/absent" must be re-checked: confirm it is still absent (it may now be used by an example or a new module).
4. **Public type / option / enumerator names** — struct/option field names and enum members named in the doc match the headers, including new members appended since the doc was written.
5. **Volatile literals** — incidental descriptive figures that drift as the code changes: test counts, allocation counts, file counts, measured throughput snapshots. Treat each as stale until confirmed, and stabilize it — restate as "the full suite" or pin it in one baseline section rather than baking in a hard number that rots. This does **not** cover normative/contractual figures (a documented connection limit, an SLO target, a default timeout/version): those are requirements, so verify and keep the exact value rather than genericizing it — a changed normative value is `stale`, not volatile.
6. **Behavioral defaults** — documented default values (timeouts, limits, versions) match the shipped defaults in code.

## Procedure

1. Extract the verifiable claims from the doc (the six classes above). Split a compound or partially-true claim ("headers are `session.hpp` and `router.hpp`") into one atomic claim per fact so each gets its own status — never force a half-true claim into a single bucket.
2. For each atomic claim, inspect the source of truth (search/read) and mark `match`, `stale`, or `unverifiable`.
3. For each `stale` claim, give the doc's value, the actual value, and the file evidence.
4. Propose the minimal correction; for a volatile literal, propose stable phrasing or one pinned baseline rather than a fresh literal that will rot again.
5. Record the reconciled corrections where the consuming workflow expects them so they are not silently carried forward.

Do not rely on memory or a prior assistant summary for any fact in the six classes; targeted inspection settles them.

## Output Format

```markdown
## Reconciliation Report

- Doc: <path/section>
- Reconciled against: <repo/path>

| Claim | Doc says | Actual | Status | Evidence |
|---|---|---|---|---|
| <atomic fact> | <value> | <value> | match/stale/unverifiable | <file> |

## Corrections

- <stale claim> → <minimal fix> (<file>)

## Volatile Literals

- <literal> → restate as "<stable phrasing>" or pin in one baseline section.

## Unverifiable

- <claim> — needs <missing access/evidence>.
```

## Anti-Patterns

- Trusting a "reflects current implementation" header without checking the six fact classes.
- Replacing one stale count with a fresh count that will rot again instead of stabilizing the phrasing.
- Genericizing a normative/contractual figure (a documented limit, SLO, or default) as if it were a volatile literal.
- Marking a correct doc `stale` against a generated, build, or vendored copy instead of the tracked source of truth.
- Preserving an "excluded/absent" claim without confirming it is still true.
- Asserting a fact is correct when the repository was not available to confirm it.
