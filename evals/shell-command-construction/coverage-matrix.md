# shell-command-construction coverage matrix

This matrix maps each synthetic fixture to its discriminating construction behavior. Original planning traces that required execution-safety handling are superseded by the user override: SCC assesses no execution concerns and always uses `Execution authority: NOT ASSESSED BY THIS SKILL`.

| Fixture | SCC-TC | Source trace | Behavioral discriminator | Trigger | Result/exclusion | Authority or handoff | Deterministic focus | Substance |
|---|---|---|---|---|---|---|---|---|
| positive-trigger-001 | 4 | AC-1, EDGE-1/2 | Literal scalar with repeated apostrophes, double quotes, backslashes, backticks, and shell metacharacters | yes | REWRITE | not assessed | exact one-word POSIX-like single-quote composition using `'"'"'` per apostrophe | yes |
| positive-trigger-002 | 9 | AC-5, EDGE-11 | Confirmed in-shell pathname expansion | yes | VALID | not assessed | exact unquoted `/tmp/scc-fixture/*.log`; no literalization, scope change, external rediscovery, or invented results | no |
| positive-edge-003 | 5 | AC-2, EDGE-4 | Leading-dash operand | yes | REWRITE | not assessed | operand position | no |
| positive-edge-004 | 5 | AC-2, EDGE-3/9 | Already-bound glob-derived Bash argv | yes | REWRITE | not assessed | exact operands/order; array boundaries; no wildcard rediscovery | yes |
| positive-edge-005 | 5 | AC-2, EDGE-5 | Confirmed set scalar that may be empty | yes | REWRITE | not assessed | one quoted argument; empty remains one argument | no |
| positive-edge-006 | 6 | AC-1, EDGE-7 | Literal multiline heredoc | yes | REWRITE | not assessed | exact `<<'EOF'` body; removable two-space prefix; payload indentation and empty line | yes |
| positive-edge-007 | 6 | AC-2, EDGE-6 | JSON stdin plus stdout/stderr routing | yes | VALID | not assessed | stdin retained; `> result.json 2>&1` order preserved | no |
| positive-edge-008 | 6 | AC-2, EDGE-8 | Supplied file interface | yes | VALID | not assessed | file transport retained | no |
| positive-edge-009 | 7 | AC-3, EDGE-3 | Unknown scalar/list | yes | BLOCKED | not assessed | no candidate | no |
| positive-edge-010 | 7 | AC-3, EDGE-2 | Unknown literal/expansion | yes | BLOCKED | not assessed | smallest fact | no |
| positive-edge-011 | 7 | AC-3 | Unknown downstream grammar only | yes | BLOCKED | not assessed | asks only for downstream grammar; quote boundary supplied | no |
| positive-edge-012 | 7 | AC-3, EDGE-9 | Empty versus unset behavior only | yes | BLOCKED | not assessed | asks only whether unset is rejected or passed as one empty argument | no |
| positive-edge-013 | 8 | AC-4, EDGE-10 | Supplied non-secret transport | yes | VALID | not assessed | source expression retained | no |
| positive-edge-014 | 8 | AC-4, EDGE-10 | Missing secret transport | yes | BLOCKED | not assessed | representative raw, fragment, explicit lowercase, Base64, URL-encoded, hex, reversed, escaped, and split sentinel forms absent; generic source request | no |
| positive-edge-015 | 9 | AC-5, EDGE-11 | Remote transport facts absent | yes | BLOCKED | not assessed | asks first for remote parser; transport contract remains a later required fact | no |
| positive-edge-016 | 10 | AC-3, EDGE-9 | Unbound external glob result set | yes | BLOCKED | not assessed | exact ordered operands required; no wildcard retention, rediscovery, or invented matches | no |
| positive-edge-017 | 11 | AC-7 | Mixed construction/portability | yes | REWRITE | `shell-portability` review required | exact candidate must be reviewed by the named owner before any compatibility claim | no |
| positive-substance-001 | 9 | AC-2, EDGE-6 | Multiline commit message | yes | REWRITE | not assessed | `-F` file transport | yes |
| negative-trigger-001 | 12 | AC-7 | Generic tutoring | no | exclusion | n/a | all markers absent | no |
| negative-trigger-002 | 12 | AC-7 | Non-shell task | no | exclusion | n/a | all markers absent | no |
| negative-close-001 | 11 | AC-7 | Portability-only review | no | exclusion | `shell-portability` | named owner present; all SCC markers absent | no |
| negative-close-002 | 12 | AC-7 | Prose-only drafting | no | exclusion | n/a | all markers absent | no |
| negative-close-003 | 12 | AC-3/7 | Underspecified bypass framing | no | exclusion | n/a | all markers absent | no |

All fixture data is synthetic. `SCC_TEST_SECRET_DO_NOT_RENDER_7c4f` appears only in a prompt and representative forbidden-output assertions; these variants are adversarial coverage, not an exhaustive DLP claim. Superseded planning traces that assigned safety, execution, or cross-target authority to SCC do not describe these fixtures; SCC uses only its construction contract.
