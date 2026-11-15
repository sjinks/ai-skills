# Vocabulary standardization review

Source SHA-256: `9fed80511413bf127a33e9d1616a2395ded84e16b16d9b6a9c822f72d671b0eb`.

Hash scope: all canonical skill files plus AGENTS.md, README.md and docs/skill-vocabulary.md (294 files). Sort repository-relative paths; hash each path, NUL, exact file bytes, NUL using SHA-256. Exclude this evidence report to avoid self-reference. All reviews below bind to this unchanged source snapshot.

## Final scope and decision

The PR standardizes severity, classification versus disposition, missing-information markers, coverage and finding lifecycle across 40 packages. Domain verdicts and explicit legacy-input mappings remain distinct. Each skill retains its operational rules locally.

Remove the bespoke vocabulary validator and its regression suite. The validator attempted to infer semantic contracts from Markdown presentation and field names. Repeated review findings showed both false acceptance and false rejection. Its tests described that partial parser, not agent adherence to the vocabulary contracts. Keeping it would add a second, incomplete contract implementation to maintain.

The shared vocabulary guide remains the authoring convention. Existing project instructions still require source-to-template/reference/documentation sweeps and skill validation. The maintenance section now requires direct comparison of each governing contract and its projections; a search or tool pass is not evidence of semantic consistency. No replacement parser, checker dependency or CI gate was added. This deliberately removes automated vocabulary lint coverage.

## Review intake and resolution

Fetched the available discussion timeline, submitted reviews including suppressed/previously missed text, and all inline threads for PR #147 before editing. The preceding seven parser findings were resolved by removing the parser. The current review identifies two contract/projection defects:

| Comment | Defect class | Affected projections and resolution |
|---|---|---|
| 4576707182 | First-match action routing conflated production corrections with verification-only work. | SSRF core, disposition template order, README and shared vocabulary guide now route supported implementation/policy/documentation corrections to fix-now even when regression verification is missing. add-verification is restricted to findings whose only required change is verification. |
| 4576707206 | A conditional matrix retained an obsolete coverage vocabulary. | Unicode adversarial matrix now uses the core four-state coverage rules, their precedence and unassessed-subpart disclosure. Accepted risk stays with the finding or the core-permitted residual-risk disclosure; acceptance does not satisfy an unmet requirement. README synchronized. |

Manual semantic walkthroughs (static reasoning, not model/runtime execution):

| Scenario | Required result under the final rules |
|---|---|
| Confirmed DNS bypass plus missing regression test | fix-now; correction includes the required regression verification. |
| Confirmed redirect bypass plus missing regression test | fix-now; add-verification cannot substitute for correcting the bypass. |
| Known correct behavior lacks its required test; no other correction needed | add-verification. |
| Missing policy decision prevents choosing a correction | clarify. |
| Documented accountable-owner acceptance of this finding/scope | retain-accepted under the existing first-match rule. |
| Agreed owned deferral with rationale/plan | defer-with-owner under the existing first-match rule. |
| Missing claimed acceptance or deferral evidence | clarify; no invented acceptance. |
| Applicable control or test demonstrably fails | gap. |
| Required assessment/evidence unavailable | not-assessed; no unqualified CLEAN result. |
| Class does not apply | n/a with reason. |
| Inspected evidence satisfies every applicable part | covered. |
| Known gap and unavailable assessment of another subpart | gap plus explicit unassessed-subpart disclosure; no unqualified CLEAN result. |
| Owner accepts an unmet requirement | gap remains; record acceptance on the finding or where the core permits under Residual risk. |
| Test plan exists but required regression tests have not run | The plan alone cannot satisfy the core Tests checklist item. |

## Inventory and validation

