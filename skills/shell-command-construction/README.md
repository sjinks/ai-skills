# shell-command-construction

> Use when constructing, repairing, or validating a concrete shell command, fragment, heredoc, redirection, or payload interface where literal text, argv boundaries, shell parsing, multiline data, or transport must be preserved.

This skill returns a construction result only. Execution safety, authorization, target validity, destructive-effect review, and permission to run are outside its scope and are not assessed.

It activates for a concrete shell target supplied by the caller or prepared from established task facts, including command construction within implementation or maintenance. Generic goals alone and mere command mentions do not activate. An incomplete concrete target blocks rather than guessing. The caller owns evidence gathering and any separately authorized execution; the skill returns one construction report.

It preserves confirmed token boundaries, literal-versus-expansion intent, operand order, transport, and payload data. SCC-Q1 keeps a multiline literal scalar in one argv word and explicitly covers `dash` and BusyBox `ash`. Bash history-sensitive quoting requires relevant mode/options when they affect literal preservation. The quoting reference also explains fixed-format `printf` payload delivery for a caller-confirmed transport. SCC-A1 distinguishes one-argument quoting from byte preservation: when exact output bytes matter, command substitution must preserve those bytes or block pending a confirmed alternative. SCC-M1 covers supplied stdin, file, heredoc, and Bash here-string transport, including leading-tab stripping, delimiter collisions, and appended-newline compatibility. The quoting reference distinguishes literal `%s` delivery from intentional `%b` escape interpretation and explains backslash-LF continuation. Downstream semantics are outside scope unless their token boundaries determine shell parsing.

All label sets use one ASCII framing space after each colon. Leading candidate whitespace and LF require multiline serialization; only LF separates report lines. Other control characters and Unicode separators remain literal candidate data. The five canonical fields, disposition values, authority literal, and construction-only boundary are unchanged.

Portability-only analysis does not activate this skill and belongs to a separate portability review. For mixed requests, SCC produces its five-field construction response first. Its `Construction next step` requires a separate portability review of the exact SCC candidate before any cross-target compatibility conclusion. Resolve a `BLOCKED` construction result before that review. SCC does not construct a portability candidate or make a compatibility claim. The five canonical labels are the default; explicit caller-requested replacement labels apply only to a direct response and are not a later-review handoff.

## Files

- [`SKILL.md`](SKILL.md) — activation, workflow, output contract, and completion rules.
- [`references/construction-rules.md`](references/construction-rules.md) — canonical construction decisions.
- [`references/quoting-rules.md`](references/quoting-rules.md) — explanatory shell semantics, source map, and scope provenance.
- [`references/response-examples.md`](references/response-examples.md) — optional caller-label eligibility and complete construction reports.
