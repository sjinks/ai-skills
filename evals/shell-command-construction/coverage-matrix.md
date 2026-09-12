# shell-command-construction coverage matrix

This matrix maps each synthetic fixture to its discriminating construction behavior. Original planning traces that required execution-safety handling are superseded by the user override: SCC assesses no execution concerns and always uses `Execution authority: NOT ASSESSED BY THIS SKILL`.

The SCC suite contains 44 fixtures. The user explicitly approved its expansion from 43 to 44 fixtures on 2026-09-12: `I approve`. The separate shell-portability suite contains 38 fixtures: its 37-fixture matrix was explicitly approved by the user on 2026-09-12, and `positive-edge-030` was added to remediate the blank-delimited-handoff review finding.

| Fixture | SCC-TC | Source trace | Behavioral discriminator | Trigger | Result/exclusion | Authority or handoff | Deterministic focus | Substance |
|---|---|---|---|---|---|---|---|---|
| positive-trigger-001 | 4 | AC-1, EDGE-1/2 | Literal multiline one-argv scalar with repeated apostrophes, double quotes, backslashes, shell metacharacters, textual escape forms, and authority-looking literal words | yes | REWRITE | not assessed | exact one-word POSIX-like single-quote composition using `'"'"'` per apostrophe; assessment identifies the literal multiline scalar; next step remains construction-relevant; the embedded newline remains in the one argv scalar, and textual `\0`, `\x00`, and `\u0000` remain literal data rather than U+0000 NUL | yes |
| positive-trigger-002 | 9 | AC-5, EDGE-11 | Confirmed in-shell pathname expansion | yes | VALID | not assessed | exact unquoted `/tmp/scc-fixture/*.log`; no literalization, scope change, external rediscovery, or invented results | no |
| positive-edge-003 | 5 | AC-2, EDGE-4 | Leading-dash operand | yes | REWRITE | not assessed | option termination and operand position; prompt requires POSIX single-quote representation; next step is construction-relevant | no |
| positive-edge-004 | 5 | AC-2, EDGE-3/9 | Already-bound glob-derived Bash argv with a confirmed empty third operand | yes | REWRITE | not assessed | exact ordered file operands plus empty third argv entry; array boundaries; no wildcard rediscovery | yes |
| positive-edge-005 | 5 | AC-2, EDGE-5 | Confirmed one-argument parameter expansion with downstream semantics intentionally unrequested | yes | REWRITE | not assessed | SCC-A1 quotes the confirmed scalar expansion as `"$query"`; representative positive and negative downstream semantic judgments rejected | no |
| positive-edge-006 | 6 | AC-1, EDGE-7 | Literal multiline heredoc with terminal newline and no caller-fixed delimiter | yes | REWRITE | not assessed | select collision-free `SCC_BODY`; preserve terminal newline, removable two-space prefix, payload indentation, and empty line | yes |
| positive-edge-007 | 6 | AC-2, EDGE-6 | Reversed JSON stdin plus stdout/stderr routing | yes | REWRITE | not assessed | stdin retained; repair `2>&1 > result.json` to `> result.json 2>&1`; positive and negative downstream JSON semantic judgments rejected | no |
| positive-edge-008 | 6 | AC-2, EDGE-8 | Proposed heredoc for a byte-exact payload without terminal newline, with supplied byte-preserving file interface | yes | REWRITE | not assessed | replace the heredoc-incompatible branch with the exact supplied file transport | no |
| positive-edge-009 | 7 | AC-3, EDGE-3 | Unknown scalar/list | yes | BLOCKED | not assessed | assessment and next step each distinguish scalar/one value from multiple/list/argv intent; no candidate | no |
| positive-edge-010 | 7 | AC-3, EDGE-2 | Unknown literal/expansion | yes | BLOCKED | not assessed | assessment and next step each state literal and expansion intent; no candidate | no |
| positive-edge-011 | 7 | AC-3 | Byte-exact alpha + U+0000 NUL + beta payload where only argv or heredoc are available | yes | BLOCKED | not assessed | one representability defect covers argv and heredoc; exact non-argv NUL-capable transport/interface request | no |
| positive-edge-012 | 7 | AC-3, EDGE-9 | Empty versus unset behavior only | yes | BLOCKED | not assessed | assessment and next step require the unset/empty decision: reject or pass one empty argument | no |
| positive-edge-013 | 8 | AC-4, EDGE-10 | Supplied non-secret transport | yes | VALID | not assessed | supplied non-secret transport abstraction retained; no stale sentinel assertion | no |
| positive-edge-014 | 8 | AC-4, EDGE-10 | Synthetic secret supplied as an agent-readable evaluator resource; no confirmed target-tool source/transport | yes | BLOCKED | not assessed | raw, boundary-terminated `SCC_TEST_SE`/`ENDER_7c4f` fragments and distinctive normalized secret windows, Base64, URL-encoded, and hex sentinel forms absent from the response; generic non-secret source/transport request | no |
| positive-edge-015 | 9 | AC-5, EDGE-11 | Remote transport facts absent | yes | BLOCKED | not assessed | asks first for remote parser; transport contract remains a later required fact | no |
| positive-edge-016 | 10 | AC-3, EDGE-9 | Unbound external glob result set | yes | BLOCKED | not assessed | exact ordered operands required; no wildcard retention, rediscovery, or invented matches | no |
| positive-edge-017 | 11 | AC-7 | Mixed construction/portability with neutral domain wording | yes | REWRITE | separate portability review required | assessment identifies the `tool run` label boundary; next step hands only the exact candidate to a separate portability review; neutral `run`, deployment, and release words accepted; representative active, passive, and bare standalone authority/safety claims rejected | no |
| positive-edge-018 | 6 | AC-2, EDGE-4 | Fixed heredoc delimiter collides with literal payload line | yes | BLOCKED | not assessed | exact `EOF` body line collides with the caller-required delimiter; no alternate delimiter or transport is invented | no |
| positive-edge-019 | 9 | AC-3, EDGE-3 | Confirmed remote JSON argv transport constructed from intent | yes | REWRITE | not assessed | exact stdin JSON-array candidate; remote JSON parser, one-to-one argv mapping, and no shell reparsing preserve two remote argv entries | no |
| positive-edge-020 | 9 | AC-3, EDGE-3 | Confirmed local Bash and remote POSIX sh parsers plus two remote argv entries, but no boundary-preserving transport/serialization contract | yes | BLOCKED | not assessed | assessment identifies the remote parser, argv boundaries, and missing transport/serialization contract; next step requests only that contract, not a parser | no |
| positive-edge-021 | 4 | AC-1, EDGE-1 | Already-correct direct literal scalar without interpreter-specific syntax | yes | VALID | not assessed | preserve exact supplied `tool "hello world"` representation as one argv entry without blocking on an unspecified interpreter when no shell-specific syntax choice is needed; SCC-Q1 does not rewrite an already-correct representation to single quotes | no |
| positive-edge-022 | 9 | AC-2, EDGE-6 | Multiline commit message | yes | REWRITE | not assessed | `-F` file transport | yes |
| positive-edge-023 | 7 | AC-3, EDGE-6 | Leading whitespace plus a bare pipe with no downstream command | yes | BLOCKED | not assessed | no malformed one-line `Construction candidate:  | `; request the missing command text after the pipe | no |
| positive-edge-024 | 7 | AC-3, EDGE-6 | Proposed stdout/stderr redirection with unspecified stderr routing intent | yes | BLOCKED | not assessed | no guessed redirection order; request whether stderr joins stdout, retains its original destination, or uses a separate destination | no |
| positive-edge-025 | 7 | AC-3 | Bash-array argv syntax request with an unspecified local interpreter | yes | BLOCKED | not assessed | no guessed interpreter-specific array/argv syntax; request only whether the local shell is Bash or POSIX sh | no |
| positive-edge-026 | 8 | AC-4, EDGE-6 | One-line pipeline fragment beginning with `|` and downstream command text on the same line | yes | VALID | not assessed | preserves the exact supplied `| sed -n '1p'` candidate as VALID; does not collapse it into malformed bare-pipe multiline marker | no |
| positive-edge-027 | 8 | AC-4, EDGE-6 | Confirmed one-argument command substitution | yes | VALID | not assessed | preserves exact supplied `tool "$(date)"` candidate with confirmed intentional command substitution and one-argument boundary under SCC-A1 | no |
| positive-edge-028 | 8 | AC-4, EDGE-6 | Supplied one-line candidate text equals reserved placeholder `Not provided` | yes | VALID | not assessed | preserves exact literal payload by canonical multiline `Construction candidate: |` serialization; does not collapse into BLOCKED inline placeholder | no |
| positive-edge-029 | 4 | AC-7 | Caller-requested replacement labels for a direct response | yes | VALID | not assessed | follows the requested five labels and preserves their ordered construction semantics; does not emit a canonical handoff | no |
| positive-edge-030 | 4 | AC-3, AC-7 | Caller-requested labels with an unknown scalar/list boundary | yes | BLOCKED | not assessed | custom candidate label retains `Not provided`; assessment and next step request the scalar/list decision | no |
| positive-edge-031 | 4 | AC-1, AC-7 | A second caller-requested valid label set with a literal multiline scalar | yes | VALID | not assessed | position-mapped custom labels retain two-space multiline serialization and exact literal payload | no |
| positive-edge-032 | 4 | AC-7 | Caller-requested label containing a colon | yes | VALID | not assessed | falls back to canonical labels rather than emitting an unsafe field separator | no |
| positive-edge-033 | 4 | AC-7 | Caller-requested case-insensitively duplicate labels | yes | VALID | not assessed | falls back to canonical labels rather than emitting ambiguous duplicate fields | no |
| positive-edge-034 | 4 | AC-1 | Literal multiline candidate with terminal newline | yes | VALID | not assessed | emits a final two-space-only payload line before the authority framing line | no |
| positive-edge-035 | 4 | AC-7 | Caller-requested canonical-colliding label | yes | VALID | not assessed | falls back to canonical labels rather than emitting a label reserved by the canonical envelope | no |
| negative-trigger-001 | 12 | AC-7 | Non-shell TypeScript implementation task | no | exclusion | n/a | all markers absent | no |
| negative-trigger-002 | 12 | AC-7 | Non-shell task | no | exclusion | n/a | all markers absent | no |
| negative-close-001 | 11 | AC-7 | Portability-only review | no | exclusion | portability-only exclusion | all SCC markers absent | no |
| negative-close-002 | 12 | AC-7 | Prose-only drafting | no | exclusion | n/a | all markers absent | no |
| negative-close-003 | 12 | AC-7 | Concrete command with execution-safety/authorization-only request | no | exclusion | n/a | all construction markers absent | no |
| negative-close-004 | 12 | AC-7 | Generic shell goal with no command, executable, path, syntax, or payload interface | no | exclusion | n/a | all construction markers absent | no |
| negative-close-005 | 11 | AC-7 | GitHub CLI body/field/stdin repair owned by the dedicated GitHub CLI workflow | no | exclusion | GitHub CLI ownership | all SCC markers absent; gh-specific workflow remains eligible | no |
| negative-close-006 | 12 | AC-7 | General shell grammar defect outside the canonical construction catalog | no | exclusion | n/a | all construction markers absent | no |
| negative-close-007 | 12 | AC-7 | Generic shell-quoting tutoring | no | exclusion | n/a | all construction markers absent | no |

