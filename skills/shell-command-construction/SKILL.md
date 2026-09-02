---
name: shell-command-construction
description: "Use when constructing, repairing, or validating a concrete shell command, fragment, heredoc, redirection, or command-producing request where literal text, argv boundaries, shell parsing, multiline data, or transport is primary. Do not use for generic shell tutoring, prose-only drafting, non-shell work, or portability-only analysis."
argument-hint: "Provide the concrete command or fragment, shell/interpreter, and intended literal/expansion, argv, and transport boundaries."
user-invocable: true
---

# Shell Command Construction

Use this skill only for a concrete shell construction target whose correct parsing or data delivery matters.

**UTILITY SKILL.** INVOKES: supplied command text and declared construction facts only. FOR SINGLE OPERATIONS: use to repair or validate one concrete command, fragment, heredoc, redirection, or payload transport.

## Scope and exclusions

This skill assesses construction only: shell parsing, argv boundaries, literal data, and selected input/output transport. Execution safety, authorization, target validity, destructive-effect review, and permission to run are outside scope and not assessed. Never execute a command or recommend execution.

Do not activate for generic shell tutoring, prose-only drafting without a shell invocation, non-shell work, or portability-only analysis; route portability-only work to `shell-portability`. For a mixed construction-and-portability request, produce the construction result first and make `shell-portability` review of the exact candidate the only next step; make no cross-target compatibility claim. If construction is `BLOCKED`, resolve that first.

## DO NOT USE FOR:

- Generic shell education with no concrete command, fragment, or payload transport.
- Drafting prose without a shell invocation, non-shell work, or portability-only analysis.
- Execution safety, authorization, target validity, destructive-effect review, or permission to run.

## Required facts

Before producing a candidate, establish only the facts that change construction:

- interpreter when syntax materially differs;
- literal versus expansion intent;
- one scalar argument versus a structured argument list;
- quote boundaries and downstream-language grammar;
- stdin, file, heredoc, redirection, or argv transport;
- for SSH or another remote command boundary: the remote interpreter/parser and a confirmed boundary-preserving transport/serialization contract;
- empty versus unset behavior when material;
- when literal or expanded glob handling is involved: explicit glob scope or an already-bound operand set; and
- a supplied non-secret source expression or transport abstraction for sensitive data.

If a required fact is absent or conflicts, return `BLOCKED`; do not guess.

## Workflow

1. Confirm this is an activated concrete construction request.
2. Identify the interpreter and command form when construction differs by shell.
3. Identify literal/expansion, scalar/list, operand, and transport intent.
4. Select the applicable canonical rule in [construction-rules.md](references/construction-rules.md); read [quoting-rules.md](references/quoting-rules.md) only for semantic detail.
5. Produce the smallest candidate that preserves the confirmed construction intent, or block on the smallest missing fact.
6. Serialize the exact output contract below. For a mixed request, make `shell-portability` review of the exact SCC candidate the single next step. If construction is `BLOCKED`, request its smallest missing fact instead.

The Required facts list and canonical catalog are the gating source of truth.

## Dispositions

| Result | Use when | Candidate rule |
|---|---|---|
| `VALID` | The supplied form preserves confirmed construction intent. | Preserve it exactly. |
| `REWRITE` | A minimum boundary-preserving correction is deterministic. | Preserve command name, fixed operands, option order, argument positions and count, transport, literal/expansion intent, and explicit glob scope. |
| `BLOCKED` | A candidate would require invented intent or secret representation. | Use `Candidate: Not provided` and request one smallest missing construction fact. |

Never render a secret. Do not reveal raw, partial, split, escaped, encoded, transformed, or diagnostic copies of a secret. Represent only a user-supplied non-secret source expression or transport abstraction; otherwise use `BLOCKED`.

## Output

For every activated request, output exactly these five top-level fields once, in this order, with no preamble or trailing prose:

```text
Construction result: VALID | REWRITE | BLOCKED
Construction assessment: <one non-empty line describing parsing/boundary status only>
Candidate: <one-line candidate | Not provided | multiline block>
Execution authority: NOT ASSESSED BY THIS SKILL
Next step: <one construction action, smallest clarification, or shell-portability handoff>
```

- `BLOCKED` always uses `Candidate: Not provided`.
- For a multiline candidate, write `Candidate: |` and add a two-space serialization prefix to every physical payload line, including an empty line. Remove only that prefix when interpreting the candidate; any spaces after it are literal payload indentation. Treat prefixed field-looking text as payload, not a top-level field.
- `Construction assessment` describes parsing and boundaries only; it does not assess safety, authorization, targets, effects, or permission.
- Every candidate, including an effectful-looking one, uses exactly `Execution authority: NOT ASSESSED BY THIS SKILL`.
- Do not output safety, authorization, approval, or execution claims. In particular, do not use `SAFE`, `AUTHORIZED`, `NEEDS-CONFIRMATION`, `safe`, `authorized`, `approved`, `executable`, `safe to run`, or `run this`.

## Definition of done

A response is complete only when it has preserved every confirmed boundary or returned `BLOCKED`, has not rendered a secret, has made no execution or portability claim, and matches the five-field output contract exactly.

## Provenance

Read [source-map.md](references/source-map.md) when source confidence or scope provenance matters.
