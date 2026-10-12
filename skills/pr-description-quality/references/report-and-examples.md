Read before serializing a report or checking mode, missing-input, disclosure and verdict examples.

# Report and examples

## Full report

Emit exactly one report with the core's ordered markers, no preamble/trailing prose. Full reports use CLEAN or CONCERNS, never BLOCK. Structure is template for repository-selected or caller-supplied heading/checklist structures, and default only for the unreplaced default body structure.

Fence Title as text and Body as markdown; use backtick fences longer than every backtick run in each payload. Preserve safe validation text, whitespace and literal angle brackets; fences are framing. For rewrite with only one supplied part, draft the other from usable change evidence; otherwise leave its fence empty, mark needs-author-input and request content/evidence. Validate missing either part uses reduced BLOCK.

Checks has exactly two bullets, Title then Body: `- Part: status — result`, using core values. Findings uses `- Anchor: severity — detail`; anchors are Title, Body, Input, Convention, Structure. Include convention/template evidence or assumptions even in CLEAN. Input is only for excluded source content outside title/body; it causes CONCERNS without a third check or changing passing part statuses. Record all original violations even if corrected. Creation alone uses information.

Needs author input includes all unresolved required facts or one `- None`; optional unknown metadata is omitted. Empty Findings uses `- None`. Replace all placeholders in this complete template:

````markdown
## PR Description Quality Report
Verdict: CONCERNS
Structure: default
### Title
```text
TITLE
```
### Body
```markdown
BODY
```
### Checks
- Title: rewritten — pass
- Body: rewritten — pass
### Findings
- Title: information — Created a title from supplied change evidence.
- Body: information — Created a body from supplied behavior and validation evidence.
- Convention: information — Plain imperative default; repository title rules were not supplied.
- Structure: information — Default structure; repository templates were not supplied.
### Needs author input
- None
````

## Reduced BLOCK

Use only this form for core Error handling; omit Structure, Title, Body, Checks and author-input sections. Request the smallest required input/selection, without inventing candidates:

```markdown
## PR Description Quality Report
Verdict: BLOCK
- Missing input: Concrete unavailable input or unresolved selection.
- Smallest addition to proceed: Exact input needed for the selected operation.
```

## Decision examples

Examples illustrate existing rules:

- Validate with only commits: BLOCK for title/body; do not silently draft.
- Repair a vague draft with supported behavior/validation evidence: changed parts are rewritten/pass; record corrected violations as errors; CONCERNS even when emitted text is ready.
- Unchanged safe passing title/body: compliant/pass, convention/template information only, no author input, CLEAN.
- Validate a credential in Body: redact it, noncompliant/fail for the original disclosure, error finding without reproducing it, CONCERNS. Missing required facts take status precedence but retain that disclosure finding.
- A diff contains excluded content but safe title/body pass: compliant parts, Input/error finding, CONCERNS; no extra check.
- Unsupported passing-test claim: validate marks Body needs-author-input; rewrite omits the claim and states the evidence limitation with the same status until facts arrive. Missing evidence never proves no checks ran.
- Confirmed no checks: honest limitation passes description quality; drafting still yields rewritten and CONCERNS.
- Multiple unresolved templates or unreadable required template: BLOCK; no default compliance claim.
- Reverted breaking API change: omit canceled claim; unresolved final-evidence conflict needs author input.
- Optional missing issue: omit default Linked issues or leave its template section empty; do not block/invent a closure reference.

Mixed-type selection and caller-supplied structure follow the core and evidence reference: an equally primary feature/fix pair selects feat under the default tie order; a custom caller heading set uses Structure: template. Both passing unchanged parts still yield CONCERNS if excluded source content was found.
