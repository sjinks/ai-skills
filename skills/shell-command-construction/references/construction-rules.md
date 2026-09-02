Read this catalog when selecting a construction disposition; it is the sole normative owner of the construction decisions in this package.

# Construction Rules

All records use this fixed shape. `Safety projection` never assesses execution concerns.

### SCC-Q1 — Literal scalar text

Trigger: One confirmed scalar must remain literal through shell parsing.
Construction risk: Spaces, quotes, `$`, backticks, `!`, globs, or backslashes are expanded, split, or reparsed.
Required facts: Interpreter; one scalar intent; literal versus expansion intent.
Disposition: VALID or REWRITE.
Construction-preserving action: For declared POSIX-like `sh`, Bash, ksh, or zsh, single-quote literal scalar text. Within that representation, replace each embedded apostrophe with the exact close-single-quote, double-quoted-apostrophe, reopen-single-quote sequence `'"'"'`. For example, literal `O'Reilly $HOME *` is `'O'"'"'Reilly $HOME *'`; adjacent quoted segments with no unquoted whitespace form one shell word. Use a quoted heredoc for literal multiline text. If the shell is undeclared or unsupported and the syntax materially differs, return BLOCKED.
No-drift constraints: Preserve command name, fixed operands, option order, one-argument boundary, and literal bytes/characters.
Effectful marker: none.
Portability handoff: `shell-portability` review required before a cross-target claim.
Provenance: POSIX Shell Command Language; Bash manual; high.
Safety projection: not assessed by this skill.

### SCC-Q2 — Expansion and quote ambiguity

Trigger: `$`, command substitution syntax, history-sensitive `!`, glob characters, backslashes, or quote boundaries have unspecified intent.
Construction risk: A plausible quote choice changes data into expansion or expansion into literal data.
Required facts: Interpreter; literal/expansion intent; intended quote boundary.
Disposition: BLOCKED.
Construction-preserving action: Request the one missing literal/expansion or quote-boundary fact.
No-drift constraints: Do not assume a shell or reinterpret downstream syntax.
Effectful marker: none.
Portability handoff: `shell-portability` review required before a cross-target claim.
Provenance: POSIX Shell Command Language; Bash manual; high.
Safety projection: not assessed by this skill.

### SCC-A1 — Scalar and structured argv

Trigger: Input may be one scalar operand or multiple operands.
Construction risk: Word splitting or quoting collapses or expands argument count.
Required facts: Interpreter; scalar/list intent; each intended argument boundary.
Disposition: REWRITE or BLOCKED.
Construction-preserving action: Quote a confirmed single scalar; use a declared-shell structured argv form only for confirmed multiple entries; otherwise request scalar/list intent.
No-drift constraints: Preserve argument count, order, positions, command name, and fixed operands.
Effectful marker: none.
Portability handoff: `shell-portability` review required before a cross-target claim.
Provenance: POSIX Shell Command Language; Bash manual; high.
Safety projection: not assessed by this skill.

### SCC-O1 — Paths and leading-dash operands

Trigger: A path contains spaces or an intended operand begins with `-`.
Construction risk: Splitting or option parsing changes the operand.
Required facts: Interpreter; operand boundary; target support for option termination when needed.
Disposition: REWRITE or BLOCKED.
Construction-preserving action: Preserve the path as one operand and use the target's confirmed option-termination form; otherwise request supported operand syntax.
No-drift constraints: Preserve options and their order, operand position/count, and path text.
Effectful marker: outside construction scope.
Portability handoff: `shell-portability` review required before a cross-target claim.
Provenance: POSIX Utility Syntax Guidelines; high.
Safety projection: not assessed by this skill.

### SCC-M1 — Multiline stdin, file, and heredoc payloads

