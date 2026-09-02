Read this reference when a selected construction rule needs shell-semantic detail; it is explanatory and does not define dispositions.

# Quoting Semantics

- In declared POSIX-like `sh`, Bash, ksh, and zsh, single quotes preserve enclosed characters literally and cannot contain a literal single quote without closing and reopening the quote. Within a single-quoted representation, each apostrophe has the exact close-single-quote, double-quoted-apostrophe, reopen-single-quote form `'"'"'`: literal `O'Reilly $HOME *` is `'O'"'"'Reilly $HOME *'`. Adjacent quoted segments with no unquoted whitespace form one shell word. An undeclared or unsupported shell with materially different syntax is an unresolved construction fact for SCC-Q1 or SCC-Q2.
- Double quotes preserve one argument boundary while allowing the shell's documented parameter and command substitutions. Whether that expansion matches the supplied intent is evaluated by SCC-Q2.
- `"$@"` preserves positional parameters as separate arguments; `"$*"` has different joining behavior.
- Unquoted parameter expansion and pathname expansion can change argument count. A shell array is a Bash-family structure, not a portable default.
- A quoted heredoc delimiter, such as `<<'EOF'`, prevents parameter expansion, command substitution, and backslash interpretation in the body. The delimiter cannot occur alone on a body line. A heredoc body has a newline before its delimiter; its terminal-newline and NUL-preservation facts are evaluated by SCC-M1. Heredocs and argv cannot carry U+0000 NUL; a supplied file or binary-safe interface may preserve it when its transport contract confirms that behavior.
- Shell redirections are processed according to their written order, so a change in order can change where standard error goes.
- Command substitution is not a general transport for arbitrary multiline argv data: it can trim trailing newlines and introduces a new parsing boundary.
- `--` is conventionally an option terminator, and command support is a construction fact for SCC-O1.
- Local shell argv does not guarantee remote argv across SSH or another remote boundary: SSH typically serializes command text and a remote shell reparses it. The remote interpreter/parser and a boundary-preserving transport/serialization contract are facts evaluated by SCC-RX1.
- POSIX-like shell words and process argv cannot carry U+0000 NUL. Textual escape forms such as `\0`, `\x00`, and `\u0000` are ordinary representable text unless byte-level input identifies an actual U+0000 NUL. The resulting argv scalar fact is evaluated by SCC-Q1; supplied stdin, file, and heredoc transport facts are evaluated by SCC-M1.
- Raw, partial, split, escaped, encoded, transformed, and diagnostic copies expose secret material. The available source-expression or transport fact is evaluated by SCC-E1.

These semantics describe only parsing and delivery. They do not assess execution safety, authorization, target validity, destructive effects, or permission to run.
