Read the Report format section before emitting a report. Read the remaining sections when selecting a conventional type, classifying a removal, or illustrating a message rewrite or split.

# Types and Examples

The core defines rule precedence and decisions; the Report format section below defines report serialization. The type descriptions and removal choices below are fallback message defaults; apply caller and readable repository rules first under the core precedence. Examples are non-normative and use hypothetical supplied issue/change context.

## Report format

Use these exact markers in order; do not substitute labels. Replace every report-template placeholder with concrete content, including both BLOCK fields. Preserve literal angle-bracket text in supplied messages.

- `## Commit Message Quality Report`
- `Verdict:` — `CLEAN`, `CONCERNS`, or `BLOCK`.
- `Mode:` — `conventional` or `plain`.
- `### Commit message` — full message in a `text` fence; use a fence longer than any backtick run in the message.
- `### Checks` — exactly three bullets, each `<part>: <result> — <status>`; failure reasons name violated contract items or required missing facts or message rules:
  - `Subject:` result is `pass`, `pass (length: <N> chars, over 50)`, or `fail (reason)`. Replace `<N>` with the measured whole-subject character count as a decimal integer.
  - `Body:` result is `pass`, `fail (reason)`, or `n/a (not needed)`.
  - `Footers:` result is `pass`, `fail (reason)`, or `none`.
- `### Findings` — bullets `<anchor>: <severity> — <detail>`, with anchor `Subject`, `Body`, `Footers`, `Input`, or `Convention`. For `error`, detail names the violation and correction. For `warning`, detail names the unresolved fact or message rule and required input. Use `Input` only for excluded source content outside the message parts, with severity `error`. For required non-violating cleanup advice, use `Body: information — <cleanup preservation status and advice>`; say `unverified` when effective cleanup is unknown. Include `Convention: information — <evidence or assumption>`; `Convention` uses only `information`.
- `### Split recommendation` — proposed commits or `- None`.
- `### Needs author input` — exact missing facts or required message rules or `- None`.

Use bullets outside the message fence. For an empty Findings, Split recommendation or Needs author input list, use `- None`. A full report always has convention information, so its Findings list is not empty.

For unusable input, the core's reduced BLOCK template replaces the full form, including Mode and all section headings. Do not emit an incomplete full report.

The core's verdict policy deliberately returns `CONCERNS` for newly drafted or corrected text, including passing text. Do not copy another report's verdict semantics or treat a passing draft as `CLEAN`.

The complete validation example below is illustrative, not a second source of decision rules.

## Subject grammar

In conventional mode use a lowercase type from `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`; optional scope is enclosed in parentheses and consists of comma-separated `[a-z0-9][a-z0-9-]*` tokens without spaces; optional `!`; then exactly `: ` and an imperative description. Plain mode omits the prefix. In both modes, the description starts lowercase unless a proper noun/acronym. The core owns punctuation, whole-subject length and selected-rule precedence.

## Conventional type selection

| Type | Use for |
| --- | --- |
| `feat` | New user-visible capability. |
| `fix` | Bug fix or corrected behavior. |
| `docs` | Documentation only. |
| `style` | Formatting/whitespace, no behavior change. |
| `refactor` | Code change with no behavior change. |
| `perf` | Performance improvement. |
| `test` | Adding or fixing tests. |
| `build` | Build system, packaging, dependencies. |
| `ci` | CI/automation config. |
| `chore` | Maintenance with no source/test behavior change. |
| `revert` | Reverting a previous commit. |

Removal type: deleting dead or unused code is `chore`; removing deprecated internals is `refactor`; removing a supported public capability is `feat` with a `BREAKING CHANGE:` footer; removing tests or CI uses `test` or `ci`.

## Illustrations

Vague draft, Conventional mode:

Supplied input: subject `fixed login bug`, no body. Author-supplied change facts say expired sessions failed before the refresh path could renew the session token, forcing users back through login; the change refreshes expired sessions before retry.

Input diagnosis: `fixed` is past tense and there is no type. The corrected output below uses `Subject: pass — rewritten`; its newly written body also uses `Body: pass — rewritten`, and omitted optional footers use `Footers: none — compliant`.
- Rewrite:

