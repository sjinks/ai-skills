Read when Body is requested to select evidence, reviewer-useful content and template structure.

# Evidence and structure

## Change evidence

Use the entire supplied final diff/change description. History can explain rationale but cannot prove final behavior or successful execution. Remove reverted claims, fixup chronology and mechanical details unless they explain behavior or guide review. The draft is not evidence for its own factual claims. Use separately supplied author facts where available; request unresolved required behavior, impact or rationale.

Write for a reviewer who has not seen the conversation. Apply the core's Body principles to select outcomes before writing prose. Use concrete before/after outcomes for a bug fix when needed to understand the failure. Replace unexplained shorthand such as “fails closed” with the observable result.

Explain breaking changes, changed failure behavior and compatibility/migration effects established by evidence. When persistence determines whether migration is needed and that fact is unknown, request it. Do not invent migration safety or demand migration details without an evidenced compatibility effect.

Include alternatives when the caller/template requires comparison or the choice needs comparison to explain a consequential difference in behavior, compatibility, risk, operational burden or cost. Use evidenced options and reasons; missing required comparison facts need author input. Otherwise omit unknown alternatives without inventing deliberation.

Describe consequential differences between affected modes or operations. Do not enumerate unaffected modes. For testing/CI changes, explain changes in automated/manual or fixture/live verification only when affected. If automated coverage is removed, explain the evidenced reason and resulting tradeoff; a retained manual counterpart does not establish adequacy or rationale. A pure unit-test assertion change does not require a discussion of live services.

If no diff is available, report that evidence boundary under Input/information rather than implying repository inspection. An evidence limitation alone does not fail Body; unresolved required facts do.

## Relevance and verification

Apply this relevance rule to verification details, implementation details, commands and limitations: include them only when they explain changed behavior, a material risk/limitation, reproduction, directly supporting evidence beyond routine CI status, or a caller/template requirement. A limitation identifies the qualified claim or unverified behavior and its practical consequence unless the caller/template explicitly requests a status field.

Under the core's verification rule, omit routine successful build/lint/syntax/whitespace/unit-suite/CI summaries, assertion counts, exact versions and hashes, agent verdicts, process-review summaries, editing chronology and redundant instructions. A review verdict is not proof of correctness. Required internal audit records belong in the task handoff unless the body independently needs them under the relevance rule.

For example, successful execution with network facilities disabled can substantiate an offline-execution claim. Limit that observation to the exercised suite; do not assert that unrelated integration tests are offline. A generic unit-suite pass provides no equivalent offline evidence.

When included tests/examples explain behavior, state representative input conditions and expected outcomes rather than topic inventories. Identify illustrative examples; do not imply they ran. Preserve actual results and distinguish passed, failed, skipped, pending and proposed/unrun checks. Older checks apply only when evidence establishes that their scope remains valid. Never execute checks through this skill.

Retain material failures and verification gaps tied to changed behavior, even when routine successes are omitted. Routine pending CI, missing review or absent evaluation alone does not establish such a gap. Do not add generic missing-evidence or no-checks notices. Do not infer whether checks ran.

For example, an author-confirmed unrun replacement test suite leaves the runner migration unverified. That is a concrete gap; a successful compilation does not establish that the replacement suite runs. A routine migration with no evidenced prior failure does not need an invented failure story. Report-generation changes matter when supplied evidence identifies consumers that still require the removed reports. Do not claim those consumers were inspected unless they were available and read.

Missing routine validation evidence alone requires no author input. Draft/rewrite omits unsupported optional success claims and records the correction; request support only for retained claims or required fields. Validate preserves safe unsupported claims and marks Body needs-author-input until support arrives. A supported but irrelevant inventory remains a relevance violation in validate.

Include only real supplied issue links and attribution. Use Closes only for established full resolution. Omit optional unknown IDs; request an identifier only when required.

## Templates and structure

Honor an explicitly selected readable template. Otherwise inspect readable repository rules and available PR templates. If several candidates remain without a selection rule, BLOCK requesting selection. If a relevant selected/required template is unreadable, BLOCK requesting its text.

If discovery is unavailable and no template is known to be required, use default structure and record the assumption. This fallback does not select title conventions. For title-only operations, body-template discovery and selection are outside scope.

Preserve required headings/checklist fields. Treat unmarked template elements as required. Preserve explicitly optional elements only when they have relevant content or the caller requests retention; otherwise omit them. An explicit retention request permits an empty optional heading. Fill required sections from evidence; leave an irrelevant required section empty unless its template requires a value. Missing facts needed by required fields use needs-author-input. Do not infer completion marks; draft/rewrite removes unsupported marks and validate reports them without repair. Disclosure removal overrides template preservation.

A caller-supplied heading/checklist structure is a template. Use Structure: template for selected repository or caller templates. Use Structure: default otherwise. In default structure, use a short paragraph for one outcome; use Summary and Changes only when they separate useful topics. Testing, Risks and follow-up and Linked issues are optional headings when the content warrants them. Verification details may appear alongside the behavior they explain. Do not create headings or request evidence merely to fill a section.
