# Vocabulary checker review remediation

Source SHA-256: `157583037d05c2c18f234f7754a85134ecb685d80f8934e4559915c8e9225d27`.

This report supersedes the source fingerprint for checker execution in the earlier [state migration review](vocabulary-state-review.md). Hash the same 296 sorted relative source paths as that report: path, NUL, exact file bytes, NUL, using SHA-256; exclude evidence reports. Skill files, authoring rules and vocabulary guide are byte-identical to commit c03738f26d405819d3451de24b56f22074896c1a. The earlier CAIE, instruction-quality and readiness reports remain evidence for those unchanged instruction bytes, not proof of the corrected checker.

## Review intake and fix classes

Fetched all available merged discussion comments, submitted reviews (including suppressed/previously missed bodies), and inline review threads for PR #147 and companion PR #96. PR #147 had one unresolved inline thread and one additional suppressed finding; its two earlier threads were already resolved. PR #96 had no unresolved inline threads and no new review submissions for this follow-up; its historical whole-PR limitations are unchanged.

| Class | Finding | Affected source/projections | Planned validation and observed result |
|---|---|---|---|
| Presentation must not bypass declaration validation | Inline 4576428407: bold-colon rubric labels were skipped. | BULLET_DEFINITION collection, active severity section, test-suite-audit severity rubric, neighboring bold/code/unformatted rules. | Both colon placements accept all four levels; removing each level fails even with a complete README; extra uppercase/lowercase unknown levels fail. Red before fix, green after. |
| Every declared report anchor must be inspected | Suppressed Subject finding in review PRR_kwDOSjxqsc8AAAABYCgyqQ. | OLD_ENTRY and commit-message-quality report anchors; related Title/Body/Footers/Input/Convention/Structure/Disclosure anchors. | Every anchor rejects every listed legacy label; Subject accepts all four canonical severities and permitted note. Red before fix, green after. |

Bold presentation markers are removed before bullet collection; canonical enum validation still occurs locally. Unknown single-word labels inside an active severity section cannot silently end that rubric. Multiword classifications, verdicts, confidence, legacy input prose and standalone domain fields retain their distinct treatment.

## Inventory and limits

Searched canonical skills and scripts for bold-colon definitions and Subject anchors; inspected the recognized finding-anchor set against commit/PR report contracts. Ran the complete checker across all 82 packages, including 41 severity-bearing packages, to challenge false rejection of unrelated bold definitions and mixed severity/classification sections. Existing tests cover headings, code wrappers, inline rubrics, sentinels, confidence, legacy-input prose, declaration locality and domain artifact statuses.

Refreshed the open sibling inventory: #96, #140 and #147. Inspected the full paginated changed-file lists for #96 and #140. Neither contains a projection of scripts/check-skill-vocabulary.py or its regression suite. The #96 prompt-grader helper checks a different protocol; #140 implements a domain completion report. Neither requires propagation of this parser patch. Untracked experimental artifacts remain excluded.

All 44 regression tests pass. The checker passes on all canonical packages. No skill source changed, so no new Waza skill check or CAIE draft audit is required for this checker-only patch. Prior Waza advisories and live-model limitations remain. Independent review was not performed because the comparable current-model ceiling could not be verified; review was local. No live model/API call ran.

## Equivalence-Class Audit Report
Triggering finding: bold-colon rubric labels and the Subject finding anchor bypassed vocabulary validation.
Locked audit scope: scripts/check-skill-vocabulary.py, scripts/test_skill_vocabulary.py, their canonical format/anchor consumers and available open sibling PR inventories, at the source fingerprint above.
Output depth: standard
Verdict: CLEAN
Severity: NONE

