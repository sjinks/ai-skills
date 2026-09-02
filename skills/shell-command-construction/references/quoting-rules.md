Read this reference when a selected construction rule needs shell-semantic detail; it is explanatory and does not define dispositions.

# Quoting Semantics

- In declared POSIX-like `sh`, Bash, ksh, and zsh, single quotes preserve enclosed characters literally and cannot contain a literal single quote without closing and reopening the quote. Within a single-quoted representation, replace each apostrophe with the exact close-single-quote, double-quoted-apostrophe, reopen-single-quote sequence `'"'"'`: literal `O'Reilly $HOME *` becomes `'O'"'"'Reilly $HOME *'`. Adjacent quoted segments with no unquoted whitespace form one shell word. If the shell is undeclared or unsupported and this syntax materially differs, block rather than guess.
- Double quotes preserve one argument boundary while allowing the shell's documented parameter and command substitutions; use them only when that expansion is intended.
- `"$@"` preserves positional parameters as separate arguments; `"$*"` has different joining behavior.
- Unquoted parameter expansion and pathname expansion can change argument count. A shell array is a Bash-family structure, not a portable default.
- A quoted heredoc delimiter, such as `<<'EOF'`, prevents parameter expansion, command substitution, and backslash interpretation in the body. The chosen delimiter must not occur alone on a body line.
- Shell redirections are processed according to their written order, so a change in order can change where standard error goes.
- Command substitution is not a general transport for arbitrary multiline argv data: it can trim trailing newlines and introduces a new parsing boundary.
- `--` is conventionally an option terminator, but command support must be known before using it for a leading-dash operand.
- Local shell argv does not guarantee remote argv across SSH or another remote boundary: SSH typically serializes command text and a remote shell reparses it. Require the remote interpreter/parser and a confirmed boundary-preserving transport/serialization contract; otherwise block and offer no generic remote candidate.
- Never reveal raw, partial, split, escaped, encoded, transformed, or diagnostic copies of a secret. Use only a supplied non-secret source expression or transport abstraction.

These semantics describe only parsing and delivery. They do not assess execution safety, authorization, target validity, destructive effects, or permission to run.
