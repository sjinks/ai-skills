Read this catalog when selecting a construction disposition; it is the sole normative owner of the construction decisions in this package.

## Composition and precedence

Select every applicable canonical rule, not one rule by preference. Representability and fail-closed constraints always apply. Transport- and boundary-specific rules constrain the candidate. SCC-A1 owns scalar/list intent and confirmed parameter-expansion argv boundaries; SCC-Q1 applies only to directly supplied literal scalar data, never an expansion source. Combine nonconflicting no-drift constraints. If applicable actions conflict after this precedence, or a required fact is missing, return `BLOCKED`.

# Construction Rules

All records use this fixed shape. The catalog-only `Safety projection` field is metadata; it never assesses execution concerns and is not part of the user-facing output contract.

### SCC-Q1 — Direct literal scalar text

Trigger: Directly supplied literal scalar data must remain literal through shell parsing; this does not cover a parameter-expansion source.
Construction risk: Spaces, quotes, `$`, backticks, `!`, globs, or backslashes are expanded, split, or reparsed.
Required facts: Interpreter; one scalar intent; literal versus expansion intent; when byte-level input indicates NUL may be present, whether the scalar contains NUL.
Disposition: VALID, REWRITE, or BLOCKED.
Construction-preserving action: POSIX-like shell words and process argv cannot represent U+0000 NUL. If the intended scalar contains NUL, return BLOCKED even when every other fact is complete, with `Candidate: Not provided`; request a confirmed non-argv NUL-capable transport/interface rather than inventing one. Otherwise, first validate and preserve any supplied representation that already keeps the confirmed literal scalar as exactly one shell word. Rewrite a defective or absent representation for declared POSIX-like `sh`, Bash, ksh, or zsh by single-quoting the literal scalar text. Within that representation, replace each embedded apostrophe with the exact close-single-quote, double-quoted-apostrophe, reopen-single-quote sequence `'"'"'`. For example, literal `O'Reilly $HOME *` is `'O'"'"'Reilly $HOME *'`; adjacent quoted segments with no unquoted whitespace form one shell word. A multiline scalar remains one quoted shell word containing its newline; do not change its transport to stdin, a file, or a heredoc. If the shell is undeclared or unsupported and the syntax materially differs, return BLOCKED.
No-drift constraints: Preserve command name, fixed operands, option order, the one-argv-entry boundary, and literal bytes/characters, including embedded newlines.
Effectful marker: none.
Portability handoff: separate portability review required before a cross-target claim.
Provenance: POSIX Shell Command Language; Bash manual; high.
Safety projection: catalog metadata only; execution concerns not assessed by this skill.

### SCC-Q2 — Expansion and quote ambiguity

Trigger: `$`, command substitution syntax, history-sensitive `!`, glob characters, backslashes, or quote boundaries have unspecified shell intent; or downstream token boundaries materially determine shell parsing and are unknown.
Construction risk: A plausible quote choice changes data into expansion or expansion into literal data.
Required facts: Interpreter; literal/expansion intent; intended quote boundary; downstream-language grammar only when its token boundaries materially determine shell parsing.
Disposition: BLOCKED.
Construction-preserving action: Request the one missing literal/expansion, quote-boundary, or parsing-relevant downstream-token-boundary fact. Exact supplied literal argument text with confirmed shell boundaries does not require target/downstream semantic validation; do not issue such a validation result.
No-drift constraints: Do not assume a shell or reinterpret downstream syntax when it materially affects parsing or validation.
Effectful marker: none.
Portability handoff: separate portability review required before a cross-target claim.
Provenance: POSIX Shell Command Language; Bash manual; high.
Safety projection: catalog metadata only; execution concerns not assessed by this skill.

### SCC-A1 — Scalar and structured argv

Trigger: Input may be one scalar operand or multiple operands.
Construction risk: Word splitting or quoting collapses or expands argument count.
Required facts: Interpreter; scalar/list intent; each intended argument boundary; when byte-level input indicates NUL may be present, whether any intended argv entry contains NUL.
Disposition: VALID, REWRITE, or BLOCKED.
Construction-preserving action: Validate an already-correct confirmed scalar expansion or structured argv form. For a confirmed one-argument parameter expansion, quote it (for example, `"$query"`); for confirmed multiple NUL-free Bash entries, preserve the structured argv form (for example, `"${items[@]}"`). Rewrite a defective form to the applicable representation. Block only when scalar/list or entry-boundary intent is absent, conflicts, or an intended argv entry contains U+0000 NUL.
No-drift constraints: Preserve argument count, order, positions, command name, and fixed operands.
Effectful marker: none.
Portability handoff: separate portability review required before a cross-target claim.
Provenance: POSIX Shell Command Language; Bash manual; high.
Safety projection: catalog metadata only; execution concerns not assessed by this skill.

### SCC-O1 — Paths and leading-dash operands

Trigger: A path contains spaces or an intended operand begins with `-`.
Construction risk: Splitting or option parsing changes the operand.
Required facts: Interpreter; operand boundary; target support for option termination when needed.
Disposition: VALID, REWRITE, or BLOCKED.
Construction-preserving action: Validate an already-correct path boundary and supported option-termination form. Rewrite a defective form while preserving the path as one operand and using the target's confirmed option-termination form; otherwise request supported operand syntax.
No-drift constraints: Preserve options and their order, operand position/count, and path text.
Effectful marker: outside construction scope.
Portability handoff: separate portability review required before a cross-target claim.
Provenance: POSIX Utility Syntax Guidelines; high.
Safety projection: catalog metadata only; execution concerns not assessed by this skill.

### SCC-M1 — Multiline stdin, file, and heredoc payloads

