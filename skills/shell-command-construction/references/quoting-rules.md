Read Quoting Semantics when a selected construction rule needs shell-semantic detail. Read Source Map when source confidence or scope provenance matters. This reference is explanatory and does not define dispositions.

# Quoting Semantics

- In declared POSIX-like shells—including `sh`, `dash`, and BusyBox `ash`—and in Bash, ksh, and zsh, single quotes preserve enclosed characters literally and cannot contain a literal single quote without closing and reopening the quote. Within a single-quoted representation, each apostrophe has the exact close-single-quote, double-quoted-apostrophe, reopen-single-quote form `'"'"'`: literal `O'Reilly $HOME *` is `'O'"'"'Reilly $HOME *'`. Adjacent quoted segments with no unquoted whitespace form one shell word. An undeclared or unsupported shell with materially different syntax is an unresolved construction fact for SCC-Q1 or SCC-Q2.
- Double quotes preserve one argument boundary while allowing the shell's documented parameter and command substitutions. Unspecified expansion intent remains an SCC-Q2 ambiguity; confirmed one-argument expansion intent (including intentional command substitution such as `"$(date)"`) is evaluated by SCC-A1.
- In Bash, when history expansion is enabled, `!` in history-expandable positions can expand, including inside double quotes outside POSIX mode. Interactive Bash enables history expansion by default; non-interactive Bash can enable it explicitly. In Bash POSIX mode, `!` has no history-expansion meaning inside double quotes. Single-quoted literal text prevents history expansion; single quotes appearing inside an outer double-quoted string do not establish that protection. Bash also treats `!` immediately before a closing double quote as quoted. Backslash-escaping `!` inside double quotes retains that backslash in the argument; it is not a byte-equivalent replacement for a literal exclamation mark. For literal `!` in a potentially expandable position, establish the relevant Bash mode/options or use the SCC-Q1 single-quoted representation. SCC-Q2 blocks when those construction facts are unresolved.
- An unquoted backslash immediately followed by LF removes both characters as a line continuation; this is not a payload newline. Backslash-LF is also removed inside double quotes. Single quotes preserve both characters literally. Preserve an intentional continuation; when a payload requires the LF, use a representation that retains it under the confirmed literal/expansion intent. These rules concern an immediately adjacent backslash and LF, not a backslash followed by spaces or CRLF.
- `"$@"` preserves positional parameters as separate arguments; `"$*"` has different joining behavior.
- Unquoted parameter expansion and pathname expansion can change argument count. A shell array is a Bash-family structure, not a portable default.
- A quoted heredoc delimiter, such as `<<'EOF'`, prevents parameter expansion, command substitution, and backslash interpretation in the body. With `<<-`, leading tabs are stripped from body and delimiter lines even with a quoted delimiter; spaces remain. The delimiter cannot occur alone on a body line after that processing. An immediately terminating delimiter gives an empty body and delivers zero bytes. A nonempty literal body includes the LF terminating its final body line; one blank body line delivers LF. The opening command line's LF is not body data. SCC-M1 evaluates empty/nonempty intent, terminal-newline intent, and NUL preservation. Heredocs and argv cannot carry U+0000 NUL; a supplied file or binary-safe interface may preserve it when its transport contract confirms that behavior.
- In Bash, a here-string `<<< word` performs the documented expansions and quote removal without word splitting or pathname expansion, then supplies the resulting string plus one LF. Empty strings still deliver LF; strings already ending in LF gain another. SCC-M1 evaluates exact-byte compatibility and preserves intentional appended newlines.
- Shell redirections are processed according to their written order, so a change in order can change where standard error goes.
- Ordinary `$(...)` command substitution removes trailing newlines in POSIX-like shells and Bash, even inside double quotes. Double quotes preserve one argument, not those removed bytes. SCC-A1 requires compatibility with exact-byte intent when that intent matters; intentional one-argument substitution without such an exact-byte requirement remains supported.
- For a caller-confirmed `printf` transport that delivers literal text, a fixed format such as `printf '%s' "$payload"` treats the payload as data; `printf '%s\n' "$payload"` adds a newline. In Bash `printf`, `%b` interprets backslash escapes in its corresponding argument; `printf '%b' "$payload"` therefore does not deliver arbitrary literal text like `%s` does. Preserve `%b` when escape interpretation is the caller's confirmed intent. Putting the payload in the format position, as in `printf "$payload"`, interprets its percent conversions and backslash escapes. This distinction concerns the selected payload transport, not general formatting review. Preserve intentional caller-supplied formats and newline intent. Do not invent a `printf` transport or change confirmed argument roles; unresolved transport facts use the core required-fact gate.
- `--` is conventionally an option terminator, and command support is a construction fact for SCC-O1.
- Local shell argv does not guarantee remote argv across SSH or another remote boundary: SSH typically serializes command text and a remote shell reparses it. The remote interpreter/parser and a boundary-preserving transport/serialization contract are facts evaluated by SCC-RX1.
- POSIX-like shell words and process argv cannot carry U+0000 NUL. Textual escape forms such as `\0`, `\x00`, and `\u0000` are ordinary representable text unless byte-level input identifies an actual U+0000 NUL. The resulting argv scalar fact is evaluated by SCC-Q1; supplied stdin, file, and heredoc transport facts are evaluated by SCC-M1.
- Raw, partial, split, escaped, encoded, transformed, and diagnostic copies expose secret material. The available source-expression or transport fact is evaluated by SCC-E1.

These semantics describe only parsing and delivery. They do not assess execution safety, authorization, target validity, destructive effects, or permission to run.

## Source Map

| Area | Sources | Confidence |
|---|---|---|
| Shell quoting, expansions, heredocs, redirections, and pathname expansion | [POSIX Shell Command Language](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html); [GNU Bash Reference Manual](https://www.gnu.org/s/bash/manual/bash.html) | High |
| Bash history-sensitive quoting | GNU Bash Reference Manual, History Expansion and Double Quotes sections | High |
| Literal `printf` payload delivery | GNU Bash Reference Manual, Bash Builtins section; GNU Coreutils manual, printf invocation | High |
| Utility option termination | POSIX Utility Syntax Guidelines | High |
| Git multiline message interfaces | Git documentation | High |
| Remote command serialization and reparsing | OpenSSH `ssh(1)` manual | High |
| Secret-safe representation boundary | OWASP Secrets Management Cheat Sheet | Medium |

### Ownership boundary

This package is the normative owner for construction dispositions, required construction facts, boundary-preserving actions, and no-drift constraints. The catalog records include a `Safety projection` metadata field only; it is not part of the user-facing output contract. Its value always states that execution concerns are not assessed by this skill.

Construction output does not assess execution safety, authorization, target validity, destructive effects, or permission to run. Portability-only requests are excluded; mixed requests require a separate portability review before a compatibility conclusion.

### Package policy versus shell semantics

The Bash manual documents ordinary command substitution removing trailing newlines. The exact-byte gate, construction-only authority boundary, and report framing are package policies, not protections enforced by the shell. LF framing does not redefine other candidate characters as separators.