- Inspected the final contract diff and surviving authoring rule, package README summaries and maintenance guide. The removed parser remains absent; this record consolidates current evidence.
- Searched AGENTS.md, README.md, docs, scripts and .github for the removed executable/test paths and obsolete report links. No active references remain after consolidation.
- Carry forward earlier package assessments only for instruction files unchanged since d8359252ca6236a4cdbab1d07ac9d76db600ecaf. The SSRF core and README, Unicode adversarial matrix and README, and shared vocabulary guide changed in the follow-up. The current SSRF/Unicode package-path CAIE, instruction-quality and readiness reports below cover those corrections; the current authoring-path reports cover the guide. Earlier direct-sweep and compatibility-symlink evidence applies only to unchanged files; the four changed canonical skill files were compared again after the follow-up.
- Refreshed open sibling inventory: #96, #140 and #147. Inspected full changed-file inventories. #140 has no related package. At immutable #96 head c02bfcb889ac6bd693909098b0fa22d03d589962, read both changed SSRF/Unicode fixtures and searched both complete suite directories for disposition and coverage labels. Graders require substantive risks and report sections, not the conflicting action order or obsolete coverage enum. No fixture change is needed. The earlier companion fixture commit remains unchanged.
- Git diff checks pass. Static semantic walkthroughs cover both reported failures and their neighboring acceptance, deferral, clarification, verification-only and coverage branches. No replacement checker was added and no live model/API evaluation ran.
- Reran Waza on both final affected packages and exact pre-change package snapshots: SSRF 3/3 links, Unicode 5/5 links; non-exempt specification checks pass. No new advisory failures. Existing SSRF over-specificity and body-structure advisories remain. Repository-exempt token/frontmatter/missing-suite/complexity advisories are not blockers. This is not an all-checks-green or full-PR merge-readiness claim. Removed checker test counts are not current validation.
- Review is local. Independent review was not performed because the routing table’s comparable current-model ceiling could not be verified. Static model compatibility is unmeasured.

## Equivalence-Class Audit Report
Triggering finding: SSRF first-match routing masked a production correction, and a Unicode matrix projected obsolete coverage states.
Locked audit scope: the two affected canonical packages, shared vocabulary guide, related workspace projections and open sibling PR inventories at the source fingerprint above.
Output depth: standard
Verdict: CLEAN
Severity: NONE

| Axis | Candidate | Presence | Disposition | Evidence |
|------|-----------|----------|-------------|----------|
| Opposite Bound | Implementation correction versus verification-only work | absent | n/a | Supported corrections win; verification-only findings still select add-verification. |
| Sibling Parameter/Field | Disposition and classification slots | absent | n/a | Classification remains evidence kind; action enum/order matches the source rule. |
| Mirror Call Site/Use Site | Core/matrix/README/guide uses | absent | n/a | All add-verification occurrences and the Unicode matrix projection were inspected. |
| Inverse Operation | Coverage versus acceptance | absent | n/a | Acceptance never converts gap to covered; no inverse inference of safety. |
| Type/Schema Narrowing | Four coverage states | absent | n/a | Unicode matrix links to the core state contract without a richer incompatible enum. |
| Validation vs Normalization/Sanitization | Presentation-to-semantic mappings | absent | n/a | No old missing/not-applicable/accepted-tradeoff coverage translation remains. |
| Happy/Error/Retry/Cancel Path Twin | Action-selection branches | absent | n/a | Correction plus missing tests, verification-only and clarification cases were walked through. |
| Race/Shared-State Twin | Runtime shared state | n/a — structurally inapplicable | n/a | No concurrency implementation changes. |
| Permission/Authorization Class | Owner acceptance/deferral authority | absent | n/a | Existing evidence/owner prerequisites and lack of execution authority are retained. |
| Observability Twin | Residual risk disclosure | absent | n/a | Unassessed subparts and accepted risks stay explicit in their permitted slots. |
| Resource Cleanup | Runtime resources | n/a — structurally inapplicable | n/a | No allocation or cleanup implementation changes. |
| Contract Symmetry | Rules and output slots | absent | n/a | SSRF procedure, disposition order, coverage rules and template were compared. |
| Equivalence by Naming | Adversarial matrices | absent | n/a | SSRF matrix already uses the four states; Unicode counterpart corrected. |
| Test Mirror | Sibling evals and static scenarios | absent | n/a | Inspected sibling fixtures/directories; static walkthroughs cover both failure classes. |
| Empty/Sentinel Equivalence | gap/not-assessed/n/a/covered | absent | n/a | Known gaps, unavailable evidence, structural inapplicability and satisfaction remain distinct. |
| Async/Sync or Mode Twin | Matrix-loaded and normal review paths | absent | n/a | Conditional matrix path now shares the same coverage contract; full/reduced templates remain valid. |
| Documentation/Spec Prose Twin | Shared guide and package README files | absent | n/a | Guide and READMEs state the corrected routing/coverage boundaries. |
| Cache/Projection/Source-of-Truth Twin | Canonical versus compatibility paths | absent | n/a | Changed skill files compare equal through the generated-path symlink. |

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
Target: Vocabulary-maintenance path, SSRF disposition routing and Unicode matrix coverage at the source fingerprint above.
Intended behavior: Route supported corrections ahead of verification-only work, and preserve one coverage contract across core and matrix paths.
Evidence basis: Final contract/projection diff, equivalence sweep, static scenario walkthroughs, Waza snapshot comparison and sibling inventory.
What works: A known implementation bypass cannot select add-verification solely because its test is missing. The Unicode matrix cannot classify missing evidence as a defect or accepted risk as completed coverage.
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