Trigger: Markdown, JSON, commit messages, comments, or other multiline data must reach a supplied stdin, file, or heredoc interface.
Construction risk: Inline quoting, unquoted heredocs, or substitution changes lines or expands payload text.
Required facts: Interpreter; literal/expansion intent; confirmed destination interface and transport; when a heredoc is considered, whether a caller-fixed delimiter occurs alone on any payload line, or otherwise whether a collision-free delimiter can be selected; when a byte-exact payload and a heredoc are considered, terminal-newline intent and, if byte-level input indicates NUL may be present, NUL presence plus confirmed selected-transport capability to preserve it.
Disposition: VALID, REWRITE, or BLOCKED.
Construction-preserving action: Retain the supplied transport; use a quoted heredoc delimiter when literal body text requires it and the payload ends with the heredoc's unavoidable newline before its delimiter. The delimiter must be absent from body delimiter lines. If a caller-required or fixed delimiter collides and no caller-supplied alternate delimiter or transport is allowed, return `BLOCKED`. If the delimiter is selectable, use a confirmed collision-free delimiter without changing payload data. If a byte-exact payload must not end in a newline, retain another confirmed byte-preserving file/stdin-like interface or return `BLOCKED` when none is supplied; do not invent a transport. When byte-level input indicates NUL is present, a heredoc must return `BLOCKED` or switch only to a supplied confirmed NUL-capable transport; heredoc and argv cannot carry NUL, while a supplied file or binary-safe interface may.
No-drift constraints: Preserve line boundaries, empty lines, payload-owned indentation and characters, transport, command name, fixed operands, and redirection placement. The two-space response serialization prefix is not payload data.
Effectful marker: outside construction scope.
Portability handoff: separate portability review required before a cross-target claim.
Provenance: POSIX Shell Command Language; Git documentation; high.
Safety projection: catalog metadata only; execution concerns not assessed by this skill.

### SCC-R1 — Redirections and pipelines

Trigger: A redirection or pipeline's stream binding/order is material.
Construction risk: Ordering binds a stream differently than intended.
Required facts: Interpreter; intended stdin/stdout/stderr routing; command and operand boundaries.
Disposition: VALID, REWRITE, or BLOCKED.
Construction-preserving action: Use the stated ordering only when it realizes the confirmed stream routing; request routing intent when absent.
No-drift constraints: Preserve command order, stream destinations, fixed operands, and selected transport.
Effectful marker: outside construction scope.
Portability handoff: separate portability review required before a cross-target claim.
Provenance: POSIX Shell Command Language; high.
Safety projection: catalog metadata only; execution concerns not assessed by this skill.

### SCC-RX1 — Remote command boundary

Trigger: SSH or another remote-command mechanism carries a command or arguments across a remote execution boundary.
Construction risk: Local shell argv preservation does not guarantee remote argv preservation because SSH typically serializes command text and a remote shell reparses it.
Required facts: Local interpreter; remote interpreter/parser; intended remote argv boundaries; confirmed boundary-preserving transport/serialization contract.
Disposition: BLOCKED by default; VALID or REWRITE only when every required fact is confirmed.
Construction-preserving action: Do not offer a generic remote candidate. If the remote interpreter/parser is absent, request only that parser. After it is known, if the boundary-preserving transport/serialization contract is absent, request only that contract.
No-drift constraints: Preserve confirmed local and remote argument boundaries, command order, and selected transport; do not infer remote quoting semantics from local quoting.
Effectful marker: outside construction scope.
Portability handoff: separate portability review required before a cross-target claim.
Provenance: OpenSSH `ssh(1)` command invocation behavior; POSIX Shell Command Language; high.
Safety projection: catalog metadata only; execution concerns not assessed by this skill.

### SCC-G1 — External glob binding

Trigger: An external command must receive glob-derived operands, or a glob must stay literal.
Construction risk: Pathname expansion silently changes the selected operand set.
Required facts: Interpreter; literal versus expansion intent; explicit pattern scope; bound result set when an external result is required.
Disposition: VALID, REWRITE, or BLOCKED.
Construction-preserving action: Preserve a confirmed literal pattern as literal; preserve a confirmed in-shell expansion; block rather than discover or broaden an external operand set.
No-drift constraints: Preserve the explicit selection scope, operand count/order, command name, and fixed operands.
Effectful marker: outside construction scope.
Portability handoff: separate portability review required before a cross-target claim.
Provenance: POSIX Shell Command Language; high.
Safety projection: catalog metadata only; execution concerns not assessed by this skill.

### SCC-E1 — Empty, unset, and secret-safe sources

Trigger: Empty/unset behavior or secret-bearing data changes construction.
Construction risk: Empty and absent inputs take different paths, or a rendered value exposes sensitive data.
Required facts: Intended empty/unset behavior only when that behavior is at issue; a supplied non-secret source expression or transport abstraction only for secret-bearing input.
Disposition: VALID, REWRITE, or BLOCKED.
Construction-preserving action: Preserve an already-correct supplied non-secret source expression or transport abstraction, or rewrite a defective form. When empty/unset behavior is at issue, request that intent if unavailable; for secret-bearing input, return `BLOCKED` when no secret-safe representation is supplied.
No-drift constraints: Never render raw, partial, split, escaped, encoded, transformed, or diagnostic copies of a secret; preserve supplied transport, argument boundaries, and command structure.
Effectful marker: outside construction scope.
Portability handoff: separate portability review required before a cross-target claim.
Provenance: POSIX Shell Command Language; OWASP Secrets Management Cheat Sheet; medium.
Safety projection: catalog metadata only; execution concerns not assessed by this skill.