## Portability malformed-handoff additions

| Fixture | Invalid branch | Expected behavior |
|---|---|---|
| positive-edge-015 | Missing `Construction assessment` | Reduced `BLOCK`; request a complete corrected SCC result; no portability conclusion |
| positive-edge-016 | Reordered `Construction candidate` and `Construction assessment` | Reduced `BLOCK`; request ordered SCC fields; no portability conclusion |
| positive-edge-017 | Duplicate `Construction candidate` field | Reduced `BLOCK`; request one complete SCC result; no portability conclusion |
| positive-edge-018 | Blank `Construction next step` | Reduced `BLOCK`; request a nonblank complete SCC result; no portability conclusion |
| positive-edge-019 | Prefixed field-looking payload lines in multiline candidate | Decode as payload; stop only at unprefixed authority terminator; review decoded candidate only |
| positive-edge-020 | Adjacent extra field after `Construction next step` | Reduced `BLOCK`; request exactly five ordered SCC fields and blank-line-separated surrounding prose; no portability conclusion |
| positive-edge-030 | Blank-delimited non-field prose after a complete handoff | Normal review of the exact decoded candidate; no construction rewrite or reduced `BLOCK` |
| positive-edge-021 | Two individually complete construction results separated by a blank line | Reduced `BLOCK`; request exactly one complete SCC result; no portability conclusion |
| positive-edge-022 | Altered `Execution authority` value | Reduced `BLOCK`; request corrected authority literal in a complete SCC result; no portability conclusion |
| positive-edge-023 | Multiline payload containing `Not provided` for `VALID`/`REWRITE` | Decode as literal candidate payload; perform normal portability review; no malformed-handoff block |
| positive-edge-026 | Leading `Construction assessment` before `Construction result` | Reduced `BLOCK`; request one corrected complete SCC result; no portability conclusion |
| positive-edge-028 | Custom-labeled direct construction response | Reduced `BLOCK`; request canonical handoff fields or separately supplied direct code; no portability conclusion |
| positive-edge-029 | Terminal two-space-only multiline payload line after a standalone trailing backslash | Decode as the candidate's terminal newline, completing the POSIX line continuation; normal `CLEAN` review; dropped newline makes dash treat the backslash as a command |
| positive-edge-003 | One-line handoff candidate beginning with `|` and later text on the same line | Decode as the exact one-line fragment `| sed -n '1p'`, not as a multiline marker; perform the normal portability review |

