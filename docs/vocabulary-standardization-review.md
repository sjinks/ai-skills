# Vocabulary standardization review

Source tree SHA-256: `2078c18343fcf24669ec6c2e05d4d74a679d251ca2c38e3357e277bb18278631` (296 files). Hash input is each sorted repository-relative path, NUL, exact file bytes, NUL. Scope: every file under canonical `skills/`, plus `AGENTS.md`, `README.md`, `docs/skill-vocabulary.md`, and both vocabulary-check scripts. This evidence report is excluded to avoid a self-referential hash. No source change after this hash is covered by these reviews.

The inventory covered 82 canonical packages; 21 packages required changes across 50 skill files. Other packages already use canonical impact labels, consume upstream evidence without assigning severity, or return domain outcomes instead of graded findings. Domain statuses, verdict mappings, diagnostic classifications, API/log literals, and confidence scales with distinct meanings were retained.

## Validation

- `python3 -B scripts/check-skill-vocabulary.py`: passed, 82 packages; 40 contain severity sections/fields. The checker detects declaration/projection drift; it does not prove semantic equivalence.
- `python3 -B scripts/test_skill_vocabulary.py`: 11 tests passed. Tests reject old output labels, old summary counts, old action sentinels, missing levels, and unknown levels; accept canonical fields, lowercase confidence, and declared legacy-input tables. Temporary fixtures are isolated and restored.
- `git diff --check`: passed.
- `cmp`: all 50 changed canonical skill files match their paths through `.agents/skills`; that directory resolves to canonical `skills/`.
- `waza check`: ran on all 82 packages; reran all 21 affected packages on the final tree and compared with their original snapshots. Affected packages have passing links, no non-exempt specification failures, and no newly failing advisories. Six packages had link warnings repaired.
- Waza is not fully green: baseline module-count, body-structure, and cross-model-density advisories remain in affected packages. Repository-exempt token-budget/frontmatter/evaluation-suite/complexity reports were excluded from this comparison. This is a disclosed validation limitation, not a claim that all repository checks pass.
- No live model/API evaluation ran. Static checks do not establish measured model compatibility.

Baseline non-exempt Waza advisories:

| Package | Remaining baseline advisory |
|---|---|
| `boost-asio` | `module-count`, `body-structure` |
| `boost-beast` | `module-count`, `body-structure` |
| `cpp-coroutines` | `module-count`, `body-structure` |
| `nestjs-code-review` | `cross-model-density`, `body-structure` |
| `instruction-quality-audit` | `cross-model-density`, `body-structure` |
| `pre-review-self-audit` | `body-structure` |
| `requirement-sharpening` | `cross-model-density`, `body-structure` |
| `review-finding-quality` | `body-structure` |
| `test-gap-to-test-plan` | `body-structure` |
| `type-safe-design` | `body-structure` |

## Scope and sibling inventory

