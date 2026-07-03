# evals

Evaluation suites for the skills in this repository, in
[waza](https://github.com/microsoft/waza) format. Each suite lives in
`evals/<skill-name>/` and contains:

- `eval.yaml` — eval spec: name, skill, config, metrics, and an eval-level
  `behavior` grader (named `efficiency`) for tool-call and total-token
  budgets.
- `tasks/positive-trigger-*.yaml` — prompts that should activate the
  skill, plus content/format graders to check the skill's structured
  output.
- `tasks/positive-edge-*.yaml` (some suites) — documented hard-behavior
  cases such as blocked input, no-findings reports, package/path handling,
  and other edge scenarios that still must activate and satisfy the output
  contract.
- `tasks/negative-trigger-*.yaml` — off-topic prompts that must not
  activate the skill. Each suite uses a different off-topic prompt so a
  single shared bias does not silently pass everywhere.
- `tasks/negative-close-*.yaml` — close-domain prompts that
  look like the skill's target but should still not activate it (e.g. a
  single-lens CSS question for `multi-lens-review`).

## Grader Design

Each task has a baseline set of task-level graders plus one eval-level
`efficiency` grader. Positive tasks add `skill_invocation`; selected
representative positives add `task_completion_substance`;
`spock-voice` positives add `tone_quality`; and
`nestjs-development/positive-trigger-1.yaml` adds the `ts_parse`
`program` grader. Grader names match metric names so `waza`'s metric →
grader weighting takes effect.

- `trigger_accuracy` (task-level, `trigger`) — heuristic
  prompt-vs-SKILL.md keyword overlap. `mode: positive` on positive
  tasks, `mode: negative` on negative tasks. `threshold` is calibrated
  per skill because skills here use the `Use when: ...` description
  style rather than the `USE FOR: "..."` phrase block the trigger
  grader scores most strongly against. Calibrated thresholds:
  - `adversarial-review`: 0.30
  - `equivalence-class-audit`: 0.45
  - `multi-lens-review`: 0.40
  - `nestjs-code-review`: 0.50
  - `nestjs-development`: 0.50
  - `nestjs-testing`: 0.50
  - `nestjs-version-upgrade`: 0.50
  - `review-cycle-gatekeeper`: 0.40
  - `spock-voice`: 0.15 (short SKILL.md body → very few keywords)
  - `ssrf-outbound-fetch-review`: 0.45
  - `web-app-security-review`: 0.45
  - `test-gap-to-test-plan`: 0.55
  - `archive-extraction-safety`: 0.50
  - `cross-model-instruction-authoring`: 0.45
  - `auth-claim-contract-review`: 0.45
  - `dependency-audit`: 0.50
  - `factcheck`: 0.45
  - `source-to-skill`: 0.45
  - `type-safe-design`: 0.45
  - `unicode-text-security-review`: 0.45
  - `cmake-build-review`: 0.45
  - `cpp-error-handling-design`: 0.45
  - `cpp-sanitizer-triage`: 0.45
  - `cpp-concurrency-review`: 0.45
  - `cpp-api-abi-review`: 0.45
  - `cpp-object-lifetime`: 0.45
  - `cpp-cert`: 0.45
  - `cpp-const-correctness`: 0.45
  - `cpp-performance`: 0.45
  - `cpp-struct-layout`: 0.45
  - `cpp-data-structure-selection`: 0.45
  - `cpp-openssl`: 0.45
  - `cpp-server-hardening-review`: 0.45
  - `fix-batching-and-root-cause`: 0.45
  - `fix-blast-radius`: 0.45
  - `pr-scope-slicer`: 0.45
  - `pre-review-self-audit`: 0.45
  - `review-disagreement-resolution`: 0.45
  - `review-finding-quality`: 0.45
  - `commit-message-quality`: 0.45
  - `commit-hygiene`: 0.45
  - `pr-description-quality`: 0.45
  - `single-pass-review-completeness`: 0.45
  - `acceptance-criteria-quality`: 0.45
  - `assumption-surfacing`: 0.45
  - `requirements-ambiguity-audit`: 0.45
  - `requirement-sharpening`: 0.45
  - `scope-boundary-definition`: 0.45
  - `spec-edge-case-enumeration`: 0.45
  - `architecture-decision-record`: 0.45
  - `architecture-tradeoff-analysis`: 0.45
  - `dependency-choice-review`: 0.45
  - `failure-mode-design`: 0.45
  - `interface-contract-design`: 0.45
  - `data-migration-safety`: 0.45
  - `hypothesis-driven-debugging`: 0.45
  - `implementation-task-decomposition`: 0.45
  - `refactoring-safety`: 0.45
  - `spec-deviation-handling`: 0.45
  - `vip-dev-env`: 0.45
  - `gh-cli`: 0.45
  - `shell-portability`: 0.45
  - `flaky-test-diagnosis`: 0.45
  - `test-quality-review`: 0.45
  - `perf-measurement`: 0.45
  - `doc-source-reconciliation`: 0.45
  - `artifact-consolidation`: 0.45
  - `agent-skill-audit`: 0.45
  - `instruction-quality-audit`: 0.45
