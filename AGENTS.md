## Running model evals (cost control)

- NEVER run `waza run` (or any command that issues live model/API calls) without explicit per-run approval from the user. A full eval suite costs roughly 200-270 premium Copilot requests; even a single `--task ... --trials 1` probe costs about 9-18. Before running, state the expected scope and cost, prefer the smallest scope that answers the question, and do not re-run to "confirm" a result that existing measurements already establish.
- `waza check`, schema validation, `cmp`, `git`, `gh`, and file reads/searches are free and do not need approval.

When creating or materially updating skills:

- When creating a new skill, use cross-model-instruction-authoring to keep the instruction portable across target models.
- A material update changes triggers, workflow, decision rules, output contracts, behavior-affecting references, or eval contracts.
- Before considering a new skill or material update complete, perform a direct projection sweep across its rules, outputs, references, and evals. If that sweep finds a mismatch, run `equivalence-class-audit` with the mismatch as its triggering finding and an explicit scope. Then run `instruction-quality-audit`, `adversarial-review`, and `agent-skill-audit`.
- Use each review's own materiality and verdict rules. A finding is resolved only after every applicable native remediation requirement (`Correction:`, `Suggested fix:`, blocking mitigation, or acceptance criterion) is satisfied and verified, or, when the review permits acceptance, the user or a named accountable human owner explicitly accepts the finding ID, rationale, and residual risk. No agent may grant that acceptance.
- Bind each projection sweep and review result to the exact tree or diff it inspected. Any later change within that scope invalidates the result. Completion requires the same unchanged final tree to have: projection outcome `PASS`; `instruction-quality-audit` verdict `No material defects`; `adversarial-review` verdict `CLEAN`, or `CONCERNS` only when every remaining item is explicitly accepted by the user or a named accountable human owner under that review's rules; and `agent-skill-audit` verdict `Ready` or `Ready with limitations`. All other outcomes block completion. Repeat the full set after any in-scope fix; if a required review is unavailable, report the skill change blocked.
- Do not put volatile numeric eval-task totals in PR descriptions; say `all task files`. If a required template demands a count, derive it from the final tree and verify the candidate body before opening the PR. If the final push occurs after publication, verify and update the published body after that push.
- Use subagents for those reviews to keep the main context window clean.
- Optimize for token efficiency: keep instructions concise, remove duplication, and prefer reusable shared rules over repeated local text.
- Ignore Waza frontmatter complaints and hard limits on instruction size; prioritize concise, useful skill guidance over satisfying those checks.
- When guidance conflicts, prefer concise instructions that weaker models can follow reliably.
- Make instructions clear enough for weaker models such as GPT-5.4 mini and Claude Haiku 4.6: prefer explicit ordering, simple conditionals, stable terminology, and reproducible output formats.
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
