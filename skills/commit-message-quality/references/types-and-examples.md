When to read: when selecting a conventional type, classifying a removal, or illustrating a message rewrite or split.

# Types and Examples

The core defines rule precedence, decisions and report structure. The type descriptions and removal choices below are fallback message defaults; apply caller and readable repository rules first under the core precedence. Examples are non-normative and use hypothetical supplied issue/change context.

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

Deleting a supplied invalid body from a trivial change uses `Body: n/a (trivial) — rewritten`. If selected repository rules permit no body for a nontrivial change, correction by deletion uses `Body: pass — rewritten`; intentional omission while drafting uses `Body: pass — compliant`. Required unknown facts or rules override these passing examples with `fail (...) — needs-author-input`.

## Footer and input-finding illustrations

A hypothetical trivial change with supplied real issue #123 may omit Body while retaining a footer separated from Subject:

```text
docs: clarify setup instructions

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
