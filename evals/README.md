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
- `tasks/positive-substance-*.yaml` (some suites) — a richer task with a
  realistic artifact to review or generate.
- `tasks/negative-trigger-*.yaml` — off-topic prompts that must not
  activate the skill. Each suite uses a different off-topic prompt so a
  single shared bias does not silently pass everywhere.
- `tasks/negative-close-*.yaml` (some suites) — close-domain prompts that
  look like the skill's target but should still not activate it (e.g. a
  single-lens CSS question for `multi-lens-review`).

## Grader Design

Each task has a baseline set of task-level graders plus one eval-level
`efficiency` grader. Positive tasks add `skill_invocation`; one
representative positive per skill adds `task_completion_substance`;
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
  - `multi-lens-review`: 0.40
  - `nestjs-code-review`: 0.50
  - `nestjs-development`: 0.50
  - `review-cycle-gatekeeper`: 0.40
  - `spock-voice`: 0.15 (short SKILL.md body → very few keywords)
  - `ssrf-outbound-fetch-review`: 0.45
  - `test-gap-to-test-plan`: 0.55
- `skill_invocation` (task-level, `skill_invocation`, positive tasks
  only) — requires the named skill via `required_skills` with
  `mode: any_order`. The waza CLI release in CI (`v0.33.0`) defines
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
  (`multi-lens-review`, `ssrf-outbound-fetch-review`) use 12 000
  tokens; the rest use 8 000; `spock-voice` uses 4 000.

## Skill-body injection

Upstream waza supports `config.inject_skill_body: false` in `eval.yaml`
to suppress pasting the SKILL.md body into the agent's system prompt
during trigger-precision evals. The waza CLI release we run against
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

- Two close-domain negative tasks per skill so a single close-domain bias
  does not silently pass.
- LLM-judge `task_completion_substance` graders on one representative
  positive task in each suite (seven total). They score 1.0 / 0.5 / 0.0
  against a skill-specific rubric, using the same final-line numeric
  format as `tone_quality`.
- Edge-case positives (`positive-edge-*.yaml`) per skill covering the
  documented "hard" behaviors — BLOCK on insufficient input, CLEAN
  verdicts, lens conflict resolution, regression-during-fix-cycle,
  trusted private-target opt-in, untestable risks, and the
  PLAN-PARTIAL-on-missing-owner case.
- `nestjs-development/positive-trigger-1.yaml` runs a `program` grader
  that pipes the generated TypeScript through `tsc --noEmit` so syntax
  errors fail the task.

## Running these evals

No CI workflow ships in this repo. The waza CLI's `copilot-sdk`
executor rejects the default GitHub Actions `GITHUB_TOKEN` ("GitHub
App Server-To-Server Tokens are not supported"), so a matrix workflow
cannot be added until a user-scoped Copilot PAT is configured. For
now the suite is run either:

- locally by a maintainer with `copilot login` configured, or
- in a workflow that injects a user-scoped GitHub Copilot PAT and
  accepts the per-leg quota consumption.

Until that workflow is added, run the suite manually with:

```bash
waza run evals/<skill>/eval.yaml \
  --model claude-sonnet-4.6 \
  --output results.json \
  --reporter junit:junit.xml \
  -v
```

The `waza check evals/<skill>/eval.yaml` subcommand validates the spec
without executing any model, which is useful for catching schema-drift
when upstream waza releases ship.
