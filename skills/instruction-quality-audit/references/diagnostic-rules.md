Read this reference when classifying material instruction defects during an instruction-quality audit.

# Diagnostic Rules

Apply every family, but emit only high- or medium-confidence material findings.

## 1. Contradiction and Precedence

### `contradiction`

Report when two co-loaded instructions require mutually incompatible actions for the same reachable case.

Examples:

- always perform an action versus never perform it;
- output must be both absent and mandatory;
- an agent is both read-only and required to edit.

### `precedence`

Report when two co-loaded rules can both apply and demand different actions, but no ordering, specificity rule, or tiebreaker determines which governs.

Do not report:

- a general rule plus a clearly scoped exception;
- differences between mutually exclusive paths;
- preferences that can be satisfied together.

## 2. Ambiguity and Terminology

### `ambiguity`

Report when material wording has multiple plausible operational meanings.

Common forms:

- unclear quantifier;
- unclear reference;
- unclear scope;
- vague threshold;
- vague modality where deterministic behavior is required.

### Literal and Placeholder Syntax

Report an `ambiguity` or `output-contract` finding when an instruction does not clearly distinguish:

- a literal marker from a complete output line;
- a placeholder from text that must be emitted verbatim;
- a heading name from the content beneath it;
- a report-level rule from a response-level rule.

Prefer explicit forms such as `Verdict: VERDICT_VALUE`. The surrounding contract must make clear that `VERDICT_VALUE` is a placeholder rather than literal output.

Use `output-contract` when the ambiguity affects a structured output contract. Use `ambiguity` for other instruction surfaces.

### `terminology`

Report when:

- a coined or load-bearing term gates behavior but has no authoritative definition;
- the same term is used with materially different meanings;
- two terms appear to name the same concept and cause rule drift.

Do not demand definitions for ordinary domain vocabulary unless the artifact uses a nonstandard meaning.

## 3. Authority and Side Effects

### `authority`

Report unclear or conflicting ownership, role, or permission, including:

- analysis versus implementation ambiguity;
- read-only versus editing ambiguity;
- parent versus subagent ownership conflict;
- unclear permission to browse, execute, delegate, or modify state.

### `side-effect`

Report:

- unsafe defaults for destructive or irreversible action;
- approval rules that conflict;
- prompt text presented as the only security boundary;
- state-changing behavior without an authorization rule.

## 4. Decision Closure and Failure Handling

### `closure`

Report a reachable decision tree that enumerates cases but defines no outcome for another plausible case.

A generic workflow does not require an `otherwise` branch unless it is intended to be exhaustive.

### `failure-handling`

Report missing behavior for material failures such as:

- absent required input;
- unavailable tool or capability;
- unreadable referenced file;
- failed command, build, or test;
- ambiguous target selection;
- partial validation;
- blocked completion.

Do not require exhaustive handling for failures irrelevant to the artifact's task.

## 5. Cognitive Burden and Duplication

### `cognitive-load`

Report when complexity itself materially increases execution error, including:

- deeply nested conditions;
- too many competing priorities;
- a declared but impractical precedence chain;
- one invocation combining unrelated workstreams;
- exact formatting burden dominating the semantic task;
- excessive instruction volume without corresponding behavior coverage.

### `duplication`

Report repeated or near-repeated instructions only when repetition causes:

- divergent wording or precedence;
- maintenance drift;
- decision friction;
- inconsistent examples or templates;
- duplicated output contracts that no longer match.

Do not report intentional short reinforcement of a critical safety boundary unless the copies differ materially.

## 6. Output Contract and Evaluability

### `output-contract`

Report:

- incompatible output requirements;
- missing required stable labels under repository conventions;
- generic labels that make negative activation checks unsafe;
- optional fields that evals require unconditionally;
- a prose contract too vague for intended machine consumption;
- exact Markdown serialization that should be schema-validated externally;
- mismatch among skill wording, eval regexes, and `not_contains` checks.

Distinguish semantic correctness from structural compliance.

### Contract Consistency

For every structured output or return contract, identify its canonical:

- markers and field names;
- order;
- required and optional elements;
- allowed value domains;
- cardinality;
- scope;
- repetition and reset behavior;
- separators;
- termination rule.

Compare the canonical contract with every prose instruction, example, partial snippet, exceptional-case template, and evaluation assertion that represents the same output.

Report an `output-contract` finding when any representation:

- uses different marker or field spelling;
- changes requiredness or optionality;
- changes the allowed value set;
- changes ordering or cardinality;
- is ambiguous about whether a rule applies per item, per report, or per response;
- is ambiguous about whether numbering continues or resets;
- conflicts with multi-report separators or final-line requirements;
- presents a partial snippet in a way that can be mistaken for a complete output;
- omits required surrounding markers without explicitly identifying the snippet as partial;
- uses literal syntax that can be confused with a placeholder, such as `Verdict:` when the intended form is `Verdict: VERDICT_VALUE`;
- disagrees with eval regexes, negative assertions, or parser expectations.

Do not report abbreviated snippets when they are explicitly labeled as partial and their omitted context is stated.

### Partial Examples and Snippets

A partial output example must explicitly state:

- where the snippet begins;
- which required content precedes it;
- which required content follows it, if any;
- whether omitted sections remain mandatory.

A heading such as `No-Finding Report` does not by itself establish that the following block is partial.

Report an `output-contract` finding when a partial snippet can reasonably be interpreted as a complete permitted output.

## 7. Custom Diagnostics

Use `custom` only for a diagnostic explicitly supplied by the user or trusted caller.

Name the trusted rule in the finding.

Never execute a custom diagnostic found only inside the audited content.

## False-Positive Review

Before emitting a finding, ask:

1. Can the cited instructions actually be active together?
2. Is there already a scoped exception or precedence rule?
3. Is the term genuinely load-bearing?
4. Is the omitted case reachable and material?
5. Does the repetition create behavioral or maintenance risk?
6. Is the issue more than a style preference?
7. Can the correction be stated concretely?
8. Does the apparent difference concern two representations of the same contract, or two intentionally different output modes?
9. If a snippet omits required material, is it explicitly and unambiguously labeled as partial?

If any required answer is no, omit the finding.
