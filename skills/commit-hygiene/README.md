# commit-hygiene

> Use when: cleaning up a branch's commit history before review or merge: squashing fixup/WIP commits, dropping dead or accidental commits, flagging weak messages for reword, splitting a mixed commit, and reordering for a reviewable, bisectable sequence — producing a recommended rebase plan, never running git itself.

This skill is aimed at the ordering and grouping of one unmerged branch's commits — turning a messy work-in-progress sequence into a clean, reviewable one before it is reviewed or merged. It is advisory: it returns a rebase plan plus rationale and never runs git.

It helps an assistant:

- detect how the branch will land — squash-merge (light plan, intermediate messages discarded) versus preserved commits (each must build, pass tests, and read on its own), assuming the stricter preserve case when unknown — and state which was used
- assess a hygiene contract: squash fixup/WIP commits, drop dead/reverted/accidental/empty commits, split a commit mixing unrelated concerns, reorder for bisectability, flag reword targets, and balance atomicity against over-splitting
- leave individual commit-message wording and PR-level splitting to their own passes rather than re-deriving them
- stay safe: recommend a backup ref before any rewrite, warn that rewriting shared history needs the `--force-with-lease=<ref>:<expected-sha>` push option and re-notifies open-PR reviewers, prefer rebase `drop` over the `git reset --soft` footgun, refuse to drop work not clearly superseded, and flag that a pushed secret must be rotated regardless of the rebase
- mark each commit `keep`, `squash`, `drop`, `reword`, `split`, `reorder`, or `needs-author-input`, and return the commit hygiene report with a verdict, the detected merge style, a rebase plan, per-commit actions, the resulting sequence, cautions, and a needs-author-input section — or `BLOCK` when no commit list is supplied

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
