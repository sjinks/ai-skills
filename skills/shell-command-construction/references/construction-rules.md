Read this catalog when selecting a construction disposition; it is the sole normative owner of the construction decisions in this package.

## Composition and precedence

Select every applicable canonical rule, not one rule by preference. Representability and fail-closed constraints always apply. Transport- and boundary-specific rules constrain the candidate. SCC-A1 owns scalar/list intent and confirmed expansion-source argv boundaries (including parameter and command substitution); SCC-Q1 applies only to directly supplied literal scalar data, never an expansion source. Combine nonconflicting no-drift constraints. If applicable actions conflict after this precedence, or a required fact is missing, return `BLOCKED`.

# Construction Rules

All records use this fixed shape. The catalog-only `Safety projection` field is metadata; it never assesses execution concerns and is not part of the user-facing output contract.

### SCC-Q1 — Direct literal scalar text

Trigger: Directly supplied literal scalar data must remain literal through shell parsing; this does not cover a parameter-expansion source.
Construction risk: Spaces, quotes, `$`, backticks, `!`, globs, or backslashes are expanded, split, or reparsed.
Required facts: Interpreter and relevant modes/options when syntax or quoting behavior materially differs; one scalar intent; literal versus expansion intent; when byte-level input indicates NUL may be present, whether the scalar contains NUL.
Disposition: VALID, REWRITE, or BLOCKED.
Construction-preserving action: POSIX-like shell words and process argv cannot represent U+0000 NUL. If the intended scalar contains NUL, return BLOCKED even when every other fact is complete, with `Construction candidate: Not provided`; request a confirmed non-argv NUL-capable transport/interface rather than inventing one. Otherwise, first validate and preserve any supplied representation that already keeps the confirmed literal scalar as exactly one shell word. Rewrite a defective or absent representation for declared POSIX-like shells—including `sh`, `dash`, and BusyBox `ash`—or Bash, ksh, or zsh by single-quoting the literal scalar text. Within that representation, replace each embedded apostrophe with the exact close-single-quote, double-quoted-apostrophe, reopen-single-quote sequence `'"'"'`. For example, literal `O'Reilly $HOME *` is `'O'"'"'Reilly $HOME *'`; adjacent quoted segments with no unquoted whitespace form one shell word. A multiline scalar remains one quoted shell word containing its newline; do not change its transport to stdin, a file, or a heredoc. If the shell is undeclared or unsupported and the syntax materially differs, return BLOCKED.
No-drift constraints: Preserve command name, fixed operands, option order, the one-argv-entry boundary, and literal bytes/characters, including embedded newlines.
Effectful marker: none.
Portability handoff: separate portability review required before a cross-target claim.
Provenance: POSIX Shell Command Language; Bash manual; high.
Safety projection: catalog metadata only; execution concerns not assessed by this skill.

### SCC-Q2 — Expansion and quote ambiguity

Trigger: `$`, command substitution syntax, history-sensitive `!`, glob characters, backslashes, or quote boundaries have unspecified shell intent; or downstream token boundaries materially determine shell parsing and are unknown.
Construction risk: A plausible quote choice changes data into expansion or expansion into literal data.
Required facts: Interpreter and relevant modes/options when syntax or quoting behavior materially differs, including Bash history-expansion and POSIX-mode settings for history-sensitive `!`; literal/expansion intent; intended quote boundary; downstream-language grammar only when its token boundaries materially determine shell parsing.
Disposition: BLOCKED.
Construction-preserving action: Request the one missing interpreter-mode/option, literal/expansion, quote-boundary, or parsing-relevant downstream-token-boundary fact. Exact supplied literal argument text with confirmed shell boundaries does not require target/downstream semantic validation; do not issue such a validation result.
No-drift constraints: Do not assume a shell or reinterpret downstream syntax when it materially affects parsing or validation.
Effectful marker: none.
Portability handoff: separate portability review required before a cross-target claim.
Provenance: POSIX Shell Command Language; Bash manual; high.
Safety projection: catalog metadata only; execution concerns not assessed by this skill.

### SCC-A1 — Scalar and structured argv

Trigger: Input may be one scalar operand or multiple operands.
Construction risk: Word splitting or quoting collapses or expands argument count.
Required facts: Interpreter when syntax materially differs; scalar/list intent; each intended argument boundary; for command substitution when exact output bytes matter, compatibility of its documented trailing-newline removal with the intended argument; when byte-level input indicates NUL may be present, whether any intended argv entry contains NUL.
Disposition: VALID, REWRITE, or BLOCKED.
Construction-preserving action: Validate an already-correct confirmed scalar expansion or structured argv form. For a confirmed one-argument expansion source, preserve one argument boundary (for example, `"$query"` or `"$(date)"` when command substitution is intentional and one argument is required); for confirmed multiple NUL-free Bash entries, preserve the structured argv form (for example, `"${items[@]}"`). Quoting preserves argument count, not bytes already changed by substitution. When exact output bytes matter, establish that the selected substitution preserves the required bytes; ordinary `$(...)` removes trailing newlines in POSIX-like shells and Bash. If required newlines would be lost, use only a caller-supplied confirmed byte-preserving representation permitted by the no-drift rules; otherwise return BLOCKED and request that representation. Rewrite a defective form to the applicable representation. Block when the materially required interpreter, scalar/list intent, or entry-boundary intent is absent or conflicts, or an intended argv entry contains U+0000 NUL.
No-drift constraints: Preserve argument count, order, positions, command name, and fixed operands.
Effectful marker: none.
Portability handoff: separate portability review required before a cross-target claim.
Provenance: POSIX Shell Command Language; Bash manual; high.
Safety projection: catalog metadata only; execution concerns not assessed by this skill.

