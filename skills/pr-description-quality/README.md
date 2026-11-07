# pr-description-quality

> Prepare or validate one PR title and body, including before opening/updating a PR within a larger task; return copy-ready text and an evidence-backed quality report.

This skill checks description quality without publishing PRs, executing checks, reviewing implementation correctness or authoring commit messages. It honors selected templates and title rules, covers the whole supplied change and reconciles final behavior with commit-history claims.

Bodies answer the reviewer's core questions: what is the issue, why does it matter, and how does the solution address it, including evidenced breaking changes and other concerns? Alternatives and reasons for rejecting them are included when needed to explain a consequential choice or required by the caller/template. Optional unknown alternatives are omitted; missing required comparison facts need author input. These are content requirements within the selected template, not mandatory new headings. Testing supports that explanation.

Draft/rewrite creates or repairs text; validate preserves safe supplied text and reports defects. Every mode removes sensitive content without treating removal as original compliance. Missing required input or unresolved required template/rule selection returns a five-line BLOCK report with a sanitized Disclosure line, including when sensitive content co-occurs; missing author facts produces a full CONCERNS report. Optional unknown issue links are omitted; included validation claims retain outcomes and evidence boundaries.

Bodies explain the problem, observable before/after behavior, consequential differences between modes, representative test/example input conditions and expected outcomes, and evidenced compatibility effects. Illustrative examples are distinguished from executed tests. Routine successful check summaries, counts, exact tool versions, revision hashes, process-review summaries, agent review verdicts and generic review/evaluation disclaimers are omitted by default. Explicit caller/template requirements and details needed to explain a material risk, limitation or reproduction requirement override that default. Except for explicit caller/template requirements and the existing absent-evidence or confirmed-no-checks notices, limitations identify the specific claim they qualify or unverified behavior and its practical consequence; missing review/evaluation alone is insufficient. Material failures and verification gaps remain visible; the quality report separately records source-evidence limitations. Supplied routine results still count as evidence even when omitted from the body. Required internal audit records belong in the task handoff unless the body independently needs them under these rules.

The report preserves CLEAN/CONCERNS/BLOCK and template/default, with compliant/rewritten/noncompliant/needs-author-input statuses. Findings distinguish errors, unresolved facts and informational convention/structure or source-evidence limits. Input/information evidence limits do not alone force CONCERNS. Full disclosure findings retain sanitized locations; reduced BLOCK reports only the generic Disclosure signal without locations. Newly drafted/repaired parts yield CONCERNS even when emitted text passes. CLEAN requires both parts to be compliant and no forbidden content found, including in supplied source outside the title/body.

When no required template is known, unavailable repository template context selects default body structure, without changing title mode; supplied title history remains usable when repository files are unavailable.

Without caller/repository convention rules, a strict majority of all usable supplied historical PR titles must match the core conventional grammar to select conventional mode; ties, minorities and empty history select plain.

Conventional title types follow the stated primary outcome; unresolved mixed-type ties use a fixed priority order after caller/repository rules. Caller-supplied heading/checklist structures are templates and use Structure: template; default describes only the unreplaced default headings.

## Files

- [`SKILL.md`](SKILL.md) — activation, workflow, decisions and completion gates.
- [`references/evidence-and-structure.md`](references/evidence-and-structure.md) — scope, validation evidence, history, templates and conventions.
- [`references/report-and-examples.md`](references/report-and-examples.md) — report serialization, reduced failure form and decision examples.
