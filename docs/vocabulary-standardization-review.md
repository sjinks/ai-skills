# Vocabulary standardization review

Source SHA-256: `03563caed2adce2d529fe2c5d66af315c384e41ecafd1ae5de14fdba04626eb8`.

Hash scope: all canonical skill files plus AGENTS.md, README.md and docs/skill-vocabulary.md (294 files). Sort repository-relative paths; hash each path, NUL, exact file bytes, NUL using SHA-256. Exclude this evidence report to avoid self-reference. All reviews below bind to this unchanged source snapshot.

## Final scope and decision

The PR standardizes severity, classification versus disposition, missing-information markers, coverage and finding lifecycle across 40 packages. Domain verdicts and explicit legacy-input mappings remain distinct. Each skill retains its operational rules locally.

Remove the bespoke vocabulary validator and its regression suite. The validator attempted to infer semantic contracts from Markdown presentation and field names. Repeated review findings showed both false acceptance and false rejection. Its tests described that partial parser, not agent adherence to the vocabulary contracts. Keeping it would add a second, incomplete contract implementation to maintain.

The shared vocabulary guide remains the authoring convention. Existing project instructions still require source-to-template/reference/documentation sweeps and skill validation. The maintenance section now requires direct comparison of each governing contract and its projections; a search or tool pass is not evidence of semantic consistency. No replacement parser, checker dependency or CI gate was added. This deliberately removes automated vocabulary lint coverage.

## Review intake and resolution

Fetched available discussion timeline, submitted reviews including suppressed/previously missed text, and all inline threads for PR #147 before editing. The latest review contains seven validator findings, all eliminated by removing the validator rather than extending its parser.

| Comment | Defect class | Final resolution |
|---|---|---|
| 4576606634 | Coverage recognition depended on the first enum member. | No coverage parser remains; review the complete local coverage contract and its slots. |
| 4576606654 | Obsolete summary matching omitted positive counts. | No summary-count regex remains; exact summary labels remain defined by each package. |
| 4576606666 | Malformed severity alternatives were treated as prose. | No severity-list parser remains; review literal alternatives against their governing contract. |
| 4576606685 | Lifecycle checks missed output-table cells. | No field-only lifecycle check remains; the guide explicitly includes structured fields and tables. |
| 4576606702 | Markdown wrappers bypassed obsolete-entry checks. | No obsolete-entry matcher remains; review formatting as presentation. |
| 4576606733 | Valid bulleted fields were collected as rubric levels. | No overlapping field/rubric collectors remain. |
| 4576606747 | Prose rubrics depended on repeating a keyword. | No keyword-dependent prose-rubric recognizer remains. |

## Inventory and validation

- Inspected the entire removal diff and the surviving authoring rule, README summary and maintenance guide. Consolidated the previous parser-specific reports into this final record.
- Searched AGENTS.md, README.md, docs, scripts and .github for the removed executable/test paths and obsolete report links. No active references remain after consolidation.
- Skill sources are byte-identical to d8359252ca6236a4cdbab1d07ac9d76db600ecaf; the 40 package CAIE reports in the PR description still assess those same instruction bytes. The previous direct sweep covered rules, outputs, checklists, conditional references, examples, README descriptions and consumers. Existing compatibility-symlink comparisons cover those unchanged bytes.
- Refreshed open sibling inventory: #96, #140 and #147. Inspected the full changed-file inventories for #96 and #140; neither contains this validator, its tests, the vocabulary guide or these review reports. No sibling propagation is needed for removal. The earlier companion fixture commit c02bfcb remains in #96, unchanged.
- Git diff checks pass. No new behavioral tests are needed for deleting this optional read-only tool and its own tests; skill output behavior is unchanged. No live model/API evaluation ran.
- Earlier Waza checks on the unchanged skill files found passing links and non-exempt specification checks, with existing advisory failures. Those baseline limitations remain; this is not an all-checks-green or full-PR merge-readiness claim. A removed check’s earlier passing test count is not current validation.
- Review is local. Independent review was not performed because the routing table’s comparable current-model ceiling could not be verified. Static model compatibility is unmeasured.

## Equivalence-Class Audit Report
Triggering finding: the optional vocabulary parser admits invalid contracts and rejects a valid contract.
Locked audit scope: validator/test removal, surviving project vocabulary instructions and documentation, and available sibling PR projections at the source fingerprint above.
Output depth: standard
Verdict: CLEAN
Severity: NONE