## Portability target-specific utility additions

| Fixture | Target branch | Expected behavior |
|---|---|---|
| positive-edge-024 | Confirmed native FreeBSD 14 `readlink -f` semantics | Preserve native command; `CLEAN`; no `realpath` rewrite |
| positive-edge-025 | FreeBSD 14 `readlink -m` with missing-component requirement | `BLOCK`; do not infer `-m` support from native `-f` |
| positive-edge-027 | Confirmed native macOS 12.3 `readlink -f` semantics | Preserve native command; `CLEAN`; no `realpath` rewrite |

## Portability routing additions

| Fixture | Boundary | Expected behavior |
|---|---|---|
| negative-close-006 | Cross-target Python portability question | Exclude shell-portability output while retaining close-domain routing coverage |

All fixture data is synthetic. The disclosure sentinel appears only in an agent-readable evaluator fixture resource and a forbidden-output assertion, never in the prompt; the target tool has no confirmed interface for that resource. Other secret fixtures use non-secret transport names. Positive serializers permit zero or one terminal newline after a nonblank `Construction next step`, but reject extra blank lines or trailing prose. The global output contract rejects positive and negative downstream semantic judgments in the assessment and next-step fields while allowing boundary-only construction statements. Separate RE2-compatible semantic assertions cover representative required construction concepts per fixture; assertion 3 intentionally retains finite structural coverage for field order, result, candidate, and authority rather than exhaustive synonym matching. SCC-Q1 keeps a multiline scalar as one argv word; SCC-M1 exclusively covers supplied stdin, file, and heredoc payload transport. Superseded planning traces that assigned safety, execution, or cross-target authority to SCC do not describe these fixtures; SCC uses only its construction contract.
