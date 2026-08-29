---
name: shell-safety
description: "Use when: an exact nontrivial shell or terminal command is being composed, recommended, validated, or considered for execution, or the user explicitly requests command-safety review but has not supplied the command and needs a blocker response. Execution-scoped triggers include git commit/push/reset/rebase/clean/checkout, rm/mv/cp/chmod/chown, kill/pkill/sudo/dd/mkfs, package/container/cloud/IaC/database/SSH/GPG/network/archive/service commands, pipes, redirects, heredocs, substitutions, globs, quoting, variables, paths, and history rewrites. Do not use for portability-only review, generic shell tutoring or syntax explanation, example commands not being considered for execution, non-shell application review, or prose-only commit-message drafting."
argument-hint: "Paste the command to validate, or state that the exact command is unavailable for a blocker response."
user-invocable: true
---

# Shell Safety

## When to Use

Before composing or running any shell command that is not trivially safe. Trivially safe means these exact literal forms after trusted executable resolution: `ls`, `ls -la`, `pwd`, `whoami`, and `which <cmd>`. Git read commands remain in normal classification because configuration, pagers, and fsmonitor integration can execute auxiliary programs. Arbitrary `<program> --version` and `<program> --help` invocations likewise remain in the normal classification path because resolving and executing an untrusted program can have side effects before or instead of flag parsing. File-content reads are not unconditionally trivial because they can disclose secrets.

**UTILITY SKILL.** INVOKES: terminal command composition and execution only after safety classification. FOR SINGLE OPERATIONS: use to classify one proposed command, rewrite a risky command, or decide what checks must pass before execution.

## DO NOT USE FOR:

- Portability-only shell reviews where the question is cross-shell or cross-OS compatibility rather than execution safety.
- Generic shell tutoring, syntax explanation, or command examples that the assistant is not about to run or recommend running.
- Prose-only requests to draft or revise a commit message when no `git commit` shell invocation is being constructed or reviewed.
- Non-shell languages or application-level security review where no shell command is being composed, validated, or executed. A database statement explicitly intended for execution in a terminal database CLI or REPL is a terminal action and remains in scope.

Everything else needs validation. In particular:

- Any `git commit`, `git push`, `git reset`, `git rebase`, `git clean`, `git checkout`, `git branch -D`, `git tag`.
- Any `rm`, `mv`, `cp`, `chmod`, `chown`, `find -delete`, `dd`, `mkfs`, `truncate`.
- Any `sudo`, `kill -9`, `pkill`, `shutdown`, `reboot`, `systemctl stop/disable`.
- Any pipe (`|`), redirect (`>`, `>>`, `2>&1`), heredoc (`<<EOF`), command substitution (`$(...)`, backticks), glob (`*`, `?`), brace expansion (`{a,b}`).
- Any path with spaces, special characters, or that comes from a variable (`$VAR`, `"$VAR"`).
- Any `ssh`, `scp`, `rsync --delete`, `curl ... | sh`, `wget ... | bash`.
- Any cloud CLI mutation (`aws *-delete`, `aws s3 sync --delete`, `gcloud ... delete`, `az ... delete`).
- Any IaC mutation (`terraform destroy`, `terraform apply -auto-approve`, `pulumi destroy --yes`).
- Any container mass-mutation (`docker system prune`, `docker rm $(docker ps -aq)`, `kubectl delete namespace`).
- Any database mutation executed or proposed for execution through a terminal database CLI or REPL (`DROP`, `TRUNCATE`, `DELETE FROM ... ;` without `WHERE`, `FLUSHALL`, `dropDatabase()`). Ask for the terminal execution context when it is absent.
- Any secret variable in echo, env dump, or a command-line flag carrying a secret, including:
	- ``--password=<redacted>``
	- ``--token=<redacted>``

## Procedure

