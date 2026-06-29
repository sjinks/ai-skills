## Running model evals (cost control)

- NEVER run `waza run` (or any command that issues live model/API calls) without explicit per-run approval from the user. A full eval suite costs roughly 200-270 premium Copilot requests; even a single `--task ... --trials 1` probe costs about 9-18. Before running, state the expected scope and cost, prefer the smallest scope that answers the question, and do not re-run to "confirm" a result that existing measurements already establish.
- `waza check`, schema validation, `cmp`, `git`, `gh`, and file reads/searches are free and do not need approval.

When creating or updating skills:

- Optimize for token efficiency: keep instructions concise, remove duplication, and prefer reusable shared rules over repeated local text.
- Ignore Waza frontmatter complaints and hard limits on instruction size; prioritize concise, useful skill guidance over satisfying those checks.
- When guidance conflicts, prefer concise instructions that weaker models can follow reliably.
- Make instructions clear enough for weaker models such as GPT 5 mini and Haiku 4.5: prefer explicit ordering, simple conditionals, stable terminology, and reproducible output formats.
- Check consistency: remove contradictions, incompatible constraints, and unstable priority ordering.
- Check cohesion: ensure sections support the same task without duplication or distracting scope creep.
- Check coherence: keep workflows, terms, and expected behavior understandable and logically ordered.
- Check completeness: cover input handling, edge cases, output requirements, and the target artifact scope.
- Check suitability for weaker models: evaluate instruction length, nesting depth, overloaded conditionals, ambiguous or conflicting priorities, missing examples, and whether the expected output format is easy to reproduce.
- Check contradiction risks: identify instructions that directly conflict with each other.
- Check ambiguity risks: identify vague or underspecified instructions that a model could interpret in multiple ways.
- Check persona consistency: identify places where the expected tone, personality, or role contradicts itself.
- Check cognitive load: simplify deeply nested conditions, too many competing priorities, and unclear precedence.
- Check semantic coverage: add guidance for scenarios or edge cases where the model would otherwise have to guess.
- For skill/eval contract changes, align skill wording and eval assertions before finalizing: confirm canonical output labels and exact spelling; representative selection rules such as first supplied item; provenance shape such as full source set vs additional sources only; consistency across skill wording, eval regexes, and negative assertions; and sibling skills/evals with the same contract pattern.
