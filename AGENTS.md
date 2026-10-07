# Project Instructions

## Scope for skill and documentation work

- The skill, review, and documentation conventions below apply when changing this `AGENTS.md`, canonical `skills/**`, or related README files. `.agents/skills/**` is a generated-skill destination governed by `source-to-skill`: do not mirror it into `skills/**` or add README entries unless the request explicitly promotes that artifact. `AGENTS.md` is the sole Codex instruction surface; clients that load only `.github/instructions/*.instructions.md` are intentionally out of scope.

## Skill layout and content

- Canonical repository skills live at `skills/<name>/SKILL.md`; the folder name equals frontmatter `name`. When a compatibility symlink exists, edit only the canonical path and verify the resolved files match with `cmp`.
- Skills are standalone: do not name other repository skills. State the boundary as self-contained guidance instead.
- Keep `SKILL.md` operational: triggers, workflow, decision rules, checklist, output format, examples, and definition of done. Put long catalogs and matrices in `references/*.md`; every reference starts with when to read it, and `SKILL.md` gives each reference a concise summary and link.
- Review-style skills define a severity rubric, deterministic verdict mapping, no-findings path, and deterministic insufficient-context template. Preserve established verdict vocabularies; use `BLOCK`/`CONCERNS`/`CLEAN` only when canonical for that skill.
- Keep output labels and enums exact across templates, checklists, and references. State any mapping from a richer reference vocabulary. The checklist is the gating source when it overlaps decision rules.
- The `## Output` section defines distinctive labels, not prose-only output. Default labels may be caller-replaced only when the skill explicitly permits it; when that option exists, preserve the caller's requested labels exactly.
- A runnable embedded C/C++ example must include the headers it uses and compile and run cleanly with its stated commands and `-Wall -Wextra -Werror`. Clearly label partial illustrations and never pair them with a command that implies they are ready to run.

## Review and PR discipline

- Before fixing review feedback, fetch all available review, inline, and suppressed comments; group them by defect class; record the affected rule, related instruction/documentation surfaces, and planned validation. A later comment in that class is an audit miss, not a one-off patch.
- Treat terminology, label, enum, singular/plural, and section-name feedback as a defect class. Sweep templates, procedures, checklists, references, and examples; use `equivalence-class-audit` when applicable. Recheck any edited uniform item against its siblings.
- Never change a label, enum, or section name incidentally. It is a deliberate contract change requiring a sweep of related instructions and documentation.
- For sibling propagation, inventory the workspace and available open sibling PRs, recording searched paths, inspected evidence, and why each candidate changed or did not apply. Report unavailable required inventory as blocked.
- Before opening or updating a PR, summarize the change, inspected scope, validation performed, and any unresolved limitations in the task handoff or PR description.
- For every changed decision or output contract, compare its source rule with related templates, procedures, checklists, references, documentation, and sibling packages for branches, defaults, precedence, wording, cardinality, and blocker behavior. Verify conditional template slots use the same condition as the prose and expose only enum values permitted by that condition; rules based on user- versus risk-selected values apply to the selected value itself unless stated otherwise; code identifiers are fully qualified; and category headings match their content.

## Material skill changes

- A material update changes triggers, workflow, decision rules, output contracts, or behavior-affecting references. New skills use `cross-model-instruction-authoring`.
- Before completion, directly sweep rules, outputs, references, and documentation. If the sweep finds a mismatch, run `equivalence-class-audit` for its explicit scope; then run `instruction-quality-audit`, `adversarial-review`, and `agent-skill-audit`.
- Bind each sweep and review to the immutable final tree. Any in-scope change invalidates it. Completion requires the unchanged final tree to pass projection; have `instruction-quality-audit` return `No material defects`; have `adversarial-review` return `CLEAN`, or only user/owner-accepted concerns; and have `agent-skill-audit` return `Ready` or `Ready with limitations`. Follow every native correction or mitigation requirement; only the user or named accountable owner may accept residual risk.
- Delegate independent reviews only when the runtime exposes a subagent tool and its documented model ceiling permits a suitable model; otherwise review locally. Record the delegation or constraint and the immutable tree/diff hash in the PR description or task handoff. Delegated reviewers are read-only and bound to that tree or diff hash. Independent review requires a fresh reviewer context that did not author the change or its checks and challenges false acceptance, false rejection, and omitted dimensions. A local self-review does not count as independent; record the constraint and preserve the independent-review limitation when delegation is unavailable.
- Prefer concise shared rules to duplicated local text. Optimize for weaker models with explicit ordering, simple conditionals, stable terminology, and reproducible formats, without unnecessary process scaffolding for stronger models. Check consistency, cohesion, coherence, completeness, scope, ambiguity, contradictions, persona, cognitive load, and semantic coverage.
- For skill contracts, reconcile source wording and related documentation: canonical labels and spelling, representative selection, provenance shape, and sibling skills.

## Validation and documentation

- Always run `git diff --check` after relevant changes.
- For skill changes, also run `waza check skills/<name>`; for eval changes, validate the suite schema and every task file. Ignore only Waza's 500-token hard limit and its `argument-hint`/`user-invocable` frontmatter-field advisories, plus the `Create an evaluation suite` warning; everything else must be green.
- With multiple worktrees, run repository commands as `git -C <absolute-worktree> ...`.
- When a skill change is ready for a PR, or the user explicitly requests documentation work, keep its README synchronized with scope and supporting files; it has an overview, blurb, and `## Files` links. The top-level README lists every skill once, in the appropriate `## Skills` category, as a one-line link to that README; do not restore per-skill detail sections there.
- In Markdown README files, put a blank line before every `###` heading.
- Verify factual claims about language semantics, ABI behavior, tool defaults, or flags against authoritative sources. Qualify strong claims inline.