- `skill_invocation` (task-level, `skill_invocation`, positive tasks
  only) — requires the named skill via `required_skills` with
  `mode: any_order`. The currently released waza CLI (`v0.33.0`) defines
  `skill_invocation` graders as positive-only: they require at least
  one `required_skills` entry and have no "forbidden" mode. Negative
  tasks therefore omit the `skill_invocation` grader entirely;
  `trigger` (with `mode: negative`) plus `text` `not_contains`
  patterns are the primary signals that the model did not
  over-activate. When upstream waza adds a forbidden / exclusion
  mode, re-add this grader on negative tasks.
- `task_completion` (task-level, `text`) — regex / `not_contains`
  checks for the skill's required output markers (verdict labels,
  section headers, severity vocabulary, forbidden catchphrases).
  Regexes target explanatory vocabulary the skill should add, not
  words echoed from the prompt. Positive tasks also `not_contains`
  the structured-output markers of unrelated skills so cross-skill
  leakage fails the task.
- `tone_quality` (`spock-voice` positives only, `prompt`) — LLM judge.
  The rubric asks for one sentence of reasoning followed by a final
  line containing only `1.0`, `0.5`, or `0.0`, so waza's prompt-grader
  parser can extract the score reliably.
- `efficiency` (eval-level, `behavior`) — `max_tool_calls` and
  `max_tokens` budgets per task. Substance-heavy suites
  (`multi-lens-review`, `ssrf-outbound-fetch-review`,
  `web-app-security-review`, `dependency-audit`, `factcheck`,
  `unicode-text-security-review`) use 12 000
  tokens; table-heavy build/architecture suites
  (`failure-mode-design`, `architecture-tradeoff-analysis`,
  `dependency-choice-review`, `implementation-task-decomposition`,
  `hypothesis-driven-debugging`, `refactoring-safety`,
  `data-migration-safety`) use 10 000; the rest use 8 000;
  `spock-voice` uses 4 000.

## Skill-body injection

Upstream waza supports `config.inject_skill_body: false` in `eval.yaml`
to suppress pasting the SKILL.md body into the agent's system prompt
during trigger-precision evals. The currently released waza CLI
(`v0.33.0`) ships an older bundled YAML schema that rejects the field
at parse time, so it is intentionally omitted from these eval specs.
Negative-trigger tasks therefore see the SKILL.md body in the system
prompt; the `trigger` grader (`mode: negative`) and the `text`
`not_contains` patterns are the only signals against over-activation
until the field can be re-added. Re-add `inject_skill_body: false`
once a waza release with the new schema ships.

## Trials and parallelism

Each task runs `trials_per_task: 2` with `max_attempts: 2` to reduce
LLM-noise flake; `parallel: true` with `workers: 4` keeps wall time
reasonable.

## Coverage extensions

The suites also include the following beyond the baseline trigger / output
checks:

- At least two close-domain negative tasks per skill so a single close-domain bias
  does not silently pass.
- LLM-judge `task_completion_substance` graders on representative
  positive tasks across suites. They score 1.0 / 0.5 / 0.0
  against a skill-specific rubric, using the same final-line numeric
  format as `tone_quality`.
- Edge-case positives (`positive-edge-*.yaml`) per skill covering the
  documented "hard" behaviors — BLOCK on insufficient input, CLEAN
  verdicts, lens conflict resolution, regression-during-fix-cycle,
  trusted private-target opt-in, untestable risks, the
  PLAN-PARTIAL-on-missing-owner case, mixed recognized severity
  normalization, unmapped severity preservation, untrusted vulnerability-report
  triage boundaries, multi-surface web-app review, separate narrow-skill
  coverage alongside broad web security review, quick output-depth behavior
  that still reports blockers and target-specific high-risk findings,
  explicit equivalence-class `n/a` rows for empty or inapplicable axes,
  blocked handling for critical unresolved audit clarifications, missing
  dependency lockfile/provenance evidence, and dev-only scanner findings that
  should not overblock without reachability evidence.
- `source-to-skill` coverage exercises generate-new-skill destination
  defaults, analyze-only mode, extract-only helper resolution relative to the
  installed `SKILL.md`, unavailable URL-source handling, and update-existing
  public-contract preservation.
- `nestjs-development/positive-trigger-1.yaml` runs a `program` grader
  that pipes the generated TypeScript through `tsc --noEmit` so syntax
  errors fail the task.

## Running these evals

No CI workflow ships in this repo. The non-secret baseline validation is
schema/spec validation only:

```bash
waza check skills/<skill>
```

`waza check` does not execute a model and is the default validation path for
frontmatter, token budget, and eval presence checks.

Model evals are optional and require local Copilot authentication or a
user-scoped GitHub Copilot PAT. The waza CLI's `copilot-sdk` executor rejects
the default GitHub Actions `GITHUB_TOKEN` ("GitHub App Server-To-Server Tokens
are not supported"), so no workflow is provided without explicit credential and
provider details. Run model evals only when one of these is true:

- locally by a maintainer with `copilot login` configured, or
- in an explicitly configured workflow that injects a user-scoped GitHub
  Copilot PAT and accepts the per-leg quota consumption.

Manual model eval command:

```bash
waza run evals/<skill>/eval.yaml \
  --model claude-sonnet-4.6 \
  --output results.json \
  --reporter junit:junit.xml \
  -v
```
