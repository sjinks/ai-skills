Read before serializing a report or checking mode, missing-input, disclosure and verdict examples.

# Report and examples

## Full report

Emit exactly one report with the core's ordered markers, no preamble/trailing prose. Full reports use CLEAN or CONCERNS, never BLOCK. Structure is template for repository-selected or caller-supplied heading/checklist structures, and default only for the unreplaced default body structure.

Fence Title as text and Body as markdown; use backtick fences longer than every backtick run in each payload. Preserve safe validation text, whitespace and literal angle brackets; fences are framing. For rewrite with only one supplied part, draft the other from usable change evidence; otherwise leave its fence empty, mark needs-author-input and request content/evidence. Validate missing either part uses reduced BLOCK.

Checks has exactly two bullets, Title then Body: `- Part: status — result`, using core values. Findings uses `- Anchor: severity — detail`; anchors are Title, Body, Input, Convention, Structure. Include convention/template evidence or assumptions even in CLEAN. In full reports, Input covers excluded source content and source-evidence limitations outside title/body. Excluded content uses error and causes CONCERNS; an evidence limitation uses information unless it identifies an unresolved required fact under the core severity rules. Input findings add no third check or independent part status; required facts still affect the relevant Title/Body status. Information alone does not prevent CLEAN. Full disclosure findings name sanitized occurrence locations; reduced BLOCK omits locations and uses only its generic Disclosure signal. Record all original violations even if corrected. Creation alone uses information.

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

Use only this form for core Error handling; omit Structure, Title, Body, Checks and author-input sections. Request the smallest required input/selection, without inventing candidates. Always emit five lines. Inspect all readable input for forbidden content before returning this form. Use `- Disclosure: none` only when none was found; otherwise use exactly `- Disclosure: error — Forbidden content found in supplied input; excluded from output.`. This reduced field covers disclosure in any supplied input, including title/body, and does not change BLOCK. Do not include occurrence locations, extra findings, or full-only sections in reduced BLOCK. All fields remain sanitized:

```markdown
## PR Description Quality Report
Verdict: BLOCK
- Missing input: Concrete unavailable input or unresolved selection.
- Smallest addition to proceed: Exact input needed for the selected operation.
- Disclosure: none
```

When forbidden content accompanies a missing required template, the complete reduced report is:

```markdown
## PR Description Quality Report
Verdict: BLOCK
- Missing input: Required template text is unavailable.
- Smallest addition to proceed: Supply the required template text.
- Disclosure: error — Forbidden content found in supplied input; excluded from output.
```

## Decision examples

Examples illustrate existing rules:

