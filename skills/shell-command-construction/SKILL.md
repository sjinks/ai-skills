---
name: shell-command-construction
description: "Use when: constructing, repairing, or validating concrete shell commands, fragments, heredocs, redirections, or payload transport, including command-preparation subtasks within implementation or maintenance. Covers literal/expansion intent, argv and stream boundaries, and multiline data. Do not use for: generic goals without a concrete target, general grammar/debugging, tutoring, prose-only drafting, non-shell work, portability-only analysis, and GitHub CLI interface semantics."
argument-hint: "Provide the concrete command or fragment, shell/interpreter, and intended literal/expansion, argv, and transport boundaries."
---

# Shell Command Construction

Apply this skill to one concrete construction target, including a command being prepared within a larger task. The caller may supply the target or prepare it from established task facts. A generic goal alone does not activate this skill; first establish a concrete command, fragment, heredoc, redirection, or payload interface. A concrete but incomplete construction target activates and may be `BLOCKED`. A command mention without construction work does not activate.

**UTILITY SKILL.** INVOKES: concrete command text and established construction facts only. The caller owns gathering facts, invoking tools, and any separately authorized execution. This skill returns a construction report and does not execute commands.

## Scope and exclusions

This skill assesses construction only: shell parsing, argv boundaries, literal data, and selected input/output transport. Execution safety, authorization, target validity, destructive-effect review, and permission to run are outside scope and not assessed. Do not execute commands or recommend execution.

Do not activate for generic shell tutoring, prose-only drafting without a shell invocation, non-shell work, or portability-only analysis; treat portability-only work as outside this skill's scope. For a mixed construction-and-portability request, produce the construction result first and require a separate portability review of the exact candidate as the only next step; make no cross-target compatibility claim. If construction is `BLOCKED`, resolve that first.

Do not activate when correctness depends on GitHub CLI-specific interface semantics such as `gh api` `-f`/`-F`, endpoint selection, stdin field transport, or `--body-file`; the dedicated GitHub CLI workflow owns those requests, including their shell delivery details.

## Error Handling

### Required facts

Before producing a candidate, establish only the facts that change construction:

- interpreter and relevant modes/options when syntax or quoting behavior materially differs;
- literal versus expansion intent;
- one scalar argument versus a structured argument list;
- quote boundaries; downstream-language grammar only when its token boundaries determine shell quoting;
- stdin, file, heredoc, redirection, or argv transport;
- for a byte-exact payload when a heredoc is considered: whether the payload ends with a terminal newline; if the caller fixes the delimiter, whether it occurs alone on any payload line, otherwise whether a collision-free delimiter can be selected; and, when byte-level input indicates NUL may be present, whether the selected transport can preserve it;
- for SSH or another remote command boundary: the remote interpreter/parser and a confirmed boundary-preserving transport/serialization contract;
- for command substitution when exact output bytes matter: whether its documented trailing-newline removal is compatible with the intended argument;
- empty versus unset behavior when material;
- when literal or expanded glob handling is involved: explicit glob scope or an already-bound operand set;
- a supplied non-secret source expression or transport abstraction for sensitive data; and
- when byte-level input indicates NUL may be present: whether an intended scalar or argv entry contains U+0000 NUL.

If a required fact is absent or conflicts, return `BLOCKED`; do not guess. If the canonical catalog is unreadable, return `BLOCKED` and request that catalog; do not invent its rules.

## Workflow

1. Confirm this is an activated concrete construction request.
2. Identify the interpreter and command form when construction differs by shell.
3. Identify literal/expansion, scalar/list, operand, and transport intent.
4. Select all applicable canonical rules in [construction-rules.md](references/construction-rules.md), then compose them by that catalog's precedence; read [quoting-rules.md](references/quoting-rules.md) only for semantic detail.
5. Produce the smallest candidate that preserves the confirmed construction intent, or block on the smallest missing fact.
6. Serialize the exact output contract below. For a mixed request, require a separate portability review of the exact construction candidate as the single next step. If construction is `BLOCKED`, request its smallest missing fact, required catalog, or confirmed alternative instead.

The Required facts list and canonical catalog are the gating source of truth.

## Dispositions

