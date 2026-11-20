# pr-description-quality

> Draft, rewrite or assess a PR title and body with reviewer-useful context, honest evidence and repository conventions.

The skill supports whole-PR work and explicitly requested title-only or body-only operations. Review/audit without requested repairs preserves safe text; explicit repair or audit-and-rewrite produces corrected text. It does not publish PRs, execute checks or review implementation correctness.

Descriptions lead with the primary outcome and include the problem, impact and approach needed to understand it without the linked issue or task conversation. Content selection precedes report statuses. Supplied changes are checked for separate behavior, compatibility, licensing and verification effects; mechanics appear only when they explain an outcome, consequential choice or review focus. Maintenance changes do not need invented failure stories. Alternatives appear only when needed to explain a consequential choice or required by the caller/template. Missing required rationale needs author input; mechanical edits do not each need a reason.

Detail scales to the change: a short paragraph is enough for one outcome. Default headings are optional. Required and unmarked template elements are preserved; explicitly optional empty sections are omitted unless the caller requests retention. Caller/repository conventions override house title defaults.

For each PR body detail, require a reviewer decision it informs or an explicit requirement to include it in the body. Remove irrelevant details in draft/rewrite; flag them in validate without changing safe text. Keep internal records in the task handoff when either location is allowed and the records do not independently help the reviewer.

Testing/Validation sections are optional unless required. Include verification details only when they explain reproduction, support a specific behavioral claim beyond routine success, identify a material failure or gap, or meet a caller/template requirement. Otherwise omit them, including routine successful build, lint, test and CI results. Omit process summaries and editing chronology. Name the affected behavior and consequence of a gap. Missing routine evidence alone needs neither author input nor a disclaimer.

For testing/CI changes, discuss automated/manual or fixture/live coverage only when affected. Explain removed automated coverage and its rationale. A pure unit-test assertion change does not require a live-verification discussion.

The report separates action from quality. Passing created/repaired text is rewritten/pass and can be CLEAN; corrected defects remain in Findings. Unresolved failures or original disclosures yield CONCERNS. Missing operation input or unresolved relevant required rules/templates yield BLOCK. Unrequested parts are not-assessed, with empty text fences; a partial verdict covers only the requested part.

Sensitive content is excluded in every mode. Original disclosures still prevent CLEAN even when corrected or outside the requested parts. Evidence limitations are reported without inventing successful execution. Static regression cases support maintenance; they are not measured model evaluations.

Impact severities use `CRITICAL`, `HIGH`, `MEDIUM`, and `LOW`; task-specific statuses and decisions remain separate.

For independent review, include requirements or invariants needed to judge changed behavior that the PR diff, commit messages, and description do not already state. Ask for missing facts rather than inferring requirements from the implementation.

## Files

- [`SKILL.md`](SKILL.md) — modes, scope, core behavior, decisions and report markers.
- [`references/evidence-and-structure.md`](references/evidence-and-structure.md) — change evidence, content relevance and template/default structure.
- [`references/title-conventions.md`](references/title-conventions.md) — title style, history selection, type ties and breaking intent.
- [`references/report-and-examples.md`](references/report-and-examples.md) — full/partial report serialization, reduced BLOCK, decision examples and static regression cases.
