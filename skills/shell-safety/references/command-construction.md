# Command Construction

Read this when a command review involves commit-message construction, quoting, substitutions, heredocs, redirection, shell modes, secrets, or encoding.

Each record keeps the unsafe form, its risk, decision gate, and safe replacement together; retain separate inspection and mutation phases.

## Git commit messages

### GC1 - Multi-line `-m`
Example: `git commit -m "Subject\n\nBody"`

Risk: The literal `\n` is recorded instead of newlines.

Decision gate: Rewrite.

Safe replacement:
```sh
git commit -F - <<'EOF'
Subject

Body paragraph.
EOF
```
Review the exact literal heredoc before execution. Git consumes those bytes directly from stdin, so no replaceable temporary pathname exists between review and use.

### GC2 - Repeated `-m`
Example: `git commit -m "Subject" -m "Body line 1" -m "Body line 2"`

Risk: Each `-m` becomes a paragraph and bodies with lists or code are error-prone.

Decision gate: Rewrite.

Safe replacement: Prefer GC1's reviewed stdin sequence for any body beyond a subject.

### GC3 - Substitution in `-m`
Example: `git commit -m "Fix: $(cat issue.txt)"`

Risk: Embedded newlines and shell-special text can produce malformed messages.

Decision gate: Rewrite.

Safe replacement: Resolve and review the message content, then place those exact literal bytes in GC1's quoted heredoc. Do not review one pathname and let Git reopen it later.

### GC4 - Variable in `-m`
Example: `git commit -m "Fix: $TITLE"`

Risk: Newlines and shell-special content make the message ambiguous.

Decision gate: Rewrite.

Safe replacement: Resolve and restate `TITLE` without losing its line boundaries, review the exact result, then place those literal bytes in GC1's quoted heredoc.

### GC5 - Backtick substitution
Example: ``git commit -m "ship at `date"``

Risk: Backticks are difficult to nest and escape.

Decision gate: Rewrite.

Safe replacement: Resolve the date first, review the exact result, then place it as literal text in GC1's quoted heredoc.

### GC6 - Backtick or quote in `-m`
Example: ``git commit -m "use `foo()` here"``

Risk: The backtick triggers a failing command substitution.

Decision gate: Rewrite.

Safe replacement: Use GC1's quoted heredoc with the literal subject ``use `foo()` here``.

### GC7 - Apostrophe in single-quoted `-m`
Example: `git commit -m 'it\'s broken'`

Risk: Single quotes do not permit backslash escaping.

Decision gate: Rewrite.

Safe replacement: Use GC1's quoted heredoc with the literal subject `it's broken`.

### GC8 - Unicode in a non-UTF-8 terminal
Example: `git commit -m "🎉 ship"`

Risk: A legacy terminal or locale can mangle multi-byte characters.

Decision gate: Rewrite.

Safe replacement: In a verified UTF-8 terminal, use GC1's quoted heredoc with the reviewed literal UTF-8 text.

## Quoting and expansion

### Q1 - Unquoted variable in an argument
Example: `rm $file`

Risk: Word splitting and pathname expansion change the argument list.

Decision gate: Rewrite.

Safe replacement: `rm -- "$file"`.

### Q2 - Unquoted variable in a path
Example: `cd $dir`

Risk: Word splitting and pathname expansion change the path.

Decision gate: Rewrite.

Safe replacement: `cd -- "$dir"`.

### Q3 - `for` over `$(ls)`
Example: `for f in $(ls); do ...; done`

Risk: Whitespace in names becomes separate iterations.

Decision gate: Rewrite.

Safe replacement:
```sh
for f in *; do ...; done
```
For Bash/zsh NUL-delimited input:
```bash
while IFS= read -r -d '' f; do ...; done < <(find . -type f -print0)
```

### Q4 - Unquoted glob
Example: `mv *.log /tmp`

Risk: No-match behavior differs by shell and a literal glob is ambiguous.

Decision gate: Inspect then confirm matching directory state.

Safe replacement:
```sh
ls -- *.log
```
After reviewing the expansion:
```sh
mv -- *.log /tmp/
```

### Q5 - Unquoted `$@`
Example: `cmd $@`

Risk: Each argument can split further.

Decision gate: Rewrite.

Safe replacement: `cmd "$@"`.

### Q6 - Path with spaces
Example: `cat /tmp/my file.txt`

Risk: This supplies two paths.

Decision gate: Rewrite.

Safe replacement: `cat "/tmp/my file.txt"`.

### Q7 - Variable in single quotes
Example: `echo '$HOME'`

Risk: Single quotes prevent the intended expansion.

Decision gate: Rewrite when expansion is wanted.

Safe replacement: `echo "$HOME"`.

### Q8 - Mixed quotes
Example: `echo "it's $name"`

Risk: A missing closing quote can consume the rest of a script.

Decision gate: Inspect intent.

Safe replacement: `printf "%s\n" "it's $name"`.

### Q9 - Backslash escapes in single quotes
Example: `echo 'a\nb'`

Risk: `\n` remains literal and `echo -e` is non-portable.

Decision gate: Rewrite.

Safe replacement: `printf '%s\n%s\n' a b`.

### Q10 - Filename beginning with `-`
Example: `rm -file`

Risk: The name is parsed as options.

Decision gate: Rewrite.

Safe replacement: `rm -- -file`.

### Q11 - Bash history expansion in double quotes
Example: `echo "deploy!"`

Risk: Interactive history expansion can substitute history or fail.

Decision gate: Rewrite.

Safe replacement:
```sh
echo 'deploy!'
```
Or in Bash:
```bash
set +H
echo "deploy!"
```

## Command substitution and pipes

### CS1 - Backtick substitution
Example: ``echo "today is `date"``