```text
fix(auth): refresh expired sessions before retry

Expired sessions failed before the refresh path could renew the token,
forcing users back through login. Refresh on the retry path instead.
```

Mixed change, split recommended:

A supplied diff renames a config key (breaking) and also reformats an unrelated report builder. Recommend two commits, but the returned message still covers both changes unless the caller explicitly selects a prospective split. A full-scope subject could be `feat(config)!: rename timeout key and format report builder`; its body explains the rename and mentions the unrelated formatting, and its footer discloses the breaking rename.

If the caller identifies only the config-key rename as the prospective commit, return a message for that scope with subject `feat(config)!: rename timeout to timeoutMs` and the breaking-change footer. Under Split recommendation, identify the returned message as prospective for the config rename and recommend a separate formatting commit. This does not assert that either split has occurred.

These are subject/scope illustrations, not complete report templates. The core's required report sections and message body/footer rules still apply.

## Claim-fidelity illustrations

Supplied change facts say the fix refreshes expired sessions on retry and leaves other login failure paths unchanged. A draft claiming `fix all login failures` overstates that scope. Narrow it to `fix(auth): refresh expired sessions before retry` during repair; validation preserves the safe original and reports the contradicted Subject claim as `noncompliant`.

A message says the change eliminates production timeouts, but the only evidence is a diff that changes a timeout setting. Validation requests evidence or corrected author facts and uses `Subject: fail (unverified timeout claim) — needs-author-input` if the claim is in Subject. Draft/repair omits the unsupported runtime-success claim and describes the evidenced setting change. If the required rationale is also unknown, Body still needs author input. Message-only validation does not treat the supplied claim as proof.

## Omission status illustrations

Deleting a supplied, known-invalid optional footer during repair uses `Footers: none — rewritten`, an `error` finding describing the correction, and `CONCERNS`. An already absent permitted footer uses `Footers: none — compliant`.

Deleting a filler body when the subject carries all required context uses `Body: n/a (not needed) — rewritten`. Intentionally omitting an unnecessary body while drafting uses `Body: n/a (not needed) — compliant`. A rule requiring a body or missing required context overrides these passing examples; unresolved required facts use `fail (...) — needs-author-input`.

## Footer and input-finding illustrations

A hypothetical change whose subject carries all required context, with supplied real issue #123, may omit Body while retaining a footer separated from Subject:

```text
docs(cli): correct the spelling of configuration in help

Closes #123
```

For a valid safe message accompanied by a diff with sensitive source content, retain otherwise passing part checks, add `Input: error — excluded sensitive source content; review the source separately` under Findings, and select `CONCERNS`. Do not quote that content or add an Input check. Reduced BLOCK reports instead name the actual missing input and smallest requested addition; report-template placeholders are never copied literally.

## Cleanup-advice illustration

When validating a safe, otherwise compliant message with a comment-like body heading and unknown cleanup mode, preserve the message, retain `Body: pass — compliant`, and include `Body: information — cleanup preservation unverified; use --cleanup=whitespace or --cleanup=verbatim to preserve headings` under Findings. Convention evidence still appears; no author question is required, and cleanup uncertainty alone permits `CLEAN`.

## Complete validation report

Hypothetical input: validate the exact message below. Supplied change facts establish that expired sessions are refreshed before retry, but provide no production evidence for the body claim. There are no readable repository message rules or known history; use the conventional default. The change is nontrivial and no issue or attribution is supplied. The report preserves safe text and requests evidence for the unsupported production guarantee.

````markdown
## Commit Message Quality Report
Verdict: CONCERNS
Mode: conventional

### Commit message
```text
fix(auth): refresh expired sessions before retry

Eliminate production login failures after session expiry.
```

### Checks
- Subject: pass — compliant
- Body: fail (missing evidence for production guarantee) — needs-author-input
- Footers: none — compliant

### Findings
- Body: warning — the supplied change facts do not establish elimination of production login failures; provide supporting production evidence or corrected author facts.
- Convention: information — no readable repository message rules or known history were supplied; conventional mode and default style rules apply.

### Split recommendation
- None

### Needs author input
- Provide evidence supporting the production guarantee or corrected author facts about the intended effect.
````
