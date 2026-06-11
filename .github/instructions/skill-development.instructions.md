---
description: "Use when creating, editing, validating, or reviewing skills and eval suites in this repository. Covers the skills/ symlink layout, standalone-skill rule, references/ split, eval task taxonomy, YAML regex quoting, waza validation, and README registration."
applyTo: skills/**, evals/**
---

# Skill Development Conventions

## Layout

- A skill lives in `skills/<name>/SKILL.md`. `.github/skills` is a symlink to `skills/` — never create or edit files through both paths. After edits, verify with `cmp skills/<name>/SKILL.md .github/skills/<name>/SKILL.md`.
- Folder name must equal frontmatter `name`.

## Skill Content Rules

- Skills are standalone: do not reference other skills in this repository by name. Express scope boundaries as self-contained guidance instead.
- Keep `SKILL.md` operational (triggers, workflow, decision rules, checklist, output format, examples, definition of done). Move long detail to `references/`:
  - Provenance and source confidence notes -> `references/source-map.md`, with a one-line pointer from a `## Provenance` section.
  - Detailed test matrices or long enumerations -> a `references/*.md` file, with a one-paragraph summary plus link in `SKILL.md`.
- Each `references/*.md` file starts with one sentence saying when to read it.
- Review-style skills define: severity rubric, verdict mapping (`BLOCK`/`CONCERNS`/`CLEAN`), a no-findings path, and a deterministic insufficient-context (BLOCK) template.
- Keep output-format enums exact and consistent everywhere they appear (templates, checklists, references). If a reference uses a richer vocabulary, state explicitly how it collapses to the report enum.
- When decision rules and checklist items overlap, name the checklist as the gating source of truth.

## Eval Suite

- Every skill has `evals/<name>/eval.yaml` plus tasks following the sibling-suite metric/grader structure (`trigger_accuracy`, `skill_invocation`, `task_completion`, `efficiency`).
- Task taxonomy: `positive-trigger-*.yaml` (clear activations), `positive-edge-*.yaml` (documented hard behaviors), `negative-trigger-*.yaml` (off-topic, unique per suite), and at least two `negative-close-*.yaml` (close-domain prompts that must not activate).
- Negative tasks omit the `skill_invocation` grader (waza v0.33.0 has no forbidden mode).
- In task YAML, write regexes containing backslashes as single-quoted scalars; double-quoted scalars break on `\+`, `\s`, etc.
- Register new suites in `evals/README.md`: add the calibrated trigger threshold (default 0.45 for `Use when:`-style descriptions) and the token-budget listing.

## Review-Fix Discipline

- When a review comment flags terminology, label, enum-literal, singular/plural, or section-name drift in a skill, treat it as one instance of a defect class: before pushing, sweep the whole artifact (templates, procedure steps, checklist, references, examples) for the same class — for example by running the `equivalence-class-audit` skill with the comment as the triggering finding. Do not fix only the flagged line.
- When editing one item in a uniform list or template, re-check the edited item against its siblings' shape (same fields, same `Fix:`/label structure, same placeholder style) before committing.
- Never change an output label, enum value, or section name as a side effect of another fix; label changes are deliberate contract changes that require an eval-assertion check.
- When several sibling skill PRs are open at once, apply each review finding to all sibling branches before their next review round, not only to the branch where it was reported.

## Pre-PR Checklist

Run through this list before opening or updating a skill PR; each item is a recurring reviewer-finding class:

- Conditional template slots state the same condition as the prose rule that governs them, and the placeholder enum excludes values the condition rules out (e.g. a `Depth:` line emitted only for non-default depths must not list the default in its placeholder).
- Rules that depend on who selected a value (user-requested vs risk-selected) apply to the selected value itself unless the skill explicitly says otherwise.
- Code identifiers are fully qualified and code-formatted at every mention (`std::exception_ptr`, not bare `exception_ptr`), including checklists, examples, and references.
- Items listed under a category heading actually belong to that category (e.g. export/visibility macros are boundary discipline, not a versioning mechanism).
- Positive eval tasks assert the skill's structured output markers (e.g. `Verdict:`, `Classification:`) in `task_completion`, not only topic keywords.
- Negative tasks' `not_contains` lists forbid markers from every output template the skill defines, including the reduced insufficient-context template (typically `Verdict:` and `Findings:`), so an over-activated reduced response still fails. When adding required markers to positive tasks, add the same markers to negative tasks' `not_contains` in the same change.
- Every `###` heading in `README.md` has a blank line before it; verify in the diff, and run `git diff --check` for other whitespace errors.
- Factual claims about language semantics, ABI behavior, tool defaults, or flags are verified against authoritative documentation (cppreference, ISO wording, vendor docs) before commit; strong claims ("always", "silent", "never breaks") carry their qualifying conditions inline.

## Validation

- Run `waza check skills/<name>` and `git diff --check` after changes. Eval schema and all task files must validate.
- Ignore these `waza` complaints per AGENTS.md: the 500-token hard limit and the `argument-hint`/`user-invocable` frontmatter-field warnings. Everything else should be green.

## Documentation

- Update `README.md` (skill list entry + "Included Skills" section in house style) only when the change is ready for a PR or the user asks.
