# pr-description-quality

> Draft, rewrite or assess a PR title and body with reviewer-useful context, honest evidence and repository conventions.

The skill supports whole-PR work and explicitly requested title-only or body-only operations. Review/audit without requested repairs preserves safe text; explicit repair or audit-and-rewrite produces corrected text. It does not publish PRs, execute checks or review implementation correctness.

Descriptions explain the problem, impact and approach without requiring the linked issue or task conversation. They cover evidenced compatibility effects, changed failure behavior and consequential tradeoffs. Alternatives appear only when needed to explain a consequential choice or required by the caller/template. Missing required rationale needs author input; optional unknowns are omitted.

Detail scales to the change: a short paragraph is enough for one outcome. Default headings are optional. Required and unmarked template elements are preserved; explicitly optional empty sections are omitted unless the caller requests retention. Caller/repository conventions override house title defaults.

Testing/Validation sections are optional unless required. Omit routine CI/check inventories, process summaries and editing chronology. Include verification details only when they explain changed behavior, risk, limitations or reproduction, directly support a central claim beyond routine CI status, or meet a caller/template requirement. Retain material failures and consequential gaps. Missing routine evidence alone needs neither author input nor a disclaimer.

For testing/CI changes, discuss automated/manual or fixture/live coverage only when affected. Explain removed automated coverage and its rationale. A pure unit-test assertion change does not require a live-verification discussion.

The report separates action from quality. Passing created/repaired text is rewritten/pass and can be CLEAN; corrected defects remain in Findings. Unresolved failures or original disclosures yield CONCERNS. Missing operation input or unresolved relevant required rules/templates yield BLOCK. Unrequested parts are not-assessed, with empty text fences; a partial verdict covers only the requested part.

Sensitive content is excluded in every mode. Original disclosures still prevent CLEAN even when corrected or outside the requested parts. Evidence limitations are reported without inventing successful execution. Static regression cases support maintenance; they are not measured model evaluations.

## Files

- [`SKILL.md`](SKILL.md) — modes, scope, core behavior, decisions and report markers.
- [`references/evidence-and-structure.md`](references/evidence-and-structure.md) — change evidence, content relevance and template/default structure.
- [`references/title-conventions.md`](references/title-conventions.md) — title style, history selection, type ties and breaking intent.
- [`references/report-and-examples.md`](references/report-and-examples.md) — full/partial report serialization, reduced BLOCK, decision examples and static regression cases.
