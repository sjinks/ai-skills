# shell-command-construction

> Use when constructing, repairing, or validating a concrete shell command, fragment, heredoc, redirection, or command-producing request where literal text, argv boundaries, shell parsing, multiline data, or transport must be preserved.

This skill returns a construction result only. Execution safety, authorization, target validity, destructive-effect review, and permission to run are outside its scope and are not assessed.

It helps an assistant preserve confirmed shell token and quote boundaries, literal-versus-expansion intent, operand order, input transport, and multiline payloads. SCC-Q1 keeps even a multiline scalar in one argv word; SCC-M1 covers only supplied stdin, file, and heredoc payload transport. It blocks rather than guessing a shell, a shell boundary that affects construction, scalar/list intent, glob binding, empty/unset behavior, or secret-safe transport. Exact supplied literal argument text does not require validating downstream semantics; downstream grammar is required only when its token boundaries affect shell parsing. Positive and negative downstream syntax or semantic judgments are not assessed.

Portability-only analysis does not activate this skill and belongs to a separate portability review. For mixed requests, SCC produces its five-field construction response first. Its `Next step` requires a separate portability review of the exact SCC candidate before any cross-target compatibility conclusion. Resolve a `BLOCKED` construction result before that review. SCC does not construct a portability candidate or make a compatibility claim.

## Evidence status

Static checks validate artifact structure and deterministic graders; they do not prove behavior for any model. GPT-5.4 mini and Claude Haiku 4.5 are compatibility-floor evaluation goals, not proven outcomes. Model evidence is specific to the model, runtime, and settings used, and every live run remains explicitly approval-gated.

## Files

- [`SKILL.md`](SKILL.md) — activation, workflow, output contract, and completion rules.
- [`references/construction-rules.md`](references/construction-rules.md) — canonical construction decisions.
- [`references/quoting-rules.md`](references/quoting-rules.md) — explanatory shell semantics.
- [`references/source-map.md`](references/source-map.md) — provenance and scope boundaries.
