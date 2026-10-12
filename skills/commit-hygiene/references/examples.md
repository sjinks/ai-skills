When to read: when illustrating a report or checking uncertain and empty-input behavior.

# Commit Hygiene Examples

These examples illustrate the core contract; they do not add requirements. Hashes and evidence are illustrative. Never infer the stated evidence from titles alone.

## Known fixup

Input: an unmerged linear range, oldest-first. Supplied diffs establish a self-contained parser in `a1a1a1a`, an independent formatter in `c3c3c3c`, and that `b2b2b2b` only corrects the parser introduced by `a1a1a1a`. The supplied subjects are `add parser`, `fixup parser`, and `add formatter`, respectively. Publication status is unknown; the merge style preserves commits. The author supplies passing verification for the proposed surviving steps, identifies `backup/parser-cleanup` as a valid unused Git branch name, and confirms the folded commit's message and authorship metadata contain no unique rationale, issue reference, attribution, or breaking-change disclosure to preserve. No open PR is reported.

````markdown
## Commit Hygiene Report

Verdict: CONCERNS

Merge style: preserve

### Rebase plan

```text
pick a1a1a1a add parser
fixup b2b2b2b fixup parser
pick c3c3c3c add formatter
```

### Actions

- a1a1a1a: keep — none: Self-contained parser step; target for b2b2b2b.
- b2b2b2b: squash — medium: Supplied diff establishes a fixup for a1a1a1a.
- c3c3c3c: keep — none: Independent formatter step.

### Resulting sequence

- add parser
- add formatter

### Cautions

- Before any authorized rewrite, create the supplied unused backup ref at the original tip: `git branch 'backup/parser-cleanup' 'c3c3c3c'`.
- Publication status is unknown: coordinate with collaborators before rewriting shared history. Any force push requires an independently verified expected remote SHA and `--force-with-lease=<ref>:<expected-sha>`; substitute verified values.

### Needs author input

None
````

## Other branches

- **Audit proposing a rewrite:** Return the full report, including the backup and publication cautions. Frame commands as safety recommendations conditional on a future rewrite; do not tell the author to execute the rebase plan.
- **Unknown backup ref:** A supported rewrite still needs a backup. Open Cautions with a descriptive backup requirement, omit the unresolved backup command, and request an unused ref under Needs author input. Do not invent a verified-unused name.
- **Folded-message facts unknown:** Use `squash` instead of `fixup`, annotate the surviving target `message pending`, and request message review to preserve any unique rationale, issue reference, attribution, or breaking disclosure.
- **Titles only:** A commit titled `wip` without a change summary becomes `needs-author-input`, with an unchanged `pick` line and a concrete evidence request. Do not guess the squash target. Verdict: `CONCERNS`.
- **Split:** An established feature plus unrelated formatting change becomes `split` / `edit`. List the two concern descriptions in intended order, each marked `subject pending`. Do not invent final subjects. Verdict: `CONCERNS`.
- **Squash merge:** No unwanted final content and no pending final-message work yields all `keep` / `pick`, no cautions, and `CLEAN`, even with intermediate fixup titles. A missing final message that needs assessment belongs under `### Needs author input` and yields `CONCERNS`.
- **Credential exposure without rewriting:** Retain any unresolved unique change as `needs-author-input` / `pick`; flag exposure and rotation without revealing the credential. Do not emit a backup recommendation unless proposing a rewrite.
- **Explicitly empty range:** Emit the full report with a `text` block containing `# No commits in supplied range`. Actions and resulting sequence are `None`. With no pending input or cautions, the verdict is `CLEAN`.
- **Unique content approved for discard:** Use `drop` only after explicit author approval; cite that approval in the rationale. Omit the discarded commit from Resulting sequence, retain its todo/action entries, and include rewrite cautions. This is the exception to net-content preservation.
- **Verification gap in a valid range:** Return the full report with verification pending under `### Needs author input`; do not emit BLOCK or claim passing tests.
- **All commits safely dropped:** Keep every input commit as a `drop` line with its evidence-backed rationale. Resulting sequence is `None`; rewrite cautions apply and the verdict is `CONCERNS`.
- **Missing hashes, ambiguous order, or merge topology:** Use the reduced BLOCK template from `SKILL.md`; do not fabricate a runnable linear todo.

## Fixup crossing an unknown commit

Input: an unmerged linear range, oldest-first. Supplied facts establish a self-contained parser in `a1a1a1a` and a parser fixup in `c3c3c3c`; the content and dependencies of intervening `b2b2b2b` are unknown. Supplied verification covers the current unchanged range, not a reordered range. Merge style preserves commits. The supplied subjects are `add parser`, `update pipeline`, and `fixup parser`, respectively. No rewrite is proposed while the crossing is unresolved.

````markdown
## Commit Hygiene Report

Verdict: CONCERNS

Merge style: preserve

### Rebase plan

```text
pick a1a1a1a add parser
pick b2b2b2b update pipeline
pick c3c3c3c fixup parser
```

### Actions

- a1a1a1a: keep — none: Preserve the evidenced parser step at its current position.
- b2b2b2b: needs-author-input — medium: Content and dependency evidence is missing; retain its position.
- c3c3c3c: needs-author-input — medium: A parser fixup is evidenced, but moving it across b2b2b2b is not yet justified.

### Resulting sequence

- add parser
- update pipeline (provisional)
- fixup parser (provisional)

### Cautions

None

### Needs author input

- Provide the change summary and dependency/review-boundary evidence for b2b2b2b before considering a move of c3c3c3c across it, and verification for any subsequently proposed reordered steps.
````

## Source verification

- [Git interactive rebase](https://git-scm.com/docs/git-rebase#_interactive_mode) documents todo actions, ordering, and folding into the previous commit.
- [Git splitting commits](https://git-scm.com/docs/git-rebase#_splitting_commits) documents `edit` as the stop used for splitting; the todo alone does not perform the split.
- [Git push](https://git-scm.com/docs/git-push) documents explicit expected-value leases and the risks of implicit leases with background fetches.

The stricter force-push form in this package is a safety requirement, not a claim that Git rejects its other supported lease forms.