Trigger: Markdown, JSON, commit messages, comments, or other multiline data must reach a known stdin, file, or heredoc interface.
Construction risk: Inline quoting, unquoted heredocs, or substitution changes lines or expands payload text.
Required facts: Interpreter; literal/expansion intent; confirmed destination interface and transport.
Disposition: VALID, REWRITE, or BLOCKED.
Construction-preserving action: Retain the supplied transport; use a quoted heredoc delimiter when literal body text requires it; block if choosing stdin versus file would be invented.
No-drift constraints: Preserve line boundaries, empty lines, payload-owned indentation and characters, transport, command name, fixed operands, and redirection placement. The two-space response serialization prefix is not payload data.
Effectful marker: outside construction scope.
Portability handoff: `shell-portability` review required before a cross-target claim.
Provenance: POSIX Shell Command Language; Git documentation; high.
Safety projection: not assessed by this skill.

### SCC-R1 — Redirections and pipelines

Trigger: A redirection or pipeline's stream binding/order is material.
Construction risk: Ordering binds a stream differently than intended.
Required facts: Interpreter; intended stdin/stdout/stderr routing; command and operand boundaries.
Disposition: VALID, REWRITE, or BLOCKED.
Construction-preserving action: Use the stated ordering only when it realizes the confirmed stream routing; request routing intent when absent.
No-drift constraints: Preserve command order, stream destinations, fixed operands, and selected transport.
Effectful marker: outside construction scope.
Portability handoff: `shell-portability` review required before a cross-target claim.
Provenance: POSIX Shell Command Language; high.
Safety projection: not assessed by this skill.

### SCC-RX1 — Remote command boundary

Trigger: SSH or another remote-command mechanism carries a command or arguments across a remote execution boundary.
Construction risk: Local shell argv preservation does not guarantee remote argv preservation because SSH typically serializes command text and a remote shell reparses it.
Required facts: Local interpreter; remote interpreter/parser; intended remote argv boundaries; confirmed boundary-preserving transport/serialization contract.
Disposition: BLOCKED by default; VALID or REWRITE only when every required fact is confirmed.
Construction-preserving action: Do not offer a generic remote candidate. Request the remote interpreter/parser and confirmed boundary-preserving transport/serialization contract when either is absent.
No-drift constraints: Preserve confirmed local and remote argument boundaries, command order, and selected transport; do not infer remote quoting semantics from local quoting.
Effectful marker: outside construction scope.
Portability handoff: `shell-portability` review required before a cross-target claim.
Provenance: OpenSSH `ssh(1)` command invocation behavior; POSIX Shell Command Language; high.
Safety projection: not assessed by this skill.

### SCC-G1 — External glob binding

Trigger: An external command must receive glob-derived operands, or a glob must stay literal.
Construction risk: Pathname expansion silently changes the selected operand set.
Required facts: Interpreter; literal versus expansion intent; explicit pattern scope; bound result set when an external result is required.
Disposition: VALID, REWRITE, or BLOCKED.
Construction-preserving action: Preserve a confirmed literal pattern as literal; preserve a confirmed in-shell expansion; block rather than discover or broaden an external operand set.
No-drift constraints: Preserve the explicit selection scope, operand count/order, command name, and fixed operands.
Effectful marker: outside construction scope.
Portability handoff: `shell-portability` review required before a cross-target claim.
Provenance: POSIX Shell Command Language; high.
Safety projection: not assessed by this skill.

### SCC-E1 — Empty, unset, and secret-safe sources

Trigger: Empty/unset behavior or secret-bearing data changes construction.
Construction risk: Empty and absent inputs take different paths, or a rendered value exposes sensitive data.
Required facts: Intended empty/unset behavior; supplied non-secret source expression or transport abstraction.
Disposition: VALID, REWRITE, or BLOCKED.
Construction-preserving action: Preserve a supplied non-secret source expression or transport abstraction; otherwise request the empty/unset intent or return `BLOCKED` for unavailable secret-safe representation.
No-drift constraints: Never render raw, partial, split, escaped, encoded, transformed, or diagnostic copies of a secret; preserve supplied transport, argument boundaries, and command structure.
Effectful marker: outside construction scope.
Portability handoff: `shell-portability` review required before a cross-target claim.
Provenance: POSIX Shell Command Language; OWASP Secrets Management Cheat Sheet; medium.
Safety projection: not assessed by this skill.