- Validate with only commits: BLOCK for title/body; do not silently draft.
- Missing body or unavailable required template plus excluded content: five-line BLOCK with Disclosure: error and the fixed sanitized sentence; never reproduce the content. Without excluded content, the fifth line is Disclosure: none.
- Repository template discovery is unavailable, but three of five supplied historical PR titles are conventional: use default body structure with the discovery limitation and conventional title mode; missing repository files do not override supplied history.
- With no higher-precedence convention rule: three conventional titles among five supplied historical PR titles select conventional mode; two among four, one among three, or no usable history select plain.
- Repair a vague draft with supported behavior/validation evidence: changed parts are rewritten/pass; record corrected violations as errors; CONCERNS even when emitted text is ready.
- Unchanged safe passing title/body: compliant/pass, convention/template information only, no author input, CLEAN.
- Validate a credential in Body: redact it, noncompliant/fail for the original disclosure, error finding without reproducing it, CONCERNS. Missing required facts take status precedence but retain that disclosure finding.
- A usable change description supplies behavior and validation but no diff: report Input/information that no diff was available; unchanged compliant title/body can remain CLEAN.
- A diff contains excluded content but safe title/body pass: compliant parts, Input/error finding, CONCERNS; no extra check.
- Unsupported passing-test claim: validate marks Body needs-author-input; rewrite omits the claim and states the evidence limitation with the same status until facts arrive. Missing evidence never proves no checks ran.
- Confirmed no checks: honest limitation passes description quality; drafting still yields rewritten and CONCERNS.
- Supplied routine passing checks, with no meaningful regression scenario supplied: omit the routine success inventory from a drafted body unless a core exception applies. Do not invent coverage, say validation evidence was absent, or request more checks merely to fill Testing. Leave the default Testing section empty when no body-worthy verification content remains; preserve any selected template's checklist rules.
- A draft includes a supported but unnecessary unit-suite count, version matrix, full head hash and agent review verdict: rewrite removes these body details under the default omissions; validate preserves safe text and reports the unnecessary details as Body/error, noncompliant/fail. An explicit caller/template requirement permits supported details; it does not permit unsupported success or attribution.
- A supplied failing compatibility check affects the changed behavior: retain the failure and relevant environment limitation, even though routine successful checks are omitted. Proposed reproduction steps remain unrun; coverage alone is not a passing-test claim.
- A body says "fails closed" but the supplied evidence does not establish whether the finding remains or approval is withheld: request the missing behavior fact. Do not invent an outcome to make the prose concrete.
- With no explicit caller/template requirement, supplied evidence includes routine checks and local reviews, with no claim requiring evaluation: draft/rewrite omits the process summary and generic missing-review/evaluation disclaimer. The absence of independent review alone does not require author input. Validate preserves safe supplied text and reports unnecessary process details under the core's omission rule. If the caller/template explicitly requires a review/evaluation status, retain the supported status without presenting it as proof of correctness.
- A supplied limitation says the changed OAuth callback has not been exercised in a browser and still requires that verification before release: retain the specific behavior and release consequence. Do not replace it with "integration testing was not performed" or remove it with routine status details.
- Supplied examples establish that routine-only evidence requires no additional checks and an explicit template requires preserving status fields: describe those expected decisions in Testing. Do not substitute a list of example topics or retell an embedded example's application-domain bug. Do not claim the examples were executed.
- A change makes drafting remove unnecessary details while validation preserves them and reports noncompliant/fail: describe both outcomes in Changes. Do not imply all modes silently remove text. This concerns the described artifact's modes; the current operation still follows the core's draft/rewrite/validate rules.
- A draft lists changed files and passed checks but leaves the impact unclear: draft/rewrite explains the evidenced issue, why it matters and how the solution addresses it. If required impact or rationale cannot be established, request the missing fact rather than inventing harm; validate preserves safe text and reports the omission under the core's status rules.
- A supplied comparison establishes that a strict validator rejects older clients while an adapter preserves compatibility at an operational cost: include the chosen option, that tradeoff and the supplied reason for rejecting the other option. Missing required comparison facts use Body needs-author-input. A straightforward fix without a caller/template requirement needs no invented alternatives section.
- A selected repository template uses its own headings: answer the reviewer questions within that structure. Preserve the template's headings/checklists; do not replace them with four mandatory question headings.
- Multiple unresolved templates or unreadable required template: BLOCK; no default compliance claim.
- Reverted breaking API change: omit canceled claim; unresolved final-evidence conflict needs author input.
- Optional missing issue: omit default Linked issues or leave its template section empty; do not block/invent a closure reference.

Mixed-type selection and caller-supplied structure follow the core and evidence reference: an equally primary feature/fix pair selects feat under the default tie order; a custom caller heading set uses Structure: template. Both passing unchanged parts still yield CONCERNS if excluded source content was found.

## Reviewer-focused body example

This illustrative body assumes evidence establishes every stated behavior and coverage case. It uses the default headings; a selected template replaces that structure. It does not claim that the tests ran or passed. This is only the Body payload: the full report still requires its opening markers and Title before it, and Checks, Findings and Needs author input after it.

```markdown
## Summary

Two PRs can share a head commit while using different bases. A file can therefore contain a nonfunctional change in one PR and a functional change in the other. Previously, approval for that filename in one PR could suppress the other PR's finding. The second PR could lose an actionable finding even though its own diff did not qualify for approval.

## Changes

Approval reasons are now scoped to each PR and filename, so one PR's eligibility cannot determine the other's approval. When approval state is missing, the finding and error count remain and automatic approval is withheld.

## Testing

Regression tests cover the shared-head, different-base scenario in both processing orders. They verify that only the eligible PR receives approval and the other retains its finding and error count.
```

If evidence establishes a compatibility effect from changing the approval-state format, describe that effect as well. If the required persistence or migration facts are unknown, request them rather than copying an unsupported compatibility claim into this example.
