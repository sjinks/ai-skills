# doc-source-reconciliation

> Use when: a specification, architecture, README, or other doc claims to reflect the current implementation ('amended from implementation', 'current state') and may have drifted; verifying file extensions, target/example names, dependency lists, public type/option/enumerator names, and baked-in counts against the live tree; or flagging stale 'excluded/absent' claims before trusting a doc.

This skill verifies that a document claiming to describe the **current** codebase actually matches it, before that document is trusted, merged, or handed off. The governing rule: facts the tree can confirm are verified against the tree, not copied from a prior artifact or from memory. It is the cure for silent drift — a spec that still says `.hpp` after the code moved to `.h`, lists a removed dependency, names a renamed example target, enumerates an error enum that gained members, or bakes in a "127 tests" figure that is now wrong.

It helps an assistant:

- sweep the doc for six classes of verifiable fact: file names and extensions, target/example/artifact names, dependency lists, public type/option/enumerator names, volatile counts and figures, and behavioral defaults
- inspect the live tree for each claim and mark it `match`, `stale`, or `unverifiable` — never settling a fact from memory or a prior summary
- give the doc's value, the actual value, and the file evidence for every stale claim, and propose the minimal correction
- re-check every "excluded/absent" claim, since a dependency once absent may now be pulled in by an example or a new module
- stabilize volatile literals — restate a baked-in count as "the full suite" or one pinned-baseline section rather than swapping in a fresh number that will rot again
- emit a BLOCK note listing the unverifiable claims when the repository is unavailable, instead of asserting they are correct

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
