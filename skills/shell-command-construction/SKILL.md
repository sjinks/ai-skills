---
name: shell-command-construction
description: "Use when constructing, repairing, or validating a concrete supplied shell command, fragment, heredoc, redirection, or payload interface where literal text, argv boundaries, shell parsing, multiline data, or transport is primary. Do not use for generic goals without a supplied shell target, generic shell tutoring, prose-only drafting, non-shell work, or portability-only analysis."
argument-hint: "Provide the concrete command or fragment, shell/interpreter, and intended literal/expansion, argv, and transport boundaries."
user-invocable: true
---

# Shell Command Construction

Use this skill only when the request supplies a concrete shell construction target whose correct parsing or data delivery matters: a named executable, exact command fragment, heredoc/redirection, or payload interface/data. A generic goal such as “remove old files” with no command, executable, path, shell syntax, or supplied payload interface/data does not activate this skill. A concrete but incomplete construction request does activate and may be `BLOCKED`.

**UTILITY SKILL.** INVOKES: supplied command text and declared construction facts only. FOR SINGLE OPERATIONS: use to repair or validate one concrete command, fragment, heredoc, redirection, or payload transport.

## Scope and exclusions

This skill assesses construction only: shell parsing, argv boundaries, literal data, and selected input/output transport. Execution safety, authorization, target validity, destructive-effect review, and permission to run are outside scope and not assessed. Never execute a command or recommend execution.

Do not activate for generic shell tutoring, prose-only drafting without a shell invocation, non-shell work, or portability-only analysis; treat portability-only work as outside this skill's scope. For a mixed construction-and-portability request, produce the construction result first and require a separate portability review of the exact candidate as the only next step; make no cross-target compatibility claim. If construction is `BLOCKED`, resolve that first.

## DO NOT USE FOR:

- Generic shell education with no concrete command, fragment, or payload transport.
- Drafting prose without a shell invocation, non-shell work, or portability-only analysis.
- Execution safety, authorization, target validity, destructive-effect review, or permission to run.

## Required facts

Before producing a candidate, establish only the facts that change construction:

- interpreter when syntax materially differs;
- literal versus expansion intent;
- one scalar argument versus a structured argument list;
- quote boundaries; downstream-language grammar only when its token boundaries determine shell quoting;
- stdin, file, heredoc, redirection, or argv transport;
- for a byte-exact payload when a heredoc is considered: whether the payload ends with a terminal newline; if the caller fixes the delimiter, whether it occurs alone on any payload line, otherwise whether a collision-free delimiter can be selected; and, when byte-level input indicates NUL may be present, whether the selected transport can preserve it;
- for SSH or another remote command boundary: the remote interpreter/parser and a confirmed boundary-preserving transport/serialization contract;
- empty versus unset behavior when material;
- when literal or expanded glob handling is involved: explicit glob scope or an already-bound operand set;
- a supplied non-secret source expression or transport abstraction for sensitive data; and
- when byte-level input indicates NUL may be present: whether an intended scalar or argv entry contains U+0000 NUL.

If a required fact is absent or conflicts, return `BLOCKED`; do not guess.

## Workflow

1. Confirm this is an activated concrete construction request.
2. Identify the interpreter and command form when construction differs by shell.
3. Identify literal/expansion, scalar/list, operand, and transport intent.
4. Select all applicable canonical rules in [construction-rules.md](references/construction-rules.md), then compose them by that catalog's precedence; read [quoting-rules.md](references/quoting-rules.md) only for semantic detail.
5. Produce the smallest candidate that preserves the confirmed construction intent, or block on the smallest missing fact.
6. Serialize the exact output contract below. For a mixed request, require a separate portability review of the exact construction candidate as the single next step. If construction is `BLOCKED`, request its smallest missing fact instead.

The Required facts list and canonical catalog are the gating source of truth.

## Dispositions

| Result | Use when | Candidate rule |
|---|---|---|
| `VALID` | A supplied, already-correct form preserves confirmed construction intent. | Preserve it exactly. |
| `REWRITE` | A minimum boundary-preserving correction to a supplied defective form is deterministic, or a candidate can be constructed from confirmed intent when no candidate was supplied. | Preserve command name, fixed operands, option order, argument positions and count, transport, literal/expansion intent, and explicit glob scope. Preserve the original transport unless an applicable canonical rule approves a caller-supplied alternative because the original cannot preserve required bytes or boundaries. |
| `BLOCKED` | A required construction fact is absent or conflicting, or the requested boundary/data cannot be represented. | Use `Candidate: Not provided` and request one smallest missing fact or alternative. |

Never render a secret. Do not reveal raw, partial, split, escaped, encoded, transformed, or diagnostic copies of a secret. Represent only a user-supplied non-secret source expression or transport abstraction; otherwise use `BLOCKED`.

## Output

For every activated request, output exactly these five top-level fields once, in this order, with no preamble or trailing prose. Zero or one terminal newline after `Next step` is allowed.

```text
Construction result: VALID | REWRITE | BLOCKED
Construction assessment: <one line with at least one non-whitespace character, describing parsing/boundary status only>
Candidate: <one-line candidate | Not provided | multiline block>
Execution authority: NOT ASSESSED BY THIS SKILL
Next step: <one line with at least one non-whitespace character: one construction action, smallest clarification, or portability handoff>
```

- `BLOCKED` always uses `Candidate: Not provided`.
- A one-line `VALID` or `REWRITE` candidate has at least one non-whitespace character. A one-line command fragment may begin with `|` only when non-whitespace fragment text follows it on the same line; bare `Candidate: |` followed by a newline starts the multiline form. For a multiline candidate, add a two-space serialization prefix to every physical payload line (including an empty line), and include at least one payload line with a non-whitespace character after that removable prefix. Remove only that prefix when interpreting the candidate; any spaces after it are literal payload indentation. Treat prefixed field-looking text as payload, not a top-level field.
- For `VALID` or `REWRITE`, `Next step` names an affirmative construction preservation, review, or verification action. A status-only value such as `No further construction action is required` is not an action.
- `Construction assessment` describes parsing and boundaries only; it does not assess safety, authorization, targets, effects, or permission.
- Every candidate, including an effectful-looking one, uses exactly `Execution authority: NOT ASSESSED BY THIS SKILL`.
- Do not make safety, authorization, approval, or execution claims in `Construction assessment` or `Next step`. `Candidate` is confirmed literal command data: it may contain words such as `safe`, `approved`, `run this`, `deploy`, `release`, or `ship`; never alter or block a candidate solely for those words. Execution authority remains exactly `NOT ASSESSED BY THIS SKILL`.

## Definition of done

A response is complete only when it has preserved every confirmed boundary or returned `BLOCKED`, has not rendered a secret, has made no execution or portability claim, and matches the five-field output contract exactly.

## Provenance

Read [source-map.md](references/source-map.md) when source confidence or scope provenance matters.