### SCC-O1 — Paths and leading-dash operands

Trigger: A path contains spaces or an intended operand begins with `-`.
Construction risk: Splitting or option parsing changes the operand.
Required facts: Interpreter when syntax materially differs; operand boundary; target support for option termination when needed.
Disposition: VALID, REWRITE, or BLOCKED.
Construction-preserving action: Validate an already-correct path boundary and supported option-termination form. Rewrite a defective form while preserving the path as one operand and using the target's confirmed option-termination form; otherwise request supported operand syntax.
No-drift constraints: Preserve options and their order, operand position/count, and path text.
Effectful marker: outside construction scope.
Portability handoff: separate portability review required before a cross-target claim.
Provenance: POSIX Utility Syntax Guidelines; high.
Safety projection: catalog metadata only; execution concerns not assessed by this skill.

### SCC-M1 — Stdin, file, heredoc, and here-string payloads

Trigger: Literal or expanded payload data must reach a supplied stdin, file, heredoc, or here-string interface.
Construction risk: Quoting, substitution, tab stripping, or an appended newline changes payload bytes or delimiter recognition.
Required facts: Interpreter when syntax materially differs; literal/expansion intent; confirmed destination interface and transport. For a heredoc, establish whether its delimiter is fixed or selectable and whether it collides after the selected operator's leading-tab processing. For `<<-` with leading tabs, establish whether stripped tabs are syntactic indentation or required payload. If correction requires an operator change, establish whether it is allowed. When exact bytes matter, establish heredoc terminal-newline intent or compatibility with the Bash here-string's appended LF. If byte-level input indicates NUL may be present, establish NUL presence and the selected transport's preservation capability.
Disposition: VALID, REWRITE, or BLOCKED.
Construction-preserving action:
- Retain the confirmed required transport; an explicitly required caller-supplied transport supersedes a defective proposal. Preserve an already-correct supplied form as VALID.
- For literal heredoc text, use a quoted delimiter when required to prevent expansion. A heredoc necessarily supplies the newline before its delimiter. If exact payload bytes must omit that newline, use only a supplied confirmed byte-preserving alternative or return BLOCKED.
- With `<<-`, the shell strips all leading tabs from body and delimiter lines even when the delimiter is quoted; it does not strip spaces. Preserve this form when the stripped tabs are confirmed syntactic indentation. If required payload tabs would be stripped, change to plain `<<` only when the caller allows that operator change and it preserves the required payload; otherwise use only a supplied confirmed alternative or return BLOCKED. Unknown tab ownership requires BLOCKED.
- Check delimiter collisions after the selected operator's leading-tab processing. If a fixed delimiter collides, use only a caller-supplied allowed alternate delimiter or transport; otherwise return BLOCKED. If selection is allowed, choose a collision-free delimiter without changing payload data. Recheck collisions after any operator change.
- In declared Bash, `<<< word` delivers the expanded word followed by one LF, including when the word is empty or already ends in LF. When exact bytes matter, preserve the here-string only if those delivered bytes match intended stdin. Otherwise use only a supplied confirmed byte-preserving alternative or return BLOCKED; do not remove or add payload newlines to compensate. Missing newline intent requires BLOCKED when it changes the decision.
- If actual NUL is present, heredoc, Bash here-string, and argv cannot preserve it. Use only a supplied confirmed NUL-capable file or binary-safe interface, or return BLOCKED.
No-drift constraints: Preserve line boundaries, empty lines, payload-owned indentation and characters, the confirmed required transport, command name, fixed operands, and redirection placement. Heredoc operator changes require the caller's permission stated above. The two-space response serialization prefix is not payload data.
Effectful marker: outside construction scope.
Portability handoff: separate portability review required before a cross-target claim.
Provenance: POSIX Shell Command Language; GNU Bash Reference Manual, Here Documents and Here Strings; high.
Safety projection: catalog metadata only; execution concerns not assessed by this skill.

### SCC-R1 — Redirections and pipelines

Trigger: A redirection or pipeline's stream binding/order is material.
Construction risk: Ordering binds a stream differently than intended.
Required facts: Interpreter when syntax materially differs; intended stdin/stdout/stderr routing; command and operand boundaries.
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
Required facts: Local interpreter when syntax materially differs; remote interpreter/parser; intended remote argv boundaries; confirmed boundary-preserving transport/serialization contract.
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
Required facts: Interpreter when syntax materially differs; literal versus expansion intent; explicit pattern scope; bound result set when an external result is required.
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
