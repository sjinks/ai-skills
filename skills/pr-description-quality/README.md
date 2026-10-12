# pr-description-quality

> Prepare or validate one PR title and body, including before opening/updating a PR within a larger task; return copy-ready text and an evidence-backed quality report.

This skill checks description quality without publishing PRs, executing checks, reviewing implementation correctness or authoring commit messages. It honors selected templates and title rules, covers the whole supplied change and reconciles final behavior with commit-history claims.

Draft/rewrite creates or repairs text; validate preserves safe supplied text and reports defects. Every mode removes sensitive content without treating removal as original compliance. Missing required input or unresolved required template/rule selection returns a five-line BLOCK report with a sanitized Disclosure line, including when sensitive content co-occurs; missing author facts produces a full CONCERNS report. Optional unknown issue links are omitted; validation claims retain outcomes and evidence boundaries.

The report preserves CLEAN/CONCERNS/BLOCK and template/default, with compliant/rewritten/noncompliant/needs-author-input statuses. Findings distinguish errors, unresolved facts and informational convention/structure evidence. Newly drafted/repaired parts yield CONCERNS even when emitted text passes. CLEAN requires both parts to be compliant and no forbidden content found, including in supplied source outside the title/body.

Without caller/repository convention rules, a strict majority of all usable supplied historical PR titles must match the core conventional grammar to select conventional mode; ties, minorities and empty history select plain.

Conventional title types follow the stated primary outcome; unresolved mixed-type ties use a fixed priority order after caller/repository rules. Caller-supplied heading/checklist structures are templates and use Structure: template; default describes only the unreplaced default headings.

## Files

- [`SKILL.md`](SKILL.md) — activation, workflow, decisions and completion gates.
- [`references/evidence-and-structure.md`](references/evidence-and-structure.md) — scope, validation evidence, history, templates and conventions.
- [`references/report-and-examples.md`](references/report-and-examples.md) — report serialization, reduced failure form and decision examples.
