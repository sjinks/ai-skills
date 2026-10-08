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