- Inspected canonical `skills/**` rules, outputs, references, assets/templates, examples, README files, the root README, and `AGENTS.md`; swept repeated severity fields, summary labels, notes, confidence, classifications, and producer/consumer mappings.
- `.agents/skills` is a compatibility symlink, not an independent source. Existing untracked `_/**` is experimental/user work and was preserved. No tracked evaluation suites exist in this checkout.
- Open sibling inventory on 2026-11-15: `gh pr list --repo github.com/sjinks/ai-skills --state open --limit 1000` returned two PRs, below the limit.
- [PR 140](https://github.com/sjinks/ai-skills/pull/140): inspected its complete diff. Its code-smith completion statuses carry domain meaning and it emits no severity rubric; no propagation required.
- [PR 96](https://github.com/sjinks/ai-skills/pull/96): the diff endpoint rejected its size. The paginated files endpoint returned all 313 file records with patches. Inspected skill/fixture patches for changed vocabulary and the affected NestJS/gate cases. No changed skill severity contract or old severity literal in those affected fixture patches required propagation. These patches do not constitute validation of all base-branch fixture contents. No remote files were edited.

## Review independence

Independent review was not performed. These interacting producer/consumer contracts require the routing tier `Work requiring stronger judgment, synthesis, or instruction following`. The runtime exposes selectable worker models, but this session does not establish an exact current-model ceiling comparable under the routing table. The repository rule therefore requires local review. Local self-review is not independent. All reports below are static local reviews bound to the source hash above.

## CAIE audit reports

Each report covers that package's changed vocabulary rules and their corresponding report/template/example/documentation projections, with source/enum literals treated as data. Core and conditional references were compared on their applicable paths; domain-only outcomes were not treated as synonyms.

### boost-asio

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

### boost-beast

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

### code-quality

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

### commit-hygiene

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

### commit-message-quality

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

### complexity-audit

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

### controlled-agent-instruction-english

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

### cpp-coroutines

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

### instruction-quality-audit

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

### nestjs-code-review

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

### pr-description-quality

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

### pre-review-self-audit

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

### requirement-sharpening

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

### requirements-ambiguity-audit

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

### review-cycle-gatekeeper

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

### review-finding-quality

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

### source-to-skill

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

### test-gap-to-test-plan

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

### test-quality-review

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

### test-suite-audit

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

### type-safe-design

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

Package order for the CAIE reports: `boost-asio`, `boost-beast`, `code-quality`, `commit-hygiene`, `commit-message-quality`, `complexity-audit`, `controlled-agent-instruction-english`, `cpp-coroutines`, `instruction-quality-audit`, `nestjs-code-review`, `pr-description-quality`, `pre-review-self-audit`, `requirement-sharpening`, `requirements-ambiguity-audit`, `review-cycle-gatekeeper`, `review-finding-quality`, `source-to-skill`, `test-gap-to-test-plan`, `test-quality-review`, `test-suite-audit`, `type-safe-design`.

## Equivalence-class sweep

The triggering mismatches discovered during the direct sweep were stale disclosure literals after the PR core rule changed, lowercase no-issue action sentinels, and a lowercase severity ordering sentence. Their equivalent projections were corrected before the final hash. The report below evaluates their remaining presence.

```text
## Equivalence-Class Audit Report
Triggering finding: canonical severity/sentinel changes retained old labels in report examples and reference prose
Locked audit scope: canonical vocabulary paths and matching report/template/example/README projections at the source hash above
Output depth: standard
Verdict: CLEAN
Severity: NONE
| Axis | Candidate | Presence | Disposition | Evidence |
|------|-----------|----------|-------------|----------|
| Opposite Bound | highest/lowest impact levels | absent | n/a | Four-level rubrics and output alternatives agree. |
| Sibling Parameter/Field | Severity, Confidence, status, priority, verdict | absent | n/a | Independent meanings documented; confidence remains lowercase. |
| Mirror Call Site/Use Site | repeated report entries | absent | n/a | PR/commit notes and corrected-defect examples match core rules. |
| Inverse Operation | producer/consumer transformation | absent | n/a | Gate preserves CRITICAL; planner retains original input provenance. |
| Type/Schema Narrowing | enum domains | absent | n/a | Four severity values; sentinels explicitly separate. |
| Validation vs Normalization/Sanitization | legacy aliases and disclosures | absent | n/a | Explicit case-sensitive aliases; redaction independent of impact. |
| Happy/Error/Retry/Cancel Path Twin | full and reduced reports | absent | n/a | PR disclosure present/none and IQA blocked counts match their cores. |
| Race/Shared-State Twin | concurrent state | n/a — structurally inapplicable | n/a | Static vocabulary migration has no shared runtime state. |
| Permission/Authorization Class | execution authority | absent | n/a | Severity changes grant no execution or risk-acceptance authority. |
| Observability Twin | summary counts | absent | n/a | IQA full, clean, and blocked summaries use all four levels. |
| Resource Cleanup | checker fixtures | absent | n/a | Temporary test roots restored; no retained model/runtime resources. |
| Contract Symmetry | rubric/template pairs | absent | n/a | Matching prose, snippets, and exceptional templates inspected. |
| Equivalence by Naming | sibling severity rubrics | absent | n/a | Canonical skills use uppercase impact labels; distinct concepts retained. |
| Test Mirror | checker regression cases | absent | n/a | Eleven checks cover acceptance and rejection boundaries. |
| Empty/Sentinel Equivalence | NONE, UNASSESSED, unknown, note | absent | n/a | Each remains scoped to its declared report/action context. |
| Async/Sync or Mode Twin | author, audit, validate, repair | absent | n/a | Original-versus-final assessment and correction status remain independent. |
| Documentation/Spec Prose Twin | README and authoring policy | absent | n/a | Canonical vocabulary guide and affected package README files synchronized. |
| Cache/Projection/Source-of-Truth Twin | compatibility symlink | absent | n/a | All 50 changed files compared equal through the symlink. |
### Defects to fix now
- None
### Deferred follow-ups
- None
### Out-of-scope candidates discovered
- None
### Blocking questions
- None
### Test/doc implications
- None
```

## Instruction-quality audit

```text
# Instruction Quality Audit
Audit: repository vocabulary migration at the source hash above
## Audit Scope
- Mode: package
- Status: completed
- Effective instruction files: AGENTS.md; docs/skill-vocabulary.md; changed skills and their vocabulary-related references, templates, examples, and README projections
- Mutually exclusive paths: each installed skill invocation; author/audit/validate modes remain scoped by each core; no cross-skill co-loading is assumed
- Trusted custom diagnostics: repository vocabulary consistency and self-contained package requirements
- Limitations: vocabulary and its interacting report contracts only; static review, not whole-domain correctness certification or model execution
## Findings
None.
## Unresolved Questions
None.
## Summary
Critical: 0
High: 0
Medium: 0
Low: 0
Highest-priority corrections:
None.
Verdict: No material defects
```

## Adversarial review

```text
## Adversarial Review Report
Verdict: CLEAN
Target: canonical vocabulary migration at the source hash above
Intended behavior: use one impact severity vocabulary while preserving distinct status, confidence, priority, and local verdict contracts
Evidence basis: final source comparisons, eleven checker regression tests, baseline Waza comparison, and symlink comparisons
What works: packages retain local rubrics; consumers preserve canonical severities and declared legacy-input provenance; exceptional templates match their source rules
Assumptions: review is limited to the vocabulary migration; no model behavior or deployment compatibility is inferred
Findings: None
Adversarial tests: None
Mitigations / acceptance criteria: None
Residual risk: static checks do not prove model behavior; external parsers of migrated output labels need the documented contract update
```

## Readiness audit

```text
# Agent/Skill Readiness Audit
Audit: canonical repository vocabulary migration at the source hash above
## Audit Scope
- Artifact type: Other
- Mode: package
- Status: completed
- Target models: default profile roster below
- Target runtimes: Not supplied
- Files included: canonical vocabulary rules and interacting report/template/example/README paths; root authoring policy and vocabulary check invocation
- Files excluded: unrelated domain logic, experimental untracked artifacts, remote base-branch fixtures
- Limitations: static assessment only; effort/runtime settings not supplied; no independent review or measured model evaluation; baseline Waza advisories remain, so this is not an all-checks-green or merge-readiness certification
## Readiness Ratings
| Area | Rating | Main risk |
|---|---:|---|
| Discovery and delegation | 4 | Package triggers preserved; no independent review performed. |
| Instruction architecture | 5 | Packages retain local operational rubrics and no new runtime document dependency. |
| Operational completeness | 4 | Local verdicts and exceptional templates retained; legacy inputs require explicit mappings. |
| Model and runtime portability | 4 | Static compatibility only; runtime/effort settings unknown. |
| Maintainability and evaluability | 4 | Checker protects literal projections; semantic review remains required. |
## Material Findings
None.
## Target-Model Compatibility
| Model | Verdict | Main risk | Required adaptation |
|---|---|---|---|
| GPT-6 Luna | Suitable with limitations | Static profile assessment; execution/settings unverified. | None established by this static vocabulary review. |
| GPT-6 Sol | Suitable with limitations | Static profile assessment; execution/settings unverified. | None established by this static vocabulary review. |
| GPT-6.1 Sol | Suitable with limitations | Static profile assessment; execution/settings unverified. | None established by this static vocabulary review. |
| GPT-6 Astra | Suitable with limitations | Static profile assessment; execution/settings unverified. | None established by this static vocabulary review. |
| Claude Haiku 5.5 | Suitable with limitations | Static profile assessment; execution/settings unverified. | None established by this static vocabulary review. |
| Claude Sonnet 5 | Suitable with limitations | Static profile assessment; execution/settings unverified. | None established by this static vocabulary review. |
| Claude Sonnet 5.5 | Suitable with limitations | Static profile assessment; execution/settings unverified. | None established by this static vocabulary review. |
| Claude Opus 4.8 | Suitable with limitations | Static profile assessment; execution/settings unverified. | None established by this static vocabulary review. |
| Claude Opus 5 | Suitable with limitations | Static profile assessment; execution/settings unverified. | None established by this static vocabulary review. |
| Claude Opus 5.5 | Suitable with limitations | Static profile assessment; execution/settings unverified. | None established by this static vocabulary review. |
| Claude Fable 5 | Suitable with limitations | Static profile assessment; execution/settings unverified. | None established by this static vocabulary review. |
| Claude Fable 5.1 | Suitable with limitations | Static profile assessment; execution/settings unverified. | None established by this static vocabulary review. |
| Claude Mythos 5.1 | Suitable with limitations | Static profile assessment; execution/settings unverified. | None established by this static vocabulary review. |
## Priority Changes
None.
Verdict: Ready with limitations
```