| Axis | Candidate | Presence | Disposition | Evidence |
|------|-----------|----------|-------------|----------|
| Opposite Bound | Complete and incomplete rubrics | absent | n/a | Both colon placements accept complete rubrics and reject removal of each level. |
| Sibling Parameter/Field | Report anchors | absent | n/a | All eight recognized anchors reject the explicit legacy-label set. |
| Mirror Call Site/Use Site | Formatted bullet definitions | absent | n/a | Canonical package scan passes after bold normalization; code and heading regressions retain coverage. |
| Inverse Operation | Acceptance versus rejection | absent | n/a | Canonical Subject severity/note accepted; obsolete values rejected. |
| Type/Schema Narrowing | Literal severity members | absent | n/a | Unknown uppercase and lowercase levels are validated rather than ending the active rubric. |
| Validation vs Normalization/Sanitization | Bold-colon presentation | absent | n/a | Presentation removal precedes bullet matching; enum validation remains declaration-local. |
| Happy/Error/Retry/Cancel Path Twin | Valid versus invalid declarations | absent | n/a | Complete, missing-level and extra-unknown cases exercise success and failure. |
| Race/Shared-State Twin | Runtime shared state | n/a — structurally inapplicable | n/a | No concurrent runtime mutation introduced. |
| Permission/Authorization Class | Authority boundary | n/a — structurally inapplicable | n/a | Checker remains read-only and issues no model/API calls. |
| Observability Twin | Diagnostic category | absent | n/a | Tests assert missing-level, invalid-literal and obsolete-output diagnostics. |
| Resource Cleanup | Temporary fixtures | absent | n/a | Existing TemporaryDirectory and finally-root restoration remain unchanged. |
| Contract Symmetry | Source rubric and recognized anchors | absent | n/a | test-suite-audit rubric and commit-message-quality report anchors are covered. |
| Equivalence by Naming | Subject/Title and sibling anchors | absent | n/a | Regression iterates the explicit eight-anchor contract. |
| Test Mirror | Positive and negative probes | absent | n/a | Three new regression methods cover the boundaries; old defects were reproduced before correction. |
| Empty/Sentinel Equivalence | Missing levels and permitted notes | absent | n/a | Complete README cannot fill omissions; notes and prior sentinel tests remain accepted. |
| Async/Sync or Mode Twin | Markup representations | absent | n/a | Inner/outer colon forms plus prior confidence and mixed-section paths are checked. |
| Documentation/Spec Prose Twin | Maintainer claims | absent | n/a | Guide already requires declaration-local markup normalization; PR text refreshed to current tests/hash. |
| Cache/Projection/Source-of-Truth Twin | Sibling checker copies | absent | n/a | Open sibling changed-file inventories contain no checker/test projection. |

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

## Adversarial Review Report
Verdict: CLEAN
Target: Checker remediation at `157583037d05c2c18f234f7754a85134ecb685d80f8934e4559915c8e9225d27`.
Intended behavior: Validate the governing rubric regardless of bold-colon placement and reject obsolete severity entries on every supported finding anchor.
Evidence basis: Red/green regression results, all-package checker run, source diff and canonical format/anchor inventory.
What works: Complete unrelated declarations cannot satisfy a partial rubric; appended unknown labels cannot be skipped; valid Subject entries and notes remain accepted.
Assumptions: This remains a checker for documented literal forms, not a general Markdown parser.
Findings: None
Adversarial tests: None
Mitigations / acceptance criteria: None
Residual risk: Static patterns do not prove semantic rubric equivalence, and no independent or live-model review was performed.

## Pre-Review Self-Audit Report

- Change intent: Close formatting and finding-anchor bypasses in the vocabulary checker.
- Scope audited: Two Python files and this evidence report; existing skill instruction bytes unchanged.
- Project checks discovered: Checker, Python regression suite and diff checks — run.

| # | Checklist item | Status | Notes |
|---|----------------|--------|-------|
| 1 | Diff hygiene | pass | No debug output, unrelated edits or temporary files staged. |
| 2 | Scope | pass | Each hunk fixes or documents the two review defect classes. |
| 3 | Tests | pass | Reproduced old failures; all 44 tests pass with the correction. |
| 4 | Contracts | pass | Existing authoring grammar is enforced; no skill output contract changes. |
| 5 | Commit atomicity | pass | One focused checker fix with standalone motivation. |
| 6 | Description accuracy | pass | PR update distinguishes current checker evidence from prior instruction reviews. |
| 7 | Project checks | pass | Targeted suite, all-package scan and diff checks completed. |
| 8 | Reviewer anticipation | pass | Parser comment explains inner/outer colon normalization; report preserves limits. |
| 9 | Repeated-pattern consistency | n/a | No repeated templated instruction edit; equivalent parser forms were audited separately above. |

### Findings

Findings: None

### Outstanding before requesting review

- None

Verdict: CLEAN