## Current package-path CAIE audits

### ssrf-outbound-fetch-review

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

### unicode-text-security-review

```text
CAIE mode: audit
CAIE artifact: None.
CAIE findings: None.
CAIE status: Clean
```

## Current package-path instruction-quality reports

# Instruction Quality Audit

Audit: skills/ssrf-outbound-fetch-review disposition/coverage migration

## Audit Scope

- Mode: path
- Status: completed
- Effective instruction files: skills/ssrf-outbound-fetch-review/SKILL.md and its adversarial matrix; README and shared guide compared as projections.
- Mutually exclusive paths: Normal/full versus insufficient-context reports; conditional matrix loading.
- Trusted custom diagnostics: Repository contract/projection requirements.
- Limitations: Static review of the changed decision/coverage path at 9fed80511413bf127a33e9d1616a2395ded84e16b16d9b6a9c822f72d671b0eb; unchanged domain factual claims are context, not a fresh domain audit. No independent or measured model review.

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

---

# Instruction Quality Audit

Audit: skills/unicode-text-security-review disposition/coverage migration

## Audit Scope

- Mode: path
- Status: completed
- Effective instruction files: skills/unicode-text-security-review/SKILL.md and its adversarial matrix; README and shared guide compared as projections.
- Mutually exclusive paths: Normal/full versus insufficient-context reports; conditional matrix loading.
- Trusted custom diagnostics: Repository contract/projection requirements.
- Limitations: Static review of the changed decision/coverage path at 9fed80511413bf127a33e9d1616a2395ded84e16b16d9b6a9c822f72d671b0eb; unchanged domain factual claims are context, not a fresh domain audit. No independent or measured model review.

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

## Current package-path readiness reports

# Agent/Skill Readiness Audit

Audit: skills/ssrf-outbound-fetch-review disposition/coverage migration

## Audit Scope

- Artifact type: Agent Skill
- Mode: path
- Status: completed
- Target models: GPT-6 Luna; Claude Haiku 5.5
- Target runtimes: Not supplied
- Files included: skills/ssrf-outbound-fetch-review/SKILL.md and applicable adversarial matrix; README and shared guide cross-checked.
- Files excluded: Unchanged domain semantics and experimental/generated copies — outside this correction path.
- Limitations: Static assessment at 9fed80511413bf127a33e9d1616a2395ded84e16b16d9b6a9c822f72d671b0eb; no measured model compatibility or independent review. Existing Waza advisories remain; this is not a whole-PR merge-readiness verdict.

## Readiness Ratings

| Area | Rating | Main risk |
|---|---:|---|
| Discovery and delegation | 4 | Activation unchanged; adherence unmeasured. |
| Instruction architecture | 4 | Conditional references must share their core contract. |
| Operational completeness | 4 | Static scenarios do not establish model behavior. |
| Model and runtime portability | 4 | Compatibility is not measured. |
| Maintainability and evaluability | 4 | Semantic consistency is reviewed without a bespoke parser. |

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

---

# Agent/Skill Readiness Audit

Audit: skills/unicode-text-security-review disposition/coverage migration

## Audit Scope

- Artifact type: Agent Skill
- Mode: path
- Status: completed
- Target models: GPT-6 Luna; Claude Haiku 5.5
- Target runtimes: Not supplied
- Files included: skills/unicode-text-security-review/SKILL.md and applicable adversarial matrix; README and shared guide cross-checked.
- Files excluded: Unchanged domain semantics and experimental/generated copies — outside this correction path.
- Limitations: Static assessment at 9fed80511413bf127a33e9d1616a2395ded84e16b16d9b6a9c822f72d671b0eb; no measured model compatibility or independent review. Existing Waza advisories remain; this is not a whole-PR merge-readiness verdict.

## Readiness Ratings

| Area | Rating | Main risk |
|---|---:|---|
| Discovery and delegation | 4 | Activation unchanged; adherence unmeasured. |
| Instruction architecture | 4 | Conditional references must share their core contract. |
| Operational completeness | 4 | Static scenarios do not establish model behavior. |
| Model and runtime portability | 4 | Compatibility is not measured. |
| Maintainability and evaluability | 4 | Semantic consistency is reviewed without a bespoke parser. |

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
