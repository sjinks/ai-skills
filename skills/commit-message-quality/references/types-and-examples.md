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

Input subject: `fixed login bug`, no body, change refreshes expired sessions before retry.

Input diagnosis: `fixed` is past tense and there is no type. The corrected output below uses `Subject: pass — rewritten`; its newly written body also uses `Body: pass — rewritten`, and omitted optional footers use `Footers: none — compliant`.
- Rewrite:

```text
fix(auth): refresh expired sessions before retry

Expired sessions failed before the refresh path could renew the token,
forcing users back through login. Refresh on the retry path instead.
```

Mixed change, split recommended:

A diff renames a config key (breaking) and also reformats an unrelated file. Recommend two commits: `feat(config)!: rename timeout to timeoutMs` (with `BREAKING CHANGE:` footer) and `style: reformat report builder`, rather than one combined subject.

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
