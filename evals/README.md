# evals

Evaluation suites for the skills in this repository, in
[waza](https://github.com/microsoft/waza) format. Each suite lives in
`evals/<skill-name>/` and contains:

- `eval.yaml` — eval spec: name, skill, config, metrics, and eval-level
  graders such as `behavior` `efficiency` for tool-call and total-token
  budgets and deterministic output-contract checks where a suite defines one.
- `tasks/positive-trigger-*.yaml` — prompts that should activate the
  skill, plus content/format graders to check the skill's structured
  output.
- `tasks/positive-edge-*.yaml` (some suites) — documented hard-behavior
  cases such as blocked input, no-findings reports, package/path handling,
  and other edge scenarios that still must activate and satisfy the output
  contract.
- `tasks/positive-substance-*.yaml` (some suites) — representative
  realistic artifacts that add LLM-judge substance graders beyond marker
  and routing checks.
- `tasks/negative-trigger-*.yaml` — off-topic prompts that must not
  activate the skill. Each suite uses a different off-topic prompt so a
  single shared bias does not silently pass everywhere.
- `tasks/negative-close-*.yaml` — close-domain prompts that
  look like the skill's target but should still not activate it (e.g. a
  single-lens CSS question for `multi-lens-review`).

## Offline regex validation

Validate one suite without issuing model/API calls:

```sh
python3 evals/_helpers/check-eval-regexes.py --root evals/<skill-name>
```

Use `--root evals` for the repository-wide inventory. The validator decodes YAML
before counting and compiling every text grader's `regex_match` and
`regex_not_match` value with Go's `regexp` engine. Raw grep/line counts are not
authoritative. The first run may download the Go module's pinned YAML dependency.
It requires Python 3.9+ and Go 1.20+.

Optional contrastive cases are JSON and select a decoded regex by task path
relative to `--root`, grader name, list name, and zero-based index:

```json
{
  "cases": [
    {
      "name": "complete verdict",
      "task": "example/tasks/positive-trigger-1.yaml",
      "grader": "task_completion",
      "list": "regex_match",
      "index": 0,
      "matches": ["Verdict: CLEAN"],
      "does_not_match": ["Verdict: CLEAN trailing text"]
    }
  ]
}
```

Pass the file with `--cases path/to/cases.json`. A missing selector, unexpected
match/non-match, YAML error, or Go-incompatible regex fails the command with task
and grader context.

## Structured report contracts

When a skill emits a conditional structured report, make its output grammar an
executable source of truth instead of duplicating it in prose and unrelated
regexes. The shell-portability grammar lives in
`evals/_helpers/report_contract.py`; it is deliberately scoped to that skill's
finding fields and enum domains. Its preflight verifies the skill template,
decoded `task_completion` projection, and a mutation matrix without calling a
model:

```sh
python3 evals/_helpers/check-shell-report-contracts.py
```

Add a corresponding, skill-owned preflight when another skill needs a report
grammar. It must cover every profile and reject missing, reordered, duplicate,
invalid, or trailing fields.

## Grader Design

Each task has a baseline set of task-level graders plus an eval-level
`efficiency` grader; suites with an eval-level output contract also define a
matching `output_contract` metric and grader. Positive tasks add `skill_invocation`; selected
representative positives add `task_completion_substance`;
`spock-voice` positives add `tone_quality`; and
`nestjs-development/positive-trigger-1.yaml` adds the `ts_parse`
`program` grader. The `adversarial-review`, `equivalence-class-audit`, and `factcheck` suites
add deterministic `report_contract` program graders. Grader names match metric names so `waza`'s
metric → grader weighting takes effect.

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
  - `controlled-agent-instruction-english`: 0.45 (initial heuristic threshold; live calibration pending)
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
  - `cpp-correctness-review`: 0.45
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
  - `shell-command-construction`: 0.45
  - `flaky-test-diagnosis`: 0.45
  - `test-quality-review`: 0.45
  - `test-design`: 0.45
  - `perf-measurement`: 0.45
  - `doc-source-reconciliation`: 0.45
  - `artifact-consolidation`: 0.45
  - `agent-skill-audit`: 0.45
  - `instruction-quality-audit`: 0.45
  - `handoff-note`: 0.45
  - `iteration-retrospective`: 0.45
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