Risk: Backticks do not nest and are hard to escape.

Decision gate: Rewrite.

Safe replacement: `echo "today is $(date)"`.

### CS2 - Unquoted nested substitution
Example: `echo $(echo $(date))`

Risk: Output word-splits at each level.

Decision gate: Rewrite.

Safe replacement: `echo "$(echo "$(date)")"`.

### CS4 - `eval` on text
Example: `eval "$cmd"`

Risk: Text executes with the shell's privileges and cannot be safely sanitized.

Decision gate: Prohibited.

Safe replacement:
```bash
cmd=(rsync -av --delete src/ dst/)
"${cmd[@]}"
```

### CS5 - `xargs` without NUL delimiters
Example: `find . -name '*.log' | xargs rm`

Risk: Spaces, quotes, and newlines split filenames.

Decision gate: Rewrite then confirm the exact previewed deletion set.

Safe replacement: Preview the exact root and expression with `find . -name '*.log' -print`; after complete target review and confirmation, run `find . -name '*.log' -print0 | xargs -0 rm --`. Any changed root, expression, or target set requires a new preview and confirmation.

### CS6 - Pipeline without `pipefail`
Example: `set -e; cmd1 | cmd2`

Risk: Failure in an earlier pipeline command is lost.

Decision gate: Inspect the selected interpreter, then rewrite.

Safe replacement for Bash or another verified `pipefail`-capable shell:
```bash
set -o pipefail
cmd1 | cmd2 | cmd3
```
For POSIX `sh`, do not emit `pipefail`; capture each component's status through an explicitly designed non-pipeline flow, or require a supporting interpreter and update the shebang.

## Heredocs and multi-line text

### HD1 - Indented heredoc terminator
Example: `cat <<EOF` with an indented closing `EOF`.

Risk: `<<EOF` requires a column-zero terminator and keeps reading input.

Decision gate: Rewrite.

Safe replacement:
```sh
cat <<-EOF
	line
	EOF
```
`<<-EOF` strips tabs, not spaces.

### HD2 - Unwanted heredoc expansion
Example: `cat <<EOF` when `$var` must be literal.

Risk: An unquoted terminator expands variables and substitutions.

Decision gate: Rewrite.

Safe replacement:
```sh
cat <<'EOF'
literal $var and $(cmd)
EOF
```

### HD3 - Heredoc redirected to a root-owned file
Example: `cat <<EOF > /etc/foo.conf`

Risk: The unprivileged shell performs the redirection.

Decision gate: Confirm privilege use.

Safe replacement:
```sh
sudo tee /etc/foo.conf >/dev/null <<'EOF'
content
EOF
```

