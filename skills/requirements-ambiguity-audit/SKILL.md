---
name: requirements-ambiguity-audit
description: "Use when: auditing a draft specification, requirements document, feature request, user story, or product brief for ambiguity: vague quantifiers, undefined terms, TBD placeholders, conflicting requirements, missing actors, or untestable wording, before implementation planning starts."
argument-hint: "The draft spec, requirements list, or user story text to audit, plus any glossary or context that defines project terms."
user-invocable: true
---

# Requirements Ambiguity Audit

Audit specification text for wording that two reasonable readers would interpret differently. Ambiguity discovered during implementation costs a build-rework cycle; ambiguity found in the spec costs one rewrite line.

## When to Use

Use when a draft spec, requirements list, user story, or product brief needs an ambiguity check before planning or implementation. Out of scope: authoring a spec from scratch, auditing AI prompts or assistant instruction files, judging whether requirements are the right product decisions, reviewing code or designs against a spec, and systematically enumerating edge-case scenarios the spec should decide — this audit only flags named behaviors whose outcome wording is missing.

## Required Inputs

- The spec or requirements text to audit.
- Optional: a glossary or project context that defines terms; used to clear findings, never to invent them.

If no spec text is provided, emit the BLOCK template; do not fabricate requirements or findings.

## Ambiguity Classes

Sweep the whole text once per class:

1. `vague-quantifier`: "fast", "many", "usually", "minimal", "reasonable" — no measurable bound.
2. `undefined-term`: a domain or system term used without definition and absent from the supplied glossary.
3. `missing-actor`: passive voice or agentless requirement — who or what performs the action is unstated.
4. `conflicting-requirements`: two statements that cannot both hold; quote both.
5. `placeholder`: TBD, TODO, "to be decided", empty section, or "see above" with no referent.
6. `unspecified-path`: a named behavior whose error, empty-input, or rejection outcome is not stated.
7. `ambiguous-reference`: a pronoun or "this/that/it" whose referent is unclear between two candidates.
8. `untestable-wording`: a requirement no objective check could pass or fail as written.

## Rules

- Every finding quotes the exact text and names its location (section, requirement ID, or line).
- Findings of classes 1, 2, 3, 6, and 7 state the two (or more) plausible readings; if only one reading is plausible, it is not a finding. Classes 4, 5, and 8 replace the `Readings:` line as defined under Output Format.
- A term defined in the supplied glossary or surrounding text is not `undefined-term`.
- Every finding carries a proposed rewrite that survives the audit it failed; rewrites preserve intent and mark unknowns as explicit open questions rather than inventing values.
- Do not flag intentional flexibility that is explicitly delegated ("implementation may choose the cache strategy").
- Product-decision questions raised by the text are listed as open questions, not findings.

## Severity

- `blocker`: the plausible readings lead to materially different builds, or requirements conflict.
- `should-fix`: one reading dominates in context but is not stated; a wrong guess is plausible.
- `suggestion`: clarity polish; all readers would likely converge anyway.

## Output Format

```markdown
## Requirements Ambiguity Report

Verdict: BLOCK | CONCERNS | CLEAN

| # | Class | Severity | Location |
|---|-------|----------|----------|

### Findings

For each finding numbered as in the table:
- Quote: <exact text; for `conflicting-requirements`, both statements>
- Readings: <reading A> / <reading B>
- Proposed rewrite: <unambiguous replacement, unknowns as open questions>

### Open questions (product decisions, not findings)

- <question, who can answer it>
```

Class-specific `Readings:` replacements: `conflicting-requirements` → `Conflict: <why both cannot hold>`; `placeholder` → `Missing: <what content must be supplied>`; `untestable-wording` → `Untestable because: <why no objective check exists>`.

Verdict mapping: `BLOCK` — at least one `blocker` finding, or insufficient input. `CONCERNS` — findings exist, none `blocker`. `CLEAN` — no findings; immediately after the verdict line write exactly `All eight ambiguity classes were swept; no findings.` and keep the report with an empty table. Empty sections are written with `None`.

## Error Handling (BLOCK Template)

Use this reduced template only for missing or unreadable input. A `BLOCK` verdict caused by `blocker` findings uses the full report shape above.

```markdown
## Requirements Ambiguity Report

Verdict: BLOCK

- Missing input: <no spec text provided / text unreadable>
- Smallest addition to proceed: <concrete ask>
```

## Example

Input requirement (R1): "The export should complete quickly for large accounts."

Table row: `| 1 | vague-quantifier | should-fix | R1 |`

Finding 1:
- Quote: "complete quickly for large accounts"
- Readings: under a few seconds, interactively / minutes, as a background job
- Proposed rewrite: "The export completes within [OPEN QUESTION: target duration — owner to decide] for accounts up to [OPEN QUESTION: size bound]."

## Anti-Patterns

- Flagging a term the supplied glossary defines, or flexibility the text explicitly delegates.
- A finding with one plausible reading: that is a style remark, not ambiguity.
- Rewrites that invent the missing value ("fast" → "under 200 ms" when no target was agreed) instead of raising an open question.
- Answering the open questions yourself instead of routing them to the owner.
- Skipping the report on a clean text instead of emitting `CLEAN` with the sweep statement.

## Definition of Done

All eight classes were swept over the whole text, every finding has a quote, a `Readings:` line or its class-specific replacement, a severity, and a proposed rewrite, and the verdict follows the mapping.