The `cross-model-instruction-authoring` suite validates its conditional
profile-recommendation output with
`python3 evals/cross-model-instruction-authoring/check-profile-recommendation.py --self-test`.
The checker owns heading order, profile and patch value domains, required
section bodies, profile crossover, and terminal output for the
Profile Recommendation tasks.
It validates the shared Author/Adapt/Review-and-Rewrite wrapper with
`python3 evals/cross-model-instruction-authoring/check-standard-output.py --self-test`.
That checker owns label order and cardinality, required section bodies,
preamble rejection, and terminal compatibility-note handling for every
positive task using the standard wrapper.
- `output_contract` (eval-level `code`) — validates a suite-defined structured
  output contract. Shell-command-construction validates canonical
  construction-shaped output while allowing ordinary markerless prose for
  negative non-activation tasks; shell-portability rejects legacy-label mixing
  and trailing prose after a normal report.
- `report_contract` (`adversarial-review`, `equivalence-class-audit`, and
  `factcheck` positive tasks, `program`) — reads the raw agent output that Waza
  passes on stdin and validates each suite's complete report grammar, including
  top-level order, marker uniqueness, canonical enums, required rows, and
  termination. `adversarial-review` negative tasks pass `--reject`, which
  succeeds only when the output is not a complete canonical adversarial-review
  report. `equivalence-class-audit` attaches this grader only to positive tasks
  and its checker accepts a positive profile ID. `factcheck` validates evidence
  access, claim class, evidence locator/support, and one finding/correction per
  claim; `evals/factcheck/test_check_report.py` covers valid and deterministic
  malformed-report mutations. Exit code 0 passes and any non-zero exit fails.
- `tone_quality` (`spock-voice` positives only, `prompt`) — LLM judge.
  The judge calls `set_waza_grade_pass` exactly once when every full-success
  criterion holds; otherwise it calls `set_waza_grade_fail` exactly once.
  Reasoning belongs in the tool call's `reason` argument. Partial completion
  fails this strict binary rubric.
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
  `adversarial-review` uses 90 000 because paired-review tasks measure
  roughly 68 000 total tokens after fixed harness injection and cached
  multi-turn re-sends;
  `handoff-note` is explicitly budgeted at 8 000; `spock-voice` uses
  4 000.
  `shell-command-construction` uses 8 000 tokens and 10 tool calls.

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
  positive tasks across suites. They use the same strict binary pass/fail
  tool-call protocol as `tone_quality`, with skill-specific full-success
  criteria. Numeric response text alone is not a grade.
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
  blocked handling for critical unresolved audit clarifications, output-contract
  consistency for placeholders, enum drift, partial snippets, multi-report
  numbering and separators, missing dependency lockfile/provenance evidence,
  and dev-only scanner findings that should not overblock without reachability
  evidence.
- `source-to-skill` coverage exercises generate-new-skill destination
  defaults, analyze-only mode, extract-only helper resolution relative to the
  installed `SKILL.md`, unavailable URL-source handling, and update-existing
  public-contract preservation.
- `nestjs-development/positive-trigger-1.yaml` runs a `program` grader
  that pipes the generated TypeScript through `tsc --noEmit` so syntax
  errors fail the task.

## Running these evals

No CI workflow ships in this repo. The non-secret baseline validates the
schema/spec and decoded task regexes:

```bash
waza check skills/<skill>
python3 evals/_helpers/check-eval-regexes.py --root evals/<skill>
```

`waza check` does not execute a model and is the default validation path for
frontmatter, token budget, and eval presence checks. Run the regex validator
whenever task YAML or grader contracts change; it also does not execute a model.