### HD4 - `echo -e`
Example: `echo -e "a\nb"`

Risk: `-e` is non-portable.

Decision gate: Rewrite.

Safe replacement: `printf 'a\nb\n'`.

## Output and shell modes

### OR1 - Overwrite redirection
Example: `cmd > important.log`

Risk: Existing contents are replaced.

Decision gate: Confirm overwrite unless the file is verified disposable.

Safe replacement: `cmd >> log.txt`; otherwise inspect and confirm before `cmd > log.txt`.

### OR2 - Wrong stderr-redirection order
Example: `cmd 2>&1 > log`

Risk: stderr remains at the terminal.

Decision gate: Rewrite.

Safe replacement: `cmd > log 2>&1`.

### OR3 - Only stdout suppressed
Example: `cmd > /dev/null`

Risk: stderr remains visible, which may surprise the caller.

Decision gate: Inspect intent.

Safe replacement: `cmd > /dev/null 2>&1` only when both streams should be silenced.

### OR4 - `sudo` with a redirect
Example: `echo foo | sudo > /etc/file`

Risk: The current shell, not `sudo`, opens the file.

Decision gate: Confirm privilege use.

Safe replacement: `echo 'content' | sudo tee /etc/foo.conf > /dev/null`.

### SM1 - Script without strict mode
Example: A multi-step script without `set -euo pipefail`.

Risk: Later mutations can run after earlier failure, while blindly enabling strict mode can also change intended control flow or fail under an incompatible shell.

Decision gate: Inspect the selected interpreter and expected nonzero paths, then rewrite.

Safe replacement for a reviewed Bash script:
```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
```

For POSIX `sh`, use `set -eu` only after reviewing expected failures and handle pipeline component status explicitly; if `pipefail` is required, select a shell that supports it and update the shebang.

### SM2 - Unguarded `cd`
Example: `cd /tmp/build && rm -rf *`

Risk: A failed directory change can leave a destructive operation in the wrong directory.

Decision gate: Rewrite.

Safe replacement:
```sh
cd -- "$dir" || exit 1
rm -rf -- ./build
```

### SM3 - Bash constructs under `/bin/sh`
Example: `#!/bin/sh` with `[[ ... ]]`.

Risk: `/bin/sh` can be a shell without Bash extensions.

Decision gate: Rewrite.

Safe replacement:
```sh
#!/bin/sh
if [ -f "$file" ]; then ...; fi
```

### SM4 - `status` variable in zsh
Example: `status=$(curl ...)`.

Risk: `status` is read-only in zsh.

Decision gate: Rewrite.

Safe replacement: `exit_code=$(curl ...; printf '%s' "$?")`.

### SM5 - Bare `==` in zsh
Example: `echo ===`.

Risk: equals expansion changes bare `==` or `===`.

Decision gate: Rewrite.

Safe replacement:
```zsh
echo '==='
[[ "$a" == "$b" ]]
```

### SM6 - Persisted `IFS` mutation
Example: `IFS=,` followed by unrelated commands.

Risk: A sourced script or interactive shell retains the altered splitter.

Decision gate: Rewrite.

Safe replacement:
```bash
OLDIFS=$IFS
IFS=,
read -r a b c <<< "$line"
IFS=$OLDIFS
```

### SM7 - `set -x` with secrets in scope
Example: `set -x; auth_call --token=$TOKEN`.

Risk: Trace output exposes the resolved token.

Decision gate: Rewrite or block when argv is the only interface.

Safe replacement: Disable tracing before the secret enters scope and use a credential helper, protected file, stdin, or file descriptor; redirecting output does not hide argv.

## Secret and environment hygiene

### SE1 - Echoing a secret variable
Example: `echo $TOKEN`

Risk: The value enters output, history, and logs.

Decision gate: Prohibited.

Safe replacement:
```sh
if [ "${TOKEN+x}" = x ]; then printf 'TOKEN is set\n'; else printf 'TOKEN is not set\n'; fi
```

### SE2 - Environment dump to a file
Example: `env > env.txt`

Risk: Credentials may be persisted.

Decision gate: Refuse unless explicitly confirmed.

