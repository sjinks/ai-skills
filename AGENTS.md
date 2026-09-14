# Project Instructions

## Running model evals (cost control)

- Never run `waza run`, or any command that issues live model/API calls, without explicit per-run user approval. State the expected scope and cost first; a full suite costs roughly 200–270 premium Copilot requests and even one `--task ... --trials 1` probe costs roughly 9–18.
- `waza check`, schema validation, `cmp`, `git`, `gh`, file reads, and searches are free. Do not re-run paid evaluation merely to confirm an established result.

## Scope for skill and eval work

- The skill, eval, review, and documentation conventions below apply when changing this `AGENTS.md`, canonical `skills/**`, `evals/**`, or related README files. `.agents/skills/**` is a generated-skill destination governed by `source-to-skill`: do not mirror it into `skills/**`, add repository evals, or add README entries unless the request explicitly promotes that artifact. `AGENTS.md` is the sole Codex instruction surface; clients that load only `.github/instructions/*.instructions.md` are intentionally out of scope.

## Skill layout and content

- Canonical repository skills live at `skills/<name>/SKILL.md`; the folder name equals frontmatter `name`. When a compatibility symlink exists, edit only the canonical path and verify the resolved files match with `cmp`.
- Skills are standalone: do not name other repository skills. State the boundary as self-contained guidance instead.
- Keep `SKILL.md` operational: triggers, workflow, decision rules, checklist, output format, examples, and definition of done. Put provenance in `references/source-map.md`; long catalogs and matrices in `references/*.md`; every reference starts with when to read it, and `SKILL.md` gives each reference a concise summary and link (including a `## Provenance` pointer for its source map).
- Review-style skills define a severity rubric, deterministic verdict mapping, no-findings path, and deterministic insufficient-context template. Preserve established verdict vocabularies; use `BLOCK`/`CONCERNS`/`CLEAN` only when canonical for that skill.
- Keep output labels and enums exact across templates, checklists, references, and evals. State any mapping from a richer reference vocabulary. The checklist is the gating source when it overlaps decision rules.
- The `## Output` section defines distinctive labels, not prose-only output. Default labels may be caller-replaced only when the skill explicitly permits it; when that option exists, preserve the caller's requested labels exactly. Negative evals must use the same canonical labels.
- A runnable embedded C/C++ example must include the headers it uses and compile and run cleanly with its stated commands and `-Wall -Wextra -Werror`. Clearly label partial illustrations and never pair them with a command that implies they are ready to run.

## Eval suites

- Every canonical skill has `evals/<name>/eval.yaml`; new suites use sibling-style `trigger_accuracy`, `skill_invocation`, `task_completion`, and `efficiency` graders. Document any intentional exception in the skill README and `evals/README.md`.
- New or materially revised suites use the applicable filename taxonomy: `positive-trigger-*.yaml`, documented `positive-edge-*.yaml`, optional `positive-substance-*.yaml` when an LLM-judge substance check is needed, unique off-topic `negative-trigger-*.yaml`, and at least two `negative-close-*.yaml`. Preserve a stable existing suite's documented exception unless the change revises that coverage. Negative tasks omit `skill_invocation` because Waza v0.33.0 has no forbidden mode.
- Positive tasks assert structured output markers in `task_completion`, not only topic keywords. When adding a marker to positive tasks, update the matching negative exclusions in the same change. Negative `not_contains` entries cover every output-template marker and proprietary skill name, never broad English vocabulary; confirm each forbidden token is absent from that task's prompt.
- Quote YAML regexes containing backslashes with single quotes. Register new suites in `evals/README.md`, including its trigger threshold and token budget.
- For new or materially revised conditional structured reports, one deterministic validator owns markers, order, domains, cardinality, branches, and termination. Keep it suite-local at `evals/<name>/check-report.py`, or in `evals/_helpers/` only for an actually shared semantic contract. Wire it through a `program` grader, document its invocation in `evals/README.md`, and mechanically verify task assertions and negative exclusions against it. Include deterministic mutations for each omission, reorder, duplicate, invalid enum, profile crossover, trailing prose, and one valid case per profile.

## Review and PR discipline