| Result | Use when | Construction candidate rule |
|---|---|---|
| `VALID` | A supplied, already-correct form preserves confirmed construction intent. | Preserve it exactly. |
| `REWRITE` | A minimum boundary-preserving correction to a defective form is deterministic, or a candidate can be constructed from confirmed intent when no candidate was supplied. | Preserve command name, fixed operands, option order, argument positions and count, transport, literal/expansion intent, and explicit glob scope. Preserve the original transport unless an applicable canonical rule approves a caller-supplied alternative because the original cannot preserve required bytes or boundaries, or the caller explicitly requires another supplied transport. |
| `BLOCKED` | A required construction fact is absent or conflicting, the canonical catalog is unreadable, or the requested boundary/data cannot be represented. | Use `Construction candidate: Not provided` and request one smallest missing fact, required catalog, or alternative. |

Do not render a secret. Do not reveal raw, partial, split, escaped, encoded, transformed, or diagnostic copies of a secret. Represent only a user-supplied non-secret source expression or transport abstraction; otherwise use `BLOCKED`.

## Output

For every activated request, output exactly these five top-level fields once, in this order, with no preamble or trailing prose. Zero or one terminal newline after `Construction next step` is allowed.

```text
Construction result: VALID | REWRITE | BLOCKED
Construction assessment: <one line with at least one non-whitespace character, describing parsing, boundary, and selected transport/representation status only>
Construction candidate: <one-line candidate | Not provided | multiline block>
Execution authority: NOT ASSESSED BY THIS SKILL
Construction next step: <one line with at least one non-whitespace character: one construction action, smallest clarification, or portability handoff>
```

- Use the canonical labels by default. Only when the caller requests replacement labels for a direct construction-only response, read [response-examples.md](references/response-examples.md#direct-response-labels) for eligibility and mapping. For mixed requests, retain canonical labels.
- For `BLOCKED`, use `Not provided` as the candidate-field value.
- For `VALID` or `REWRITE`, the inline candidate-field value `Not provided` is reserved and forbidden. If the exact one-line candidate is `Not provided` or that text followed only by spaces or tabs, serialize it with multiline form. This partial snippet begins at the candidate field; the result and assessment fields precede it, and the authority and next-step fields follow it:
  ```text
  Construction candidate: |
    Not provided
  ```
- A one-line `VALID` or `REWRITE` candidate has at least one non-whitespace character. A one-line command fragment may begin with `|` only when non-whitespace fragment text follows it on the same line; bare candidate-field `|` followed by a newline starts the multiline form. For a multiline candidate, add a two-space serialization prefix to every physical payload line (including an empty line), and include at least one payload line with a non-whitespace character after that removable prefix. The newline before the authority field is framing, not payload; encode a terminal candidate newline as a final two-space-only payload line. Remove only that prefix when interpreting the candidate; any spaces after it are literal payload indentation. Treat prefixed field-looking text as payload, not a top-level field.
- For every label set, use exactly one ASCII space after each field colon as framing. If the exact candidate begins with a space or tab, contains LF, or equals bare `|`, use multiline form. Preserve trailing spaces and tabs in candidate data.
- Use LF (U+000A) for report framing and multiline payload-line separation. Other characters, including CR, VT, FF, U+0085, U+2028, and U+2029, remain literal candidate data; do not normalize them or treat them as report separators. If an interface cannot preserve required candidate data, return `BLOCKED` rather than a changed candidate.
- For `VALID` or `REWRITE`, the next-step field names an immediate, affirmative construction preservation, review, verification, or rewrite action, without deferral. A status-only value is not an action.
- The assessment field describes parsing, boundaries, and selected transport or representation status only; it does not assess safety, authorization, targets, effects, or permission.
- Every candidate, including an effectful-looking one, uses exactly `NOT ASSESSED BY THIS SKILL` as the authority-field value.
- Do not make safety, authorization, approval, or execution claims in the assessment or next-step field. The candidate field is confirmed literal command data: it may contain words such as `safe`, `approved`, `run this`, `deploy`, `release`, or `ship`; do not alter or block a candidate solely for those words. The authority-field value remains exactly `NOT ASSESSED BY THIS SKILL`.

## Checklist and done

- Apply every relevant catalog rule and its precedence. Required-fact conflicts, unrepresentable data, and unavailable catalog access require `BLOCKED`.
- Preserve confirmed argument boundaries, literal data, command structure, and transport; do not render a secret.
- Use exactly five ordered fields with the selected labels, one disposition, the matching candidate form, and the exact authority literal.
- Make no execution or portability claim. For a mixed request, resolve construction blockers first; otherwise require the portability handoff as the only next step.
- A response is complete only when these checks pass.

## Examples

Read [response-examples.md](references/response-examples.md#construction-examples) for complete reports covering activation, byte preservation, and serialization.

## Provenance

Read [Source Map](references/quoting-rules.md#source-map) when source confidence or scope provenance matters.
