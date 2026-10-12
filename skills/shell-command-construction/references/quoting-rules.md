Read Quoting Semantics when a selected construction rule needs shell-semantic detail. Read Source Map when source confidence or scope provenance matters. This reference is explanatory and does not define dispositions.

# Quoting Semantics

- In declared POSIX-like `sh`, Bash, ksh, and zsh, single quotes preserve enclosed characters literally and cannot contain a literal single quote without closing and reopening the quote. Within a single-quoted representation, each apostrophe has the exact close-single-quote, double-quoted-apostrophe, reopen-single-quote form `'"'"'`: literal `O'Reilly $HOME *` is `'O'"'"'Reilly $HOME *'`. Adjacent quoted segments with no unquoted whitespace form one shell word. An undeclared or unsupported shell with materially different syntax is an unresolved construction fact for SCC-Q1 or SCC-Q2.
- Double quotes preserve one argument boundary while allowing the shell's documented parameter and command substitutions. Unspecified expansion intent remains an SCC-Q2 ambiguity; confirmed one-argument expansion intent (including intentional command substitution such as `"$(date)"`) is evaluated by SCC-A1.
- `"$@"` preserves positional parameters as separate arguments; `"$*"` has different joining behavior.
- Unquoted parameter expansion and pathname expansion can change argument count. A shell array is a Bash-family structure, not a portable default.
- A quoted heredoc delimiter, such as `<<'EOF'`, prevents parameter expansion, command substitution, and backslash interpretation in the body. The delimiter cannot occur alone on a body line. A heredoc body has a newline before its delimiter; its terminal-newline and NUL-preservation facts are evaluated by SCC-M1. Heredocs and argv cannot carry U+0000 NUL; a supplied file or binary-safe interface may preserve it when its transport contract confirms that behavior.
- Shell redirections are processed according to their written order, so a change in order can change where standard error goes.
- Ordinary `$(...)` command substitution removes trailing newlines in POSIX-like shells and Bash, even inside double quotes. Double quotes preserve one argument, not those removed bytes. SCC-A1 requires compatibility with exact-byte intent when that intent matters; intentional one-argument substitution without such an exact-byte requirement remains supported.
- `--` is conventionally an option terminator, and command support is a construction fact for SCC-O1.
- Local shell argv does not guarantee remote argv across SSH or another remote boundary: SSH typically serializes command text and a remote shell reparses it. The remote interpreter/parser and a boundary-preserving transport/serialization contract are facts evaluated by SCC-RX1.
- POSIX-like shell words and process argv cannot carry U+0000 NUL. Textual escape forms such as `\0`, `\x00`, and `\u0000` are ordinary representable text unless byte-level input identifies an actual U+0000 NUL. The resulting argv scalar fact is evaluated by SCC-Q1; supplied stdin, file, and heredoc transport facts are evaluated by SCC-M1.
- Raw, partial, split, escaped, encoded, transformed, and diagnostic copies expose secret material. The available source-expression or transport fact is evaluated by SCC-E1.

These semantics describe only parsing and delivery. They do not assess execution safety, authorization, target validity, destructive effects, or permission to run.

## Source Map

| Area | Sources | Confidence |
|---|---|---|
| Shell quoting, expansions, heredocs, redirections, and pathname expansion | [POSIX Shell Command Language](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html); [GNU Bash Reference Manual](https://www.gnu.org/s/bash/manual/bash.html) | High |
| Utility option termination | POSIX Utility Syntax Guidelines | High |
| Git multiline message interfaces | Git documentation | High |
| Remote command serialization and reparsing | OpenSSH `ssh(1)` manual | High |
| Secret-safe representation boundary | OWASP Secrets Management Cheat Sheet | Medium |

### Ownership boundary

This package is the normative owner for construction dispositions, required construction facts, boundary-preserving actions, and no-drift constraints. The catalog records include a `Safety projection` metadata field only; it is not part of the user-facing output contract. Its value always states that execution concerns are not assessed by this skill.

Construction output does not assess execution safety, authorization, target validity, destructive effects, or permission to run. Portability-only requests are excluded; mixed requests require a separate portability review before a compatibility conclusion.

### Package policy versus shell semantics

The Bash manual documents ordinary command substitution removing trailing newlines. The exact-byte gate, construction-only authority boundary, and report framing are package policies, not protections enforced by the shell. LF framing does not redefine other candidate characters as separators.