1. **Categorize.** Split the command into segments and map each segment and interaction to every applicable [Category Index](#category-index) row; do not guess pattern IDs before loading their definitions.
2. **Load.** Read every reference selected by the category pass. Linked reference records are the gating source of truth for each pattern ID, risk, per-pattern decision-gate phrase, and replacement/check sequence; the global [Decision Gates](#decision-gates) and [Output](#output) in this file remain authoritative for interpreting gates and emitting results. If a selected reference is unreadable, return `Result: BLOCKED`, `Matched patterns: None`, name the unavailable reference in `Assessment:`, use `Command: Not provided`, and request the reference under `Required checks:`. Never infer `SAFE`, `REWRITE`, or `AUTHORIZED` from the Category Index alone.
3. **Match.** Check every segment and cross-segment interaction against the loaded reference records, identify every applicable pattern ID, and address every actual match. A fully checked command with no applicable pattern may be `SAFE` with `Matched patterns: None`.
	An in-scope command that mutates external resources may not use that fallback. This includes filesystem or repository objects, processes or services, privileges, packages, remote systems, and cloud, infrastructure, or database state. Process-local shell assignments by themselves are not external-resource mutations and may use `SAFE` with `Matched patterns: None` after all values and downstream execution effects are checked. If no loaded record positively classifies an external mutation, return `BLOCKED`, preserve every independently matched record after explicit subsumption and canonical ordering, and use `Matched patterns: None` only when no record matched at all. State the uncovered effect in `Assessment:` and request an applicable rule or narrower proven-safe action under `Required checks:`.
	Subsumption is explicit only. A command-specific record may declare `Subsumes: <IDs>` when it fully incorporates the same hazard, gate, and required checks; apply and report the specific record and omit only those declared generic IDs. Without that declaration, report and resolve every applicable record. Distinct hazards never subsume one another.
4. **Resolve conflicts.** Apply decision gates in this order: prohibited > rewrite-only > confirmable > safe. If two applicable rules cannot be satisfied together, return `BLOCKED`; do not choose one silently.
5. **Rewrite.** Apply the matching reference record and reassess the complete rewritten command, not only the segment that triggered the first match.
6. **Verify and report.** Resolve values, apply the decision gate, and restate the command according to [Verification Before Execution](#verification-before-execution), then emit the [Output](#output) contract.

For deep quoting questions, consult [quoting-rules.md](./references/quoting-rules.md).

## Category Index

| Category | Pattern IDs | Reference |
| --- | --- | --- |
| Command construction | `GC`, `Q`, `CS1-2`, `CS4-7`, `HD`, `OR`, `SM`, `SE`, `EN` | [command-construction.md](./references/command-construction.md) |
| Host/repository | `GD`, `FS`, `PC`, `PE`, `GP`, `SS`, `AR` | [host-and-repository-changes.md](./references/host-and-repository-changes.md) |
| Remote delivery | `CS3`, `NS`, `RX` | [remote-delivery.md](./references/remote-delivery.md) |
| Platform/data | `CL`, `IC`, `OK`, `DB` | [platform-and-data-operations.md](./references/platform-and-data-operations.md) |

Commands matching multiple rows require loading every matching reference and applying every applicable pattern. References are the sole per-pattern definitions; do not duplicate any individual pattern rule in the core.

## Decision Gates

Classify each exact command segment with the narrowest matching rule below. A compound command can match several gates; the most restrictive matching gate wins for the complete command.

Reference phrases select a Decision Gate section; they are not `Result:` values.

| Reference phrase | Interpretation | Allowed `Result:` values |
| --- | --- | --- |
| `Prohibited`, unconditional `Block` | **Prohibited** | `BLOCKED` |
| `Prohibited for <condition>` | Conditional prohibition | `BLOCKED` while the condition holds; otherwise reclassify the complete command |
| `Block <condition>` (for example `until`, `while`, `without`, `absent`, `unresolved`, or a named unsafe form) | Prerequisite failure, not permanent prohibition | `BLOCKED` while the stated condition holds; otherwise reclassify the complete command |
| `Rewrite` | **Rewrite-Only** | `REWRITE` if the replacement is safe; otherwise `BLOCKED`, `NEEDS-CONFIRMATION`, or later `AUTHORIZED` after reclassification |
| `Rewrite when <condition>` | Conditional rewrite | Apply **Rewrite-Only** while the condition holds; otherwise this pattern does not apply and the segment is reclassified without it |
| `Rewrite unless <verified-safe-condition>` | Verified-safe exception or **Rewrite-Only** | `SAFE` when the named condition is verified and the pattern remains matched; otherwise apply **Rewrite-Only** after its prerequisites pass |
| `Confirm`, `Confirmable`, `Refuse without explicit confirmation/need`, `Last-resort confirmation` | **Confirmable Effects** | `BLOCKED` until prerequisites pass, then `NEEDS-CONFIRMATION` or `AUTHORIZED` |
| `Confirm <effect> unless <verified-safe-condition>` | Verified-safe exception or **Confirmable Effects** | `SAFE` when the named safe condition is verified and the pattern remains matched; otherwise `BLOCKED` until prerequisites pass, then `NEEDS-CONFIRMATION` or `AUTHORIZED` |
| `Inspect`, `Verify`, `Require` | Prerequisite, not a gate or result | `BLOCKED` while unresolved; otherwise reclassify the complete command |

For sequential compound phrases such as `Inspect ... then rewrite`, apply every phase in order and keep the most restrictive result. For disjunctive phrases such as `Rewrite or block`, use the block branch only while its stated condition holds; if no condition is stated, treat the record as `Rewrite` and return `BLOCKED` only when no deterministic replacement exists.

### Prohibited

Return `BLOCKED`. Confirmation never authorizes the original command.
Pattern membership and exceptions are defined only by the loaded reference records.

### Rewrite-Only

Confirmation never authorizes the original form. Provide a concrete replacement that removes it, then classify the replacement from the beginning. Return `REWRITE` if the replacement is safe without confirmation, `NEEDS-CONFIRMATION` if the replacement has a confirmable effect, or `BLOCKED` if no deterministic replacement exists.

A replacement that installs or executes fetched code, applies infrastructure, mutates a cluster, or otherwise has a confirmable effect is not a `REWRITE` result merely because its syntax is safer. Verify provenance and target context, then return `NEEDS-CONFIRMATION` for the exact replacement; unresolved provenance or context returns `BLOCKED`.
Pattern membership, mandatory rewrites, and prerequisites are defined only by the loaded reference records.

### Confirmable Effects

Return `NEEDS-CONFIRMATION` only after every required preview, identity, environment, and recovery check has passed. Bind that result to the normalized command, working directory, shell or interpreter, resolved safety-relevant non-secret expansions, authenticated identity and account, repository or platform context, target identifiers, reviewed preview or plan digest, and relevant branch tips or object versions. On a later turn, re-run cheap mutable checks immediately before execution. Return `AUTHORIZED` only when the user confirmed that exact binding and every check still matches; any changed or unverifiable binding invalidates authorization and requires full reclassification. `AUTHORIZED` means approved to execute, not harmless.
Pattern membership and all command-specific prerequisites are defined only by the loaded reference records.

## Output

Whenever you classify a non-trivially-safe command you are about to send, return exactly these five fields in order, with no introductory or trailing content, even when the user did not explicitly request validation. Omit them only for commands that meet the trivially-safe definition in [When to Use](#when-to-use).

- `Result:` one of `SAFE`, `REWRITE`, `NEEDS-CONFIRMATION`, `AUTHORIZED`, or `BLOCKED`.
- `Matched patterns:` every pattern that matched during classification as `ID (category)`, where `category` is exactly one of `Command construction`, `Host/repository`, `Remote delivery`, or `Platform/data`; do not use reference titles. After applying explicit subsumption, order records by Category Index row (`Command construction`, `Host/repository`, `Remote delivery`, `Platform/data`), then by their order in that row's reference file, and separate them with comma-space. Include patterns whose prerequisites were later satisfied, and use `None` only when no pattern matched at all. A reference record headed by two IDs is one pattern and uses `/` with no spaces, for example `CS3/NS1 (Remote delivery)`.
- A conditional record whose condition does not hold does not match for output and is omitted from `Matched patterns:`.
- `Assessment:` the concrete risk and decision on exactly one non-empty physical line.
- `Command:` the exact safe or rewritten command, or `Not provided` when blocked; never include secret values. For one physical line, emit it after `Command:`. For multiple lines, emit `Command: |` and indent every physical command line, including heredoc bodies and delimiters, by two spaces. That two-space prefix is serialization only and must be removed from every line before execution. Top-level fields are always unindented, so an indented payload line such as `  Required checks:` is command data, not a field.
- `Required checks:` checks that must pass before execution, or `None`. Keep a single check or `None` inline. For multiple lines, emit `Required checks: |` and serialize each check line with the same two-space block indentation used by multiline `Command:`.

If the user asks for command safety but supplies no command, still use the same fields: `Result: BLOCKED`, `Matched patterns: None`, `Assessment:` explaining that no exact command was provided, `Command: Not provided`, and `Required checks:` asking for the exact command plus relevant working directory, shell, target, and whether any variables or secrets are involved.

Use `SAFE` only when the original command can run as restated without confirmation. Use `REWRITE` when the original must not run but a replacement is safe without further confirmation. Use `NEEDS-CONFIRMATION` before approval of an exact confirmable command. Use `AUTHORIZED` only after that exact command was confirmed and all prerequisites still hold. Use `BLOCKED` when no deterministic safe rewrite exists, material values remain unresolved, applicable rules conflict, or the exact action is prohibited.

## Provenance

See [source-map.md](./references/source-map.md) for provenance, source-confidence notes, and the boundary between shell semantics and conservative assistant-side policy.

## Verification Before Execution

Before sending the command:

1. Restate the command with safety-relevant non-secret `$VAR` and `$(cmd)` expansions resolved and quoting visible. Preserve non-material source expressions; keep secret values represented by the variable name or `<redacted>`.
2. If a material non-secret value is unknown, do not run; ask or inspect first. For secret variables, verify the source and presence without reading or echoing the value.
3. Apply the most restrictive matching Decision Gate. Do not treat confirmation as authorization for a prohibited or rewrite-only original form, and reclassify every replacement from the beginning.
4. For destructive operations, name the exact target (path, branch, instance, table, namespace) in your restatement.
5. Re-run classification over the complete restated command and confirm that every matched pattern is addressed. Immediately before an authorized command, refresh mutable identity, context, target, preview, digest, and branch-tip evidence; any mismatch invalidates authorization.

## References

- [Command construction](./references/command-construction.md) — commit messages, quoting, shell composition, secrets, and encoding.
- [Host and repository changes](./references/host-and-repository-changes.md) — Git, filesystem, processes, privilege, signing, services, and archives.
- [Remote delivery](./references/remote-delivery.md) — network-to-shell and SSH safety.
- [Platform and data operations](./references/platform-and-data-operations.md) — cloud, IaC, containers, and database changes.
- [Quoting rules](./references/quoting-rules.md) — bash/zsh quoting and expansion deep dive.
- [Source map](./references/source-map.md) — provenance and source-confidence notes.
