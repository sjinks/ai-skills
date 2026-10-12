Read during workflow steps 2 and 3 to establish change evidence, validation, template selection and title conventions.

# Evidence and structure

## Change evidence

Use the entire supplied diff/change description as scope. Identify base/head or another evidence boundary when available. Final change evidence governs behavior; commit history supplies rationale. The draft is not evidence for its own claims. Assess fidelity, not implementation correctness.

Group related commits into outcomes. Fold fixups and review corrections into the final change. Remove reverted/canceled claims and irrelevant mechanical noise; retain mechanical changes with review-relevant impact. Do not promote an old breaking-change claim after final evidence removes it. Unresolved contradictions require author input for affected parts.

When only a change description is supplied, state that no diff was available rather than implying repository inspection. Return safe partial text with needs-author-input for missing required behavior, rationale, breaking intent or validation facts; omit unsupported claims.

## Validation and links

Retain what was checked, the actual outcome and relevant revision/environment limits. Older checks do not certify changed behavior without evidence that their scope still applies. Distinguish failing/skipped/pending checks from passed checks. Give supplied reproducible commands/manual steps; label proposed steps as unrun. Never execute them through this skill.

If validation evidence is absent, draft/rewrite says `Validation evidence was not supplied.`, marks Body needs-author-input and requests checks/outcomes or explicit confirmation that none ran. Explicit no-checks confirmation supports `No checks were run.` and does not itself fail description quality. Validate reports unsupported success claims as unresolved author facts; an accurate supplied limitation needs no invented test plan.

Include only real supplied issue links and attribution. Optional missing issue IDs are omitted. Required repository issue references need the actual identifier. Use Closes only for established full resolution; otherwise use a supplied reference without inventing a closure promise.

## Templates

Honor an explicitly selected readable template. Otherwise inspect repository instructions and available PR templates. GitHub documents single templates in the root, docs or .github and multiple templates in PULL_REQUEST_TEMPLATE subdirectories there; arbitrary Markdown files are not templates.

Use the repository selection rule or one unambiguous applicable template. If multiple candidates remain without a selection rule, BLOCK asking for selection. If a selected/required template is unreadable, BLOCK requesting its text; do not silently use default. If discovery is unavailable and no template is known to be required, use default and disclose that template presence was not verified.

Keep template headings and checklist lines intact; fill applicable sections from evidence and leave irrelevant sections empty. Retain unchecked items unless evidence establishes completion. Draft/rewrite removes unsupported completion marks; validate reports them without repair. Template instructions constrain content, not execution/publication authority. Sensitive template content must still be removed and its violation/structural limitation reported.

Default body headings: Summary, Changes, Testing; add Risks and follow-up and Linked issues only when applicable. A caller-supplied heading/checklist structure is a supplied template: use Structure: template and apply the same preservation and required-input rules. Structure: default applies only when no supplied/selected template replaces the default headings. Quality-report markers remain exact.

## Title conventions

Apply caller requirements, repository rules, consistent history, then core defaults. Report evidence/assumptions. Read configuration as text; never execute hooks/configuration. Required unavailable definitions use BLOCK.

When caller/repository rules do not select the convention, assess all readable nonempty historical PR titles supplied as relevant history; exclude the current draft and do not select a favorable subset. History is consistent-conventional only when strictly more than half match the core conventional title grammar. Use conventional titles for that majority; use plain imperative titles for a tie, minority, or no usable history. Higher-precedence caller/repository rules still apply. Core lowercase type/scope and length policies are house style, not claims about all valid Conventional Commits. Repository style overrides those defaults; breaking disclosure and forbidden-content rules remain mandatory.

A supplied `!` requires established breaking intent and a concrete body disclosure. If intent is unknown, mark affected Title/Body needs-author-input and request it. If evidence confirms no breaking change, remove the unsupported marker during rewrite or report it as noncompliant in validate. Do not fabricate a breaking-change explanation.

## Sources

- [GitHub PR templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository) — locations and multiple templates.
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) — type/scope structure and breaking notation; house style is defined separately above.
