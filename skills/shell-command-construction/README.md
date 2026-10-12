# shell-command-construction

> Use before submitting any in-scope shell command to an execution tool, including routine commands, destructive commands such as `rm`, and command preparation within larger tasks; also use for concrete construction, repair, or validation.

This skill returns a construction result only. Execution safety, authorization, target validity, destructive-effect review, and permission to run are outside its scope and are not assessed.

It activates for a concrete shell target supplied by the caller or prepared from established task facts, including every in-scope shell command prepared for an execution tool. Activation does not depend on suspected quoting errors or a separate user request. Check quoting, expansion intent, argv boundaries and stream delivery before submission; recheck after construction-affecting changes. Generic goals alone and mere command mentions do not activate. An incomplete concrete target blocks rather than guessing. The caller owns evidence gathering and any separately authorized execution; the skill returns one construction report to that workflow. Direct requests end with that report; nested command preparation returns it internally or as a delegated result, ends only the subtask, and lets the enclosing workflow continue under its own response contract. A `BLOCKED` result must be resolved before submission, and `VALID`/`REWRITE` never grant execution authority. Any separately authorized submission uses exactly the decoded `Construction candidate` from the latest `VALID`/`REWRITE` report; an unchecked original or later edit cannot be submitted without a new check.

SCC-S0 checks grammar completeness for every activated target. Unresolved malformed or incomplete grammar blocks for a corrected form. A deterministic quoting/boundary correction prescribed by another canonical rule may still produce `REWRITE` after its candidate passes the grammar check; fragments whose grammar depends on enclosing context block when that context is absent. General grammar repair and parser execution remain outside the skill. Complete supplied forms still use the other construction rules before receiving `VALID` or `REWRITE`.

It preserves confirmed token boundaries, literal-versus-expansion intent, operand order, transport, and payload data. SCC-Q1 keeps a multiline literal scalar in one argv word and explicitly covers `dash` and BusyBox `ash`. Bash history-sensitive quoting requires relevant mode/options when they affect literal preservation. The quoting reference also explains fixed-format `printf` payload delivery for a caller-confirmed transport. SCC-A1 distinguishes one-argument quoting from byte preservation: when exact output bytes matter, command substitution must preserve those bytes or block pending a confirmed alternative. SCC-M1 covers supplied stdin, file, heredoc, and Bash here-string transport, including leading-tab stripping, delimiter collisions, and appended-newline compatibility. Immediately terminated heredocs preserve exact-empty payloads as zero bytes; a blank body line is LF, and nonempty literal bodies require their final LF. The quoting reference distinguishes literal `%s` delivery from intentional `%b` escape interpretation and explains backslash-LF continuation. Downstream semantics are outside scope unless their token boundaries determine shell parsing.

All label sets use one ASCII framing space after each colon. Leading candidate whitespace and LF require multiline serialization; only LF separates report lines. Other control characters and Unicode separators remain literal candidate data. The five canonical fields, disposition values, authority literal, and construction-only boundary are unchanged.

Payload facts are transport-specific: an exact nonempty literal heredoc requires terminal-newline intent, while an exact Bash here-string requires compatibility with its appended LF. Facts about one transport cannot satisfy the other's gate.

A supplied correct, collision-free heredoc delimiter needs no delimiter-change permission. Establish selection/change permission only when constructing or correcting the candidate actually requires it; collision checks and other payload facts still apply.

Portability-only analysis does not activate this skill and belongs to a separate portability review. For mixed requests, SCC produces its five-field construction response first. Its `Construction next step` requires a separate portability review of the exact SCC candidate before any cross-target compatibility conclusion. Resolve a `BLOCKED` construction result before that review. SCC does not construct a portability candidate or make a compatibility claim. The five canonical labels are the default; explicit caller-requested replacement labels apply only to a direct response and are not a later-review handoff.

## Global routing example

This repository's `AGENTS.md` requires the routing below for Codex tasks in this checkout. For other repositories, install this skill and add the following section to applicable agent instructions (for example, global Codex `AGENTS.md`). The routing requires construction checks without granting execution authority; it is an instruction rule, not measured model adherence or runtime enforcement.

```markdown
## Shell Command Preparation

Before submitting shell command text to an execution tool, read and apply `shell-command-construction` to the exact text. This includes routine commands, destructive commands such as `rm`, and commands prepared within larger tasks. Do not wait for suspected quoting errors or a separate user request.

Apply the skill's scope exclusions first. For excluded interface-specific requests, use the owning workflow to check shell delivery before submission. For in-scope commands, use the construction report within the command-preparation subtask; resolve `BLOCKED` before submission. For any authorized in-scope submission, send the execution tool exactly the decoded `Construction candidate` from the latest `VALID` or `REWRITE` report, never an unchecked original. Recheck after any construction-affecting change, including any later edit to that candidate. `VALID` and `REWRITE` establish construction only; execution authorization and effect review remain separate requirements of the calling workflow.

If the skill or a required reference is unavailable, do not submit the affected command; locate or restore the package first. Read-only tool calls needed to locate or load these instructions may proceed without this construction check. This exception does not permit submitting the command under review.
```

## Files

- [`SKILL.md`](SKILL.md) — activation, workflow, output contract, and completion rules.
- [`references/construction-rules.md`](references/construction-rules.md) — canonical construction decisions.
- [`references/quoting-rules.md`](references/quoting-rules.md) — explanatory shell semantics, source map, and scope provenance.
- [`references/response-examples.md`](references/response-examples.md) — optional caller-label eligibility and complete construction reports.
