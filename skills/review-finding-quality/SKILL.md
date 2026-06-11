---
name: review-finding-quality
description: "Use when: writing, rewriting, or auditing code review findings, review comments, or PR feedback for quality: severity tag, evidence anchor, concrete expected fix, and an explicit acceptance condition, so each finding is actionable and closable without extra clarification rounds."
argument-hint: "The draft findings or review comments to audit or rewrite, plus the diff or code context they refer to when available."
user-invocable: true
---

# Review Finding Quality

Enforce a quality contract on review findings so each one can be acted on and closed in a single round. Vague findings cause clarification rounds; findings without acceptance conditions cause "fixed it" / "not what I meant" rounds.

## When to Use

Use when drafting review comments, rewriting existing draft findings, or auditing a findings list before it is posted. Out of scope: producing new findings by reviewing code (this skill formats and audits findings it is given), deciding merge readiness, and resolving disagreements about a finding's merit.

## Required Inputs

- The draft findings or review comments, as text.
- The diff or code context they refer to, when available; used to verify anchors, never to invent new findings.

If no findings text is provided, emit the BLOCK template; do not fabricate findings.

## Finding Contract

Every finding must carry all five fields:

1. Severity: `blocker` — must be fixed before merge; `should-fix` — fix expected, narrow waiver possible; `suggestion` — advisory, author may decline.
2. Anchor: file plus line or range, or a named behavior precise enough to locate.
3. Problem: observed versus expected, stated as evidence, not opinion or tone.
4. Fix direction: concrete enough to act on without a follow-up question; dictate exact implementation only when the contract requires it.
5. Acceptance condition: a line starting `Resolved when` that is objectively checkable by either party.

## Rules

- One finding per comment; split compound findings.
- Severity derives from impact, not from wording strength.
- A question is not a finding: list it separately as a question, with what answer would settle it.
- Pure style points already enforced by an automated formatter or linter are dropped as non-findings (note them under Dropped).
- Never invent severity, anchors, or evidence the input does not support: mark the finding `needs-author-input` and name exactly what is missing.

## Per-Finding Status

- `compliant`: already satisfies all five contract fields; keep verbatim.
- `rewritten`: rewritten here to satisfy the contract.
- `needs-author-input`: cannot satisfy the contract without information only the finding's author has.

## Output Format

```markdown
## Finding Quality Report

| # | Status | Severity | Anchor |
|---|--------|----------|--------|

### Findings

For each finding numbered as in the table:
- Severity: blocker | should-fix | suggestion
- Anchor: <file:line or behavior>
- Problem: <observed vs expected>
- Fix direction: <concrete action>
- Resolved when: <objective check>

### Needs author input

- <finding #, exactly what is missing>

### Questions (not findings)

- <question, what answer settles it>

### Dropped (non-findings)

- <item, why dropped>
```

Empty sections are written with `None`. When every finding is `compliant`, say so above the table and keep the report.

### BLOCK Template (insufficient context)

```markdown
## Finding Quality Report

Verdict: BLOCK

- Missing input: <no findings text provided / findings unreadable>
- Smallest addition to proceed: <concrete ask>
```

## Definition of Done

Every input finding appears exactly once with a status, every `rewritten` finding carries all five contract fields including a `Resolved when` line, and nothing was invented beyond the supplied input.