| Axis | Candidate | Presence | Disposition | Evidence |
|------|-----------|----------|-------------|----------|
| Opposite Bound | Acceptance and rejection | absent | n/a | Both false-accept and false-reject paths are removed with the parser. |
| Sibling Parameter/Field | Required labels and enums | absent | n/a | Shared definitions and local package output fields remain unchanged. |
| Mirror Call Site/Use Site | Tool invocations | absent | n/a | Project rule, root README and maintenance guide no longer invoke the removed tool. |
| Inverse Operation | Input normalization versus output | absent | n/a | Explicit input mappings remain local; removal changes no emitted values. |
| Type/Schema Narrowing | Coverage and lifecycle schemas | absent | n/a | No inference layer remains; existing local domains are preserved. |
| Validation vs Normalization/Sanitization | Markdown formatting | absent | n/a | Maintenance review explicitly treats formatting as presentation. |
| Happy/Error/Retry/Cancel Path Twin | Parser branches | absent | n/a | Success, malformed-list and insufficient-context parser paths are all deleted. |
| Race/Shared-State Twin | Runtime shared state | n/a — structurally inapplicable | n/a | No runtime shared state changes. |
| Permission/Authorization Class | Review authority | absent | n/a | No new execution or risk-acceptance authority is granted. |
| Observability Twin | Validation claims | absent | n/a | PR description and this record disclose removed automated lint coverage. |
| Resource Cleanup | Parser-owned tests | absent | n/a | The tool’s own regression suite is removed with the tool. |
| Contract Symmetry | Rules and projections | absent | n/a | Governing vocabulary rules remain; script requirements and claims are removed together. |
| Equivalence by Naming | Similar checker paths | absent | n/a | Workspace search and sibling inventories contain no counterpart requiring removal. |
| Test Mirror | Deleted test suite | absent | n/a | No orphaned test import or command remains. |
| Empty/Sentinel Equivalence | None/unknown/not-assessed/n/a | absent | n/a | Their definitions and local representations are preserved. |
| Async/Sync or Mode Twin | Review and runtime use | absent | n/a | The guide governs authoring; self-contained installed skill behavior is unchanged. |
| Documentation/Spec Prose Twin | Obsolete reports and references | absent | n/a | Previous parser reports are replaced by this current scoped record. |
| Cache/Projection/Source-of-Truth Twin | Generated copies | absent | n/a | Canonical skills and generated-path identity are unchanged; experimental artifacts remain excluded. |

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

## CAIE audit: project vocabulary rule

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

## CAIE audit: maintenance guide

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

# Instruction Quality Audit

Audit: Project vocabulary-maintenance path

## Audit Scope

- Mode: path
- Status: completed
- Effective instruction files: AGENTS.md shared vocabulary and review/validation rules; docs/skill-vocabulary.md. Root README compared as documentation.
- Mutually exclusive paths: Package-specific domain and insufficient-context reports retain their existing contracts.
- Trusted custom diagnostics: Repository projection-consistency requirements.
- Limitations: Audit of the changed authoring path at the fingerprint above; unrelated domain rules are context. Local static review only.

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

## Adversarial Review Report
Verdict: CLEAN
Target: Vocabulary-maintenance path and tool removal at the source fingerprint above.
Intended behavior: Keep the shared contracts and semantic review requirements without maintaining a partial Markdown validator.
Evidence basis: Final diff, deleted-path/reference search, unchanged canonical skill bytes and sibling inventory.
What works: No deleted-tool requirement remains; domain outputs, legacy-input mappings and local evidence gates remain intact.
Assumptions: Maintainers apply the existing contract-projection review workflow.
Findings: None
Adversarial tests: None
Mitigations / acceptance criteria: None
Residual risk: Automated vocabulary lint coverage is deliberately removed; semantic review and model adherence remain unmeasured by static checks.

# Agent/Skill Readiness Audit

Audit: Project vocabulary-maintenance path

## Audit Scope

- Artifact type: Persistent instructions
- Mode: path
- Status: completed
- Target models: GPT-6 Luna; Claude Haiku 5.5
- Target runtimes: Not supplied
- Files included: AGENTS.md shared vocabulary/review rules; docs/skill-vocabulary.md; README documentation projection.
- Files excluded: Unchanged package-domain implementations and experimental artifacts — outside the changed authoring path.
- Limitations: Static review at the source fingerprint above; no measured model compatibility or independent review. No automated vocabulary parser remains.

## Readiness Ratings

| Area | Rating | Main risk |
|---|---:|---|
| Discovery and delegation | 4 | Guide depends on the explicit project-rule link. |
| Instruction architecture | 5 | None. |
| Operational completeness | 4 | Semantic review requires inspecting all applicable projections. |
| Model and runtime portability | 4 | Compatibility is assessed statically, not measured. |
| Maintainability and evaluability | 4 | Vocabulary consistency is reviewed without automated lint coverage. |

## Material Findings

None.

## Target-Model Compatibility

| Model | Verdict | Main risk | Required adaptation |
|---|---|---|---|
| GPT-6 Luna | Suitable with limitations | No measured compatibility evaluation. | None. |
| Claude Haiku 5.5 | Suitable with limitations | No measured compatibility evaluation. | None. |

## Priority Changes

None.

Verdict: Ready with limitations