`test-design` uses a 0.45 trigger threshold and a 7,000-token budget. Its
suite-local report validator checks default and caller-selected labels, blocked
and implementation branches, and verification status. The only implementation
profile is `implement`: it accepts `Ran:` with a pass/fail/exit result or
`Unverified:` with a reason, and rejects the no-change status. The exact run
grammar is `Ran: <command> => <passed|failed|exit N>`, with a nonempty command
and integer N. Its self-test
checks every supported profile against both status families. The implementation
edge uses supplied repository files and an exact test-file diff snapshot to require
executable interior and boundary tests (with an explicit formatting contract),
plus text assertions for the defect caught and execution outcome.

The isolated-test audit, writing one preselected test, and available-framework precedence are independent
negative-close tasks. The implementation edge supplies the positive framework
fallback when no dedicated workflow exists; flaky-test diagnosis has its own
negative-close task.

Default report labels are `Designed cases:`, `Design evidence:`, and
`Test execution:`. The projection check scans sibling skill packages for
marker collisions and permits the review-plan workflow's `Test cases:` marker
in negative responses. A separate review-findings negative case covers that
route. Bounded semantic regexes use DOTALL and have multiline contrastive cases,
including positive-transfer balance preservation and reporting the offending row.
The assessment edge checks singleton selection with a JSON case array and
`check-report.py assessment --case-count 1`; each object requires nonempty
`behavior`, `expected`, and `defect` strings. The count constraint applies only
when requested, not to ordinary assessments. It also checks partial contracts
and an explicit coverage gate; those two evidence assertions cannot match case or execution content. Reports start with their first label, without a blank or whitespace preamble. The diagnosed-failure task requires the exact supplied test command in the execution report.
Additional implementation edges require an unavailable-run status when hardware
has no faithful substitute and a diagnosed failure against unchanged buggy
production code. The user approved this expanded coverage matrix.
The isolated test-quality workflow owns writing one caller-preselected test; its existing byte-exact positive edge exercises that branch. Feature case selection and implementation remain in the feature workflow even if selection yields one case.
The `production_unchanged` diff grader compares `clamp.js` with the exact
snapshot under `evals/test-design/snapshots/`, with `update_snapshots: false`.
Snapshot comparison follows the [Waza v0.33.0 diff grader](https://github.com/microsoft/waza/blob/v0.33.0/docs/graders/diff.md).

```bash
python3 evals/test-design/check-report.py --self-test
# Validate a supplied singleton assessment report without model calls:
python3 evals/test-design/check-report.py assessment --case-count 1 < report.txt
python3 evals/test-design/check-projections.py
python3 evals/_helpers/check-eval-regexes.py --root evals/test-design --cases evals/test-design/regex-cases.json
```

The `handoff-note` caller-schema edge case additionally validates its exact
heading set and order without a model:

```bash
python3 evals/handoff-note/check-report.py --self-test
python3 evals/handoff-note/test_check_report.py
```

The projection test verifies that exact-schema profiles use the matching checker
and that negative and stop-path tasks exclude the distinctive custom top-level
markers without banning broad headings such as `## Risks`.

Static checks validate only artifact structure and deterministic assertions; they do not prove any model's behavior. GPT-5.4 mini and Claude Haiku 4.5 are compatibility-floor evaluation goals, not proven outcomes. Live evidence is specific to the model, runtime, and settings, and each live evaluation remains explicitly approval-gated.

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

`test-quality-review` retains its per-test verdict vocabulary and adds
`Authored test:` after `Verdict:` and `Findings:` for writing only. Its
`report_contract` program metric validates conditional labels, findings syntax,
verdict domains, file/snippet location syntax, generated snippet bounds, fenced code and termination. Negative
tasks exclude all three labels and the skill name. The byte-contract edge supplies
API/behavior constraints instead of a completed test; graders require generated
setup, serialization and assertion. Its declared formatting constraints allow
exact structural validation with `--wire-fixture`, rejecting comment-only bodies,
omitted setup/calls and altered expected bytes. Existing review cases use the review profile.
The suite uses a 0.45 trigger threshold and an 8,000-token budget.

```bash
python3 evals/test-quality-review/check-report.py --self-test
python3 evals/test-quality-review/check-report.py author --verdict solid < report.txt
python3 evals/test-design/check-projections.py
python3 evals/_helpers/check-eval-regexes.py --root evals/test-quality-review --cases evals/test-quality-review/regex-cases.json
```

Feature-test evals now require counted JSON records on every nonblocked positive
case. Structural grading verifies field presence per record and rejects generic
defect placeholders; `case_substance` independently judges each behavior,
observation and plausible defect mapping. This adds judge calls to future paid
runs; no live run was used to validate this revision. The threshold is 1.0.
Both clamp task execution assertions name their supplied target command.
Implementation fixtures snapshot `package.json`, and `workspace_integrity`
(threshold 1.0) rejects changed/missing package configuration and known package
or lockfile/install artifacts inside `WAZA_WORKSPACE_DIR`. It fails closed if that
variable is absent. The guard is read-only and does not inspect installations
outside the task workspace or prove that no command was attempted.
The workspace boundary follows the [Waza v0.33.0 program grader](https://github.com/microsoft/waza/blob/v0.33.0/docs/graders/program.md).

```bash
python3 evals/test-design/check-workspace.py --self-test
python3 evals/test-design/check-report.py implement --case-count 3 < report.txt
```

The approved isolated-authoring missing-context edge uses `check-report.py missing`
and requires the absent behavior/expected-result contract without invented code.
The projection map now covers review, authoring, and missing-context tasks.

The feature plan task now discriminates the read-only default when no test
modification was requested. The runnable clamp edge explicitly provides Node
and requires the supplied command to pass; failed and unavailable execution
remain separate edges. Quality authoring accepts an existing draft body.
Its framework-precedence negative and two-test review edge were user-approved.
Multiple review reports use the same grammar in input order, separated by a
blank line. Authoring remains singular; missing-context reports may occur per
reviewed test. Validate batches with:

```bash
python3 evals/test-quality-review/check-report.py review --test-count 2 --verdicts cannot-fail,solid < report.txt
```

Both testing suites register `workspace_unchanged` at threshold 1.0 for every
initially empty positive workspace that must remain read-only, including blocked
and missing context and snippet-only authoring. The shared semantic contract
is an existing real task directory with no entries at grading time; both suites
use `evals/_helpers/check-empty-workspace.py`. It rejects files, hidden entries,
empty directories and symlinks, and fails closed when the directory is absent.
The projection checker verifies the guarded tasks supply no resource files.
This is final-state evidence, not a trace of transient or outside-workspace
changes. The pinned [Waza program-grader contract](https://github.com/microsoft/waza/blob/v0.33.0/docs/graders/program.md)
provides `WAZA_WORKSPACE_DIR`; pinned workspace setup creates a temporary directory
and writes supplied resources. The Copilot session may restore files before
grading, so changes restored before grading are outside this guard's evidence.

```bash
python3 evals/_helpers/check-empty-workspace.py --self-test
WAZA_WORKSPACE_DIR=/path/to/task-workspace python3 evals/_helpers/check-empty-workspace.py
```

Authored report labels are counted only in the envelope, through `Authored test:`;
label-looking text inside the code fence is data. The existing wire authoring
edge now requires a multiline fixture comment with every canonical marker.
Default/custom-label fixtures cover solid, weak and cannot-fail author outcomes;
envelope duplicates and labels outside the closing fence remain invalid.

## Review evidence gate

`evals/_helpers/check-review-evidence.py` runs trusted local conforming and
rule-isolating counterexample probes against an immutable scoped tree. It keeps
contract, workspace, execution and model claims separate and records independent
review evidence or its unavailability. Both scope comparisons disable external
diff and textconv. All gate Git calls disable replacement objects, including
the raw blob read. Ordinary Python traceback output fails either probe;
diagnostic matching alone cannot authenticate a custom exception handler.
It does not invoke Waza or add model tasks.
See [the manifest contract and workflow](../docs/review-evidence.md).

```bash
python3 -m unittest discover -s evals/_helpers -p test_check_review_evidence.py
python3 evals/_helpers/check-review-evidence.py /tmp/review-evidence.json --repo "$PWD"
```


### Iteration retrospective report validation

`iteration-retrospective` uses a 0.45 trigger threshold and an 8,000-token budget.
Positive report tasks invoke the suite-local `report_contract` program grader
with task-specific verdict, candidate, and attempt-count expectations.
The invalid-label task uses the same grader with `--profile label-clarification`,
which validates a clarification response instead of requiring a report. The
validator owns marker spelling/order/cardinality, row fields and numbering,
value domains, default/caller-label profiles, the blocked branch, and termination.
Text graders assert the contextual status and mechanism decisions separately.
Negative exclusions cover every top-level report and clarification marker and the skill name. Default markers use a `Retrospective` prefix; generic row fields such as `Status:` and `Result:` are not independent forbidden tokens.

Existing tasks cover unknown causes, guidance precedence, blocked default labels,
known failures, and independent new-skill eligibility. `positive-edge-4.yaml`
adds evaluated partial success versus unevaluated replacement and pending outcomes,
and source-of-truth mapping; existing histories do not contain those combinations.
`positive-edge-5.yaml` adds valid caller labels, mechanism tie-breaking, preserved known failed outcomes, and an unselected established-guidance update;
existing tasks previously used only default labels. `positive-edge-1.yaml` now covers one explicitly abandoned unevaluated approach and passes
ignored caller labels that collide with blocked-report content to the validator.
`positive-edge-6.yaml` discriminates new repository guidance from extension of an
established workflow and retains that selected mechanism while a second pattern
has unrankable comparison costs. It requires `CONCERNS` and a cost-evidence next check.
`positive-edge-7.yaml` discriminates aggregation across selected reusable-skill
and established-guidance rows; existing tasks select only one mechanism.
The new-guidance task cannot reuse the existing-guidance fixture without losing
its extension assertion. The aggregation task needs multiple selected patterns;
adding them to existing single-pattern fixtures would remove their isolation.
The checker enforces candidate/mechanism compatibility; evidence that guidance
is established and that a new skill is eligible remains a contextual assertion.
`positive-edge-8.yaml` exercises duplicate nonblocked labels and requires only
the fixed conflict/request clarification. Existing custom-label and blocked
fixtures remain report tasks, so neither can cover this branch without losing
its independent assertion. Deterministic mutations also cover malformed, empty
and row-shaped labels, invalid profile crossovers, and BLOCK precedence.
Missing-evidence requests about a single explicitly abandoned approach activate the blocked fixture;
a single nonabandoned attempt and generic reflection remain excluded.
Label mutations cover every line boundary documented for Python `str.splitlines()`;
nonblocked labels must remain a single unchanged line under that same operation.
They also reject every C0/C1 control (U+0000–U+001F and U+007F–U+009F),
including controls that are not line boundaries, in every label slot.
Every positive `task_completion` text grader asserts its active profile's literal
first marker with `(?m)^`; the projection checker rejects omitted, row-only,
inactive and unanchored replacements. Default, custom, BLOCK and clarification
profiles use their respective active marker. The envelope-only response probe
checks that assertion independently of the program report grader. The `--label-set`
probe validates a JSON array of caller labels independently of response formatting.
The boundary-test debugging task also requires the selected `deterministic check`
mechanism, rejecting an empty prevention section or an unrelated mechanism.
Nonblocked failed/partly-worked timelines require learning rows; `CONCERNS`
requires next-check rows. Success-only no-learning and blocked missing-evidence
profiles remain valid. Unknown costs do not authorize guessing or early list-order
tie-breaking. Repurposed edge fixtures retain their previous label/guidance
assertions; no additional task is introduced. Empty-history BLOCK remains covered
by deterministic profile tests.
No paid model run is implied.

```bash
python3 evals/iteration-retrospective/check-report.py --self-test
python3 evals/iteration-retrospective/check-projections.py
python3 evals/iteration-retrospective/check-projections.py --label-set < labels.json
python3 evals/iteration-retrospective/check-projections.py --positive-envelope-task positive-edge-5.yaml < response.txt
python3 evals/iteration-retrospective/check-projections.py --negative-task negative-trigger-1.yaml < response.txt
python3 evals/iteration-retrospective/check-report.py --verdict CLEAN < report.txt
python3 evals/_helpers/check-eval-regexes.py --root evals/iteration-retrospective
```


## Controlled agent instruction English

`controlled-agent-instruction-english` uses a 0.45 trigger threshold, 8,000-token
budget, and eight tool calls. The positive trigger covers authoring with mandatory
validation, literal preservation, and a failure branch. The audit edge covers
mandatory modality, prerequisite order, and a warning requiring an unresolved
antecedent to be clarified. Two close negatives cover ordinary
prose editing and model selection without an artifact; the unique off-topic
negative covers a bead-count arithmetic puzzle.

The positive edges cover findings audits, clean audits with advisory thresholds,
missing audit input, unresolved intended behavior during a rewrite, and combined
audit-and-rewrite requests. The user explicitly approved the final nine-task
coverage matrix. The two blocked tasks distinguish unavailable audit text from
readable source whose intended failure policy cannot be chosen, even in a combined
audit-and-rewrite request. The author trigger also exercises sufficient purpose and
constraints despite an unavailable source. Coverage of further author-input and
combined-clean branches is being prepared; the nine-task matrix is the currently
approved scope.
There are no reusable existing tasks in this new suite; neighboring suites have
different report and routing contracts and cannot independently assert this one.

The `report_contract` program metric (threshold 1.0) selects `author`, `author-findings`,
`audit-clean`, `audit-findings`, or `blocked`. All five grammar profiles are covered
by deterministic fixtures, including the combined `author-findings` profile.
Selected author, audit, combined, and unresolved-intent positives include a `task_completion_substance` judge
metric (threshold 0.9) to reject reversed prerequisites and ineffective corrections.
This is an intentional selected-task metric; negatives retain exclusion graders,
and clean/missing-audit-input edges use deterministic branch assertions.
The unresolved-author-intent rubric rejects a chosen failure policy or invented
fallback, while allowing both policies to be named as unresolved alternatives. The judge rubrics are
configured, but their behavior has not been measured by a live run.
Run the free preflight with:

```sh
python3 evals/controlled-agent-instruction-english/check-report.py --self-test --projections
python3 evals/_helpers/check-eval-regexes.py --root evals/controlled-agent-instruction-english
waza check skills/controlled-agent-instruction-english
```

The validator checks marker order/cardinality, enums, findings fields, artifact
payload boundaries, profile crossover, clarification questions ending in `?`,
nonempty path/section locations, bare-pipe literals, inline backtick literals
containing spaced separators, and terminal status. It mechanically
checks decoded positive marker assertions, program/profile bindings, and complete
negative exclusions. Static checks do not establish model behavior; no live eval
has been approved or run for this onboarding.

Positive prompts explicitly permit reading the invoked skill and its bundled
references while forbidding inspection or modification of scenario workspace
files. This preserves mandatory resource loading without assuming a runtime
installation path.

## Prompt-grader protocol preflight

Waza v0.33.0 records `set_waza_grade_pass` and `set_waza_grade_fail` calls; a judge
that returns only numeric text fails with no recorded grade. Repository prompt
graders use exactly one pass call when every full-success criterion holds and
one fail call otherwise, including partial completion, with reasoning in the
tool's `reason` argument. This follows the [upstream prompt-grader contract](https://github.com/microsoft/waza/blob/v0.33.0/docs/graders/prompt.md).

Run the free decoded-YAML protocol check and its isolated mutations with:

```sh
python3 evals/_helpers/check-prompt-grader-contracts.py --self-test
```

The scan root must be an existing directory; missing roots and regular files fail.
An existing directory without prompt graders reports zero applicable graders.
This checks configured judge instructions, not live judge behavior.