- Before fixing review feedback, fetch all available review, inline, and suppressed comments; group them by defect class; record one bounded audit manifest with the affected rule, source/eval projections, and planned validation. A later comment in that class is an audit miss, not a one-off patch.
- Treat terminology, label, enum, singular/plural, and section-name feedback as a defect class. Sweep templates, procedures, checklists, references, and examples; use `equivalence-class-audit` when applicable. Recheck any edited uniform item against its siblings.
- Never change a label, enum, or section name incidentally. It is a deliberate contract change requiring an eval-projection check.
- For sibling propagation, inventory the workspace and available open sibling PRs, recording searched paths, inspected evidence, and why each candidate changed or did not apply. Report unavailable required inventory as blocked.
- Before adding tasks, first use an existing task if it can provide an independent discriminating assertion; record why a new task is needed otherwise. Enumerate changed branches, defaults, and precedence collisions. Give each behaviorally distinct class a discriminating positive-edge task; fixtures cover only what they explicitly assert. More than five new tasks requires explicit approval of the coverage matrix from the user or a named accountable human owner; agents cannot grant that approval.
- A projection is any consumer of a changed rule: skill procedure, template, checklist, reference, eval manifest/global grader, task grader, validator, documentation, or sibling package using the same contract. Before opening or updating a PR, record a compact contract matrix in the PR description (or, before a PR exists, the task handoff): markers, order, requiredness, domains, cardinality, positive/negative examples, and each applicable projection. Record each sweep's immutable tree/diff, inspected package and sibling scope, result, and mismatches. `PASS` has no unresolved mismatch; unavailable scope is `BLOCK`.
- For every changed decision or output contract, compare its source rule with each projection for branches, defaults, precedence, wording, cardinality, blocker behavior, and positive/negative assertions; any mismatch blocks readiness. Verify conditional template slots use the same condition as the prose and expose only enum values permitted by that condition; rules based on user- versus risk-selected values apply to the selected value itself unless stated otherwise; code identifiers are fully qualified; and category headings match their content.
- Do not put volatile task totals in PR descriptions. Say `all task files`, or derive and verify a required count from the final tree. After a final post-publication push, verify and update the published body.

## Material skill and eval changes

- A material update changes triggers, workflow, decision rules, output contracts, behavior-affecting references, or eval contracts. New skills use `cross-model-instruction-authoring`.
- Before completion, directly sweep rules, outputs, references, and evals. If the sweep finds a mismatch, run `equivalence-class-audit` for its explicit scope; then run `instruction-quality-audit`, `adversarial-review`, and `agent-skill-audit`.
- Bind each sweep and review to the immutable final tree. Any in-scope change invalidates it. Completion requires the unchanged final tree to pass projection; have `instruction-quality-audit` return `No material defects`; have `adversarial-review` return `CLEAN`, or only user/owner-accepted concerns; and have `agent-skill-audit` return `Ready` or `Ready with limitations`. Follow every native correction or mitigation requirement; only the user or named accountable owner may accept residual risk.
- Delegate independent reviews only when the runtime exposes a subagent tool and its documented model ceiling permits a suitable model; otherwise review locally. Record the delegation or constraint and the immutable tree/diff hash in the PR description or task handoff. Delegated reviewers are read-only and bound to that tree or diff hash.
- Prefer concise shared rules to duplicated local text. Optimize for weaker models with explicit ordering, simple conditionals, stable terminology, and reproducible formats, without unnecessary process scaffolding for stronger models. Check consistency, cohesion, coherence, completeness, scope, ambiguity, contradictions, persona, cognitive load, and semantic coverage.
- For skill/eval contracts, reconcile source wording and every projection: canonical labels and spelling, representative selection, provenance shape, positive/negative assertions, sibling skills, and related evals.

## Validation and documentation

- Always run `git diff --check` after relevant changes. For skill changes, also run `waza check skills/<name>`; for eval changes, validate the suite schema and every task file. Ignore only Waza's 500-token hard limit and its `argument-hint`/`user-invocable` frontmatter-field advisories; everything else must be green.
- When task YAML or grader contracts change, run `python3 evals/_helpers/check-eval-regexes.py --root evals/<skill-name>`; its decoded-YAML count is authoritative. Use `--cases` for contract-specific inputs rather than grepping YAML.
- For coupled shell-command-construction/shell-portability changes, run `python3 evals/_helpers/check-shell-contract-projections.py`. It does not invoke a live model.
- With multiple worktrees, run repository commands as `git -C <absolute-worktree> ...`.
- Each skill README has an overview, blurb, and `## Files` links; keep it synchronized with scope and supporting files. The top-level README lists every skill once, in the appropriate `## Skills` category, as a one-line link to that README; do not restore per-skill detail sections there.
- In Markdown README files, put a blank line before every `###` heading.
- Verify factual claims about language semantics, ABI behavior, tool defaults, or flags against authoritative sources. Qualify strong claims inline.