Safe replacement:
```sh
env | grep -E '^(PATH|HOME|SHELL|USER|PWD|LANG|LC_|TERM)=' > env.safe.txt
chmod 600 env.safe.txt
```

### SE3 - Secret in argv
Example: `curl --header "Authorization: Bearer abc123"`

Risk: Values are visible in history and process listings.

Decision gate: Rewrite.

Safe replacement: Use a credential helper or pre-provisioned protected file descriptor; when a file is necessary, keep it outside the repository, owner-readable only, and lifecycle-managed.

### SE4 - Authorization header in an interactive command
Example: `curl -H "Authorization: Bearer $TOKEN" https://api/...`

Risk: The command context and trace output can leak authentication.

Decision gate: Rewrite.

Safe replacement: Use the protected credential-file or helper pattern in SE3 without interpolating the secret into a displayed command.

### SE5 - Secret written into `.env`
Example: `echo "API_KEY=abc" >> .env`

Risk: Shell redirection can follow a link or race a checked path, and an already tracked file remains tracked despite `.gitignore`.

Decision gate: Block direct shell redirection of secret material.

Safe replacement: Use a credential helper or runtime secret store. When a file is unavoidable, create it outside repositories and synchronized paths through a platform API that atomically enforces no-follow, exclusive creation, owner-only permissions, and descriptor-bound writes; if that facility is unavailable, return `BLOCKED`. Never interpolate the secret into a displayed command.

### SE6 - Tracing around secret use
Example: `set -x; do_thing --token=$TOKEN`

Risk: Trace output prints the token.

Decision gate: Rewrite or block.

Safe replacement: Disable tracing before the secret enters scope; use a credential helper, protected file, stdin, or file descriptor.

### SE7 - Echoing secret-search results
Example: `grep -r PASSWORD . > findings.txt`

Risk: Raw matches persist secret values.

Decision gate: Rewrite.

Safe replacement: `rg -l 'PASSWORD|TOKEN|SECRET|PRIVATE[ _-]?KEY' .`; report locations only.

### SE8 - History expansion in double quotes
Example: `echo "wow!"`

Risk: Interactive Bash can expand prior history.

Decision gate: Rewrite.

Safe replacement: `set +H` before the double-quoted command, or use single quotes.

### SE9 - Reading a likely secret file to output
Example: `cat credentials`

Risk: Terminal, transcript, and log output can persist credentials even when the path itself is syntactically simple.

Decision gate: Inspect path identity and sensitivity without reading file contents; block when the file is sensitive or classification is uncertain.

Safe replacement: Report only non-secret metadata such as existence, owner, permissions, or an approved schema. Use an application-specific verifier when content validation is required; never display the secret value.

## Encoding and locale

### EN1 - CRLF shell script
Example: A script saved with CRLF.

Risk: `\r` corrupts commands and can break the shebang.

Decision gate: Rewrite.

Safe replacement: `dos2unix script.sh`, or resolve the platform before using its supported in-place-edit syntax.

### EN2 - UTF-8 BOM in a shell script
Example: An editor writes a BOM before `#!`.

Risk: Shebang parsing fails.

Decision gate: Rewrite.

Safe replacement: use a byte-aware editor or tool after resolving the platform; do not assume GNU/BSD `sed -i` or `\xHH` compatibility.

### EN3 - Byte-sensitive tools under an unspecified locale
Example: `sort file.txt`.

Risk: Locale collation changes cross-host output.

Decision gate: Rewrite.

Safe replacement:
```sh
LC_ALL=C sort file.txt
LC_ALL=C grep pattern file.txt
LC_ALL=C tr 'a-z' 'A-Z' < file.txt
```

### EN4 - `grep -P` portability
Example: `grep -P 'foo' file`.

Risk: BSD `grep` lacks PCRE support.

Decision gate: Rewrite.

Safe replacement: `grep -E 'foo' file` or `rg 'foo' file`.

### EN5 - Locale-dependent date
Example: `date +'%B %d'`.

Risk: Localized output changes scripts across hosts.

Decision gate: Rewrite.

Safe replacement: `LC_ALL=C date '+%B %d'` or `date -u '+%Y-%m-%dT%H:%M:%SZ'`.